import logging
import random
from zACK.enums import SearchLocation
from zACK.instructions import hacker_news
from zACK.helpers import (
    HackerNewsRateLimitError,
    get_hacker_news_client,
    build_hacker_news_post_evaluation,
    build_hacker_news_response_evaluation,
    build_hacker_news_oai_instruction,
    run_evaluation,
    run_reword,
    search_twitter,
)
from campaigns.models import Campaign
from campaigns.utils import update_campaign_run_status
from leads.models import Lead
from leads.helpers import CampaignLeadSearchResult
from django.conf import settings
from django.db import transaction
from dataclasses import asdict

DEFAULT_SCORE = 0
LEADS_BATCH_SIZE_LIMIT = 100
PROMPT_TEMPLATES_LIMIT = 100
APPROX_SECONDS_PER_HIT = 15

logger = logging.getLogger(__name__)


# https://platform.openai.com/playground for testing
def find_leads(
    campaign: Campaign,
    limit=settings.SEARCH_LIMIT,
):
    if not campaign:
        logger.warning(f"find_leads called with no Campaign.")
        return

    update_campaign_run_status(campaign, "Task started")

    search_results = []
    # Currently only handle Hacker News location
    if SearchLocation.HACKER_NEWS in campaign.locations:
        results = generate_hacker_news_leads(campaign, limit)
        search_results.extend(results)
    if SearchLocation.TWITTER in campaign.locations:
        results = generate_twitter_leads(campaign, limit)
        search_results.extend(results)

    update_campaign_run_status(campaign, "Saving leads")

    # Create Leads in DB
    lead_fields = [field.name for field in Lead._meta.get_fields()]
    processed_results = [
        {
            key: value
            for key, value in asdict(res).items()
            if key in lead_fields
        }
        for res in search_results
    ]
    num_batches = (
        len(processed_results) + LEADS_BATCH_SIZE_LIMIT - 1
    ) // LEADS_BATCH_SIZE_LIMIT

    # Use transaction.atomic() to ensure atomicity of bulk_create
    with transaction.atomic():
        for batch_number in range(num_batches):
            start_index = batch_number * LEADS_BATCH_SIZE_LIMIT
            end_index = start_index + LEADS_BATCH_SIZE_LIMIT
            batch = processed_results[start_index:end_index]
            Lead.objects.bulk_create([Lead(**item) for item in batch])

    update_campaign_run_status(campaign, f"Finished with {len(search_results)} results.")


def generate_hacker_news_leads(
    campaign: Campaign,
    limit=settings.SEARCH_LIMIT,
):
    client = get_hacker_news_client()

    try:
        response = client.search_hacker_news(campaign.search_terms)

        assert (
            response.status_code == 200
        ), f"Invalid Hacker News response code {response.status_code}."

        response_hits = response.json()["hits"][:limit]
        
        hits = client.get_hacker_news_context(response_hits)
        update_campaign_run_status(
            campaign, f"Parsing {len(response_hits)} Hacker News results."
        )
        search_results = []
        prompt_templates = campaign.prompt_templates.order_by("?")[
            :PROMPT_TEMPLATES_LIMIT
        ]

        for index, (
            username,
            comment,
            comment_url,
            profile_about,
            profile_url,
        ) in enumerate(hits, start=1):
            search_result = CampaignLeadSearchResult(
                campaign=campaign,
                location=SearchLocation.HACKER_NEWS,
                username=username,
                profile_about=profile_about,
                profile_url=profile_url,
                comment=comment,
                comment_url=comment_url,
            )

            # Step 1. Evaluate user's initial post
            # if `post_evaluation_prompt` defined on Campaign
            if campaign.post_evaluation_prompt:
                evaluation_instruction = build_hacker_news_post_evaluation(
                    template=campaign.post_evaluation_prompt,
                    prompt=comment,
                )

                search_result.post_evaluate_request_text = (
                    evaluation_instruction
                )

                evaluation_response = run_evaluation(evaluation_instruction)
                assert evaluation_response is not None

                search_result.post_evaluate_response_text = evaluation_response

                # Assume response has score in first word delimited by . or space
                # TODO: Refactor this logic into its own helper method
                words = evaluation_response.split(". ")
                score = None
                try:
                    score = int(words[0])
                    score = min(max(score, 1), 100)
                except (ValueError, AssertionError) as error:
                    logger.debug(
                        f"Issue with GPT response {evaluation_response} while"
                        " generating score."
                    )

                score = score or DEFAULT_SCORE
                search_result.post_score = score

            # Get a random Prompt Template to generate a response from
            prompt_template = random.choice(prompt_templates)
            prompt_instruction = build_hacker_news_oai_instruction(
                prompt_template=prompt_template,
                comment=comment,
                profile_about=profile_about,
                username=username,
            )
            search_result.prompt_template = prompt_template.template
            search_result.prompt_request_text = prompt_instruction

            # Step 2. Generate response from Prompt Template
            prompt_response_text = run_reword(prompt_instruction)
            assert prompt_response_text is not None
            search_result.prompt_response_text = prompt_response_text

            # Step 3. Evaluate the generated response
            # if `response_evaluation_prompt` defined on Campaign
            if campaign.response_evaluation_prompt:
                evaluation_instruction = build_hacker_news_response_evaluation(
                    template=campaign.response_evaluation_prompt,
                    prompt=prompt_response_text,
                )

                search_result.evaluate_request_text = evaluation_instruction

                evaluation_response = run_evaluation(evaluation_instruction)
                assert evaluation_response is not None

                search_result.evaluate_response_text = evaluation_response

                # Assume response has score in first word delimited by . or space
                words = evaluation_response.split(". ")
                score = None
                try:
                    score = int(words[0])
                    score = min(max(score, 1), 100)
                except (ValueError, AssertionError) as error:
                    logger.debug(
                        f"Issue with GPT response {evaluation_response} while"
                        " generating score."
                    )

                score = score or DEFAULT_SCORE
                search_result.score = score

            search_results.append(search_result)

        return search_results

    except HackerNewsRateLimitError:
        update_campaign_run_status(
            campaign, "Exception: HackerNewsRateLimitError"
        )
        raise
    except Exception as error:
        update_campaign_run_status(campaign, f"Exception: {repr(error)}")
        raise


def generate_twitter_leads(
    campaign: Campaign,
    limit=settings.SEARCH_LIMIT,
):
    try:
        response = search_twitter(campaign.search_terms)

        assert (
            response.status_code == 200
        ), f"Invalid Twitter response code {response.status_code}."

        response_hits = response.json()["statuses"][:limit]
        
        update_campaign_run_status(
            campaign, f"Parsing {len(response_hits)} Twitter results."
        )
        search_results = []
        prompt_templates = campaign.prompt_templates.order_by("?")[
            :PROMPT_TEMPLATES_LIMIT
        ]

        for index, tweet in enumerate(response_hits, start=1):
            username = tweet["user"]["screen_name"]
            comment = tweet["text"]
            profile_about = tweet["user"]["description"]
            profile_url = f"https://twitter.com/{username}"
            comment_url = f"https://twitter.com/{username}/status/{tweet['id_str']}"

            search_result = CampaignLeadSearchResult(
                campaign=campaign,
                location=SearchLocation.TWITTER,
                username=username,
                profile_about=profile_about,
                profile_url=profile_url,
                comment=comment,
                comment_url=comment_url,
            )

            # Step 1. Evaluate user's initial post
            # if `post_evaluation_prompt` defined on Campaign
            if campaign.post_evaluation_prompt:
                evaluation_instruction = build_hacker_news_post_evaluation(
                    template=campaign.post_evaluation_prompt,
                    prompt=comment,
                )

                search_result.post_evaluate_request_text = (
                    evaluation_instruction
                )

                evaluation_response = run_evaluation(evaluation_instruction)
                assert evaluation_response is not None

                search_result.post_evaluate_response_text = evaluation_response

                # Assume response has score in first word delimited by . or space
                # TODO: Refactor this logic into its own helper method
                words = evaluation_response.split(". ")
                score = None
                try:
                    score = int(words[0])
                    score = min(max(score, 1), 100)
                except (ValueError, AssertionError) as error:
                    logger.debug(
                        f"Issue with GPT response {evaluation_response} while"
                        " generating score."
                    )

                score = score or DEFAULT_SCORE
                search_result.post_score = score

            # Get a random Prompt Template to generate a response from
            prompt_template = random.choice(prompt_templates)
            prompt_instruction = build_hacker_news_oai_instruction(
                prompt_template=prompt_template,
                comment=comment,
                profile_about=profile_about,
                username=username,
            )
            search_result.prompt_template = prompt_template.template
            search_result.prompt_request_text = prompt_instruction

            # Step 2. Generate response from Prompt Template
            prompt_response_text = run_reword(prompt_instruction)
            assert prompt_response_text is not None
            search_result.prompt_response_text = prompt_response_text

            # Step 3. Evaluate the generated response
            # if `response_evaluation_prompt` defined on Campaign
            if campaign.response_evaluation_prompt:
                evaluation_instruction = build_hacker_news_response_evaluation(
                    template=campaign.response_evaluation_prompt,
                    prompt=prompt_response_text,
                )

                search_result.evaluate_request_text = evaluation_instruction

                evaluation_response = run_evaluation(evaluation_instruction)
                assert evaluation_response is not None

                search_result.evaluate_response_text = evaluation_response

                # Assume response has score in first word delimited by . or space
                words = evaluation_response.split(". ")
                score = None
                try:
                    score = int(words[0])
                    score = min(max(score, 1), 100)
                except (ValueError, AssertionError) as error:
                    logger.debug(
                        f"Issue with GPT response {evaluation_response} while"
                        " generating score."
                    )

                score = score or DEFAULT_SCORE
                search_result.score = score

            search_results.append(search_result)

        return search_results

    except Exception as error:
        update_campaign_run_status(campaign, f"Exception: {repr(error)}")
        raise
