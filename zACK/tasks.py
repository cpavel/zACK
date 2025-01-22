import os
import logging
from html import unescape
import random
from typing import Optional
from dataclasses import asdict

from django.conf import settings
from django.contrib.auth.models import User
from leads.models import Lead
from django.db import transaction
from django.utils.html import strip_tags

from zACK import enums
from zACK.celery import app
from .instructions import hacker_news

from zACK.helpers import (
    HackerNewsRateLimitError,
    build_hacker_news_response_evaluation,
    build_hacker_news_oai_instruction,
    hacker_news_client,
    logger,
    LOGS_DIR,
    SEARCH_TERM_LOG_FILE_NAME,
    run_evaluation,
    run_reword,
)

from data.models import PromptTemplate, SearchTerm
from leads.helpers import LeadSearchResult, store_search_results

# TODO: Increase the prod limit once we have rate limiting available for the API.
# See more here https://github.com/openai/openai-cookbook/blob/main/examples/How_to_handle_rate_limits.ipynb

LEADS_BATCH_SIZE = 100


@app.task
def async_search_term_by_id(search_term_id: int):
    try:
        log_file_path = SEARCH_TERM_LOG_FILE_NAME.format(
            LOGS_DIR, search_term_id
        )

        try:
            os.remove(log_file_path)
        except FileNotFoundError:
            pass

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        search_leads(search_term_id=search_term_id)

    finally:
        if file_handler:
            logger.removeHandler(file_handler)
            file_handler.close()

    return


def get_hacker_news_context(search_term_hits):
    for rec in search_term_hits:
        # Strip special characters and html tags
        comment = unescape(strip_tags(rec["comment_text"]))
        username = rec["author"]

        # TODO: Get other metrics like profile age, etc.
        profile_about, profile_url = (
            hacker_news_client.get_hacker_news_profile(username)
        )

        profile_about = unescape(strip_tags(profile_about))

        yield username, comment, profile_about, profile_url


# For performance, i.e., not hitting the DB every loop.
def filter_prompt_templates(
    prompt_templates: list[PromptTemplate], profile_length: int
):
    results: list[PromptTemplate] = []
    last_message = "No prompt templates found"

    for prompt_template in prompt_templates:
        if prompt_template.min_profile_length is None:
            results.append(prompt_template)
            continue

        if prompt_template.min_profile_length > profile_length:
            last_message = (
                f"Prompt template #{prompt_template.id} is skipped because"
                " user profile is too short"
            )
            logger.debug(last_message)
            continue

        if prompt_template.max_profile_length is None:
            results.append(prompt_template)
            continue

        if prompt_template.max_profile_length >= profile_length:
            results.append(prompt_template)
            continue
        else:
            last_message = (
                f"Prompt template #{prompt_template.id} is skipped because"
                " user profile is too long"
            )
            logger.debug(last_message)

    return results, last_message


def format_log_msg(
    message_txt: str,
    search_term: SearchTerm,
    iteration_no: str = None,
    user_name: str = None,
):
    log_message = f"Search term [{search_term.id}]"

    if iteration_no:
        log_message += f" #{iteration_no}"

    if user_name:
        log_message += f" - {user_name}"

    log_message += ": " + message_txt

    return log_message


def set_search_term_run_status(search_term: SearchTerm, status_text: str):
    logger.info(status_text)
    search_term.run_status = status_text
    search_term.save()
    return


# TODO: Once the patterns are clear, refactor this task into
# a service object or smaller functions.
def search_leads(
    location: enums.SearchLocation = None,
    user_id: int = None,
    search_term_id: int = None,
    limit=settings.SEARCH_LIMIT,
):
    logger.info(
        "Searching terms for"
        f" user_id={user_id} search_term_id={search_term_id}"
    )

    # Get bulk search terms by user_id  or  single search term by id
    if search_term_id is None:
        user = User.objects.get(id=user_id)

        search_terms = user.search_terms.filter(
            location=location,
        )
    else:
        search_terms = SearchTerm.objects.filter(id=search_term_id)

    if not search_terms:
        logger.warning(
            "No search terms found:"
            f" user_id={user_id} search_term_id={search_term_id}"
        )
        return

    logger.info(
        f"Use https://platform.openai.com/playground for testing.\n----"
    )
    logger.info(
        "ChatGPT Reword"
        f" Role:\n{hacker_news.oai_reword_role_instructions}\n----"
    )
    logger.info(
        "ChatGPT Evaluate"
        f" Role:\n{hacker_news.oai_evaluation_role_instructions}\n----"
    )

    search_results = []
    for search_term in search_terms:
        set_search_term_run_status(
            search_term,
            format_log_msg(
                "Source: " + enums.SearchLocation(search_term.location).label,
                search_term,
            ),
        )
        try:
            response = hacker_news_client.search_hacker_news(search_term.term)

            assert (
                response.status_code == 200
            ), "Wrong search term response code"

            hits_counter = 0
            hits_context = get_hacker_news_context(response.json()["hits"])

            # Loads a max of 100 random templates into ram.
            prompt_templates = search_term.prompt_templates.order_by("?")[:100]

            for (
                username,
                comment,
                profile_about,
                profile_url,
            ) in hits_context:
                hits_counter += 1
                set_search_term_run_status(
                    search_term,
                    format_log_msg(
                        "Prompt request", search_term, hits_counter, username
                    ),
                )

                search_result = LeadSearchResult(
                    search_term=search_term,
                    location=enums.SearchLocation(search_term.location),
                    username=username,
                    profile_about=profile_about,
                    profile_url=profile_url,
                    comment=comment,
                )
                search_results.append(search_result)

                profile_length = len(profile_about)
                # Does not hit the DB, since in ram.
                matching_prompt_templates, last_message = (
                    filter_prompt_templates(
                        prompt_templates=prompt_templates,
                        profile_length=profile_length,
                    )
                )

                if not matching_prompt_templates:
                    logger.info(
                        format_log_msg(
                            f"No matching prompt templates: {last_message}",
                            search_term,
                            hits_counter,
                            username,
                        )
                    )
                    search_result.prompt_request_text = last_message
                    search_result.prompt_response_text = (
                        search_result.prompt_request_text
                    )
                    continue

                prompt_template = random.choice(matching_prompt_templates)
                search_result.prompt_template = prompt_template.template

                prompt_instruction = build_hacker_news_oai_instruction(
                    prompt_template=prompt_template,
                    comment=comment,
                    profile_about=profile_about,
                )
                search_result.prompt_request_text = prompt_instruction

                logger.debug(
                    format_log_msg(
                        (
                            "[Prompt request]"
                            f" ChatGPT:\n----\nRole:\n{hacker_news.oai_reword_role_instructions}\n----\nInstructions:\n{prompt_instruction}\n---"
                        ),
                        search_term,
                        hits_counter,
                        username,
                    )
                )
                prompt_response_text = run_reword(prompt_instruction)
                assert prompt_response_text is not None
                search_result.prompt_response_text = prompt_response_text

                logger.debug(
                    format_log_msg(
                        f"Prompt response:\n----\n{prompt_response_text}\n---",
                        search_term,
                        hits_counter,
                        username,
                    )
                )

                default_score = 1
                score: Optional[int] = None
                evaluation_template = prompt_template.evaluation_template

                if evaluation_template:
                    set_search_term_run_status(
                        search_term,
                        format_log_msg(
                            "Evaluate request",
                            search_term,
                            hits_counter,
                            username,
                        ),
                    )

                    evaluation_instruction = (
                        build_hacker_news_response_evaluation(
                            template=evaluation_template.template,
                            prompt_response_message=prompt_response_text,
                        )
                    )

                    search_result.evaluate_request_text = (
                        evaluation_instruction
                    )

                    logger.debug(
                        format_log_msg(
                            (
                                "Evaluate"
                                f" request:\n----Role:\n{hacker_news.oai_evaluation_role_instructions}\n----\n{evaluation_instruction}\n---"
                            ),
                            search_term,
                            hits_counter,
                            username,
                        )
                    )

                    evaluation_response = run_evaluation(
                        evaluation_instruction
                    )
                    assert evaluation_response is not None

                    logger.debug(
                        format_log_msg(
                            (
                                "Evaluate"
                                f" response:\n----\n{evaluation_response}\n---"
                            ),
                            search_term,
                            hits_counter,
                            username,
                        )
                    )

                    search_result.evaluate_response_text = evaluation_response

                    # Assume response has score in first word delimited by . or space
                    words = evaluation_response.split(". ")

                    try:
                        score = int(words[0])
                        assert 0 <= score <= 100
                    except (ValueError, AssertionError) as error:
                        logger.warning(
                            format_log_msg(
                                "Incorrect output from evaluation model",
                                search_term,
                                hits_counter,
                                username,
                            )
                        )

                # Indicates either a missing evaluation template
                # or a failure to parse the evaluation.
                if score is None:
                    score = default_score
                    logger.warning(
                        format_log_msg(
                            f"Score is not defined. Set score to {score}",
                            search_term,
                            hits_counter,
                            username,
                        )
                    )

                # TODO: Move this into user settings and
                # customizable in the evaluation template.
                # evaluation_threshold = 60
                # if score < evaluation_threshold:
                #     logger.info(
                #         (
                #             f"User profile: {username}. Score {score}. "
                #             "Skipping prompt response message as it did not meet"
                #             f" the evaluation threshold of {evaluation_threshold}"
                #         )
                #     )
                #     continue

                search_result.score = score

                logger.info(
                    format_log_msg(
                        f"User added to results. Current limit: {limit}",
                        search_term,
                        hits_counter,
                        username,
                    )
                )

                limit -= 1
                if limit < 1:
                    logger.info(
                        format_log_msg(
                            "Stopped because of limit.",
                            search_term,
                            hits_counter,
                            username,
                        )
                    )
                    break
            if limit < 1:
                logger.info(
                    format_log_msg(
                        "Stopped because of limit.",
                        search_term,
                        hits_counter,
                        username,
                    )
                )
                break
        except HackerNewsRateLimitError:
            set_search_term_run_status(
                search_term, "Exception: HackerNewsRateLimitError"
            )
            break
        except Exception as error:
            set_search_term_run_status(
                search_term, f"Exception: {repr(error)}"
            )
            raise

    if not search_results:
        logger.warning("No search results matched existing key words")
        if search_term_id is not None:
            set_search_term_run_status(
                search_terms[0], "No search results found"
            )
        return

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
        len(processed_results) + LEADS_BATCH_SIZE - 1
    ) // LEADS_BATCH_SIZE

    # Use transaction.atomic() to ensure atomicity of bulk_create
    with transaction.atomic():
        for batch_number in range(num_batches):
            start_index = batch_number * LEADS_BATCH_SIZE
            end_index = start_index + LEADS_BATCH_SIZE
            batch = processed_results[start_index:end_index]
            Lead.objects.bulk_create([Lead(**item) for item in batch])

    # Generate TSV file
    if search_term_id is None:
        file_suffix = "user-" + str(user_id)
    else:
        file_suffix = str(search_term_id)

    results_path = store_search_results(
        file_name_suffix=file_suffix,
        search_results=search_results,
    )

    logger.info(f"Results are stored to {results_path}")

    if search_term_id is not None:
        set_search_term_run_status(search_terms[0], "Done")

@app.task
def run_search_task(search_term_id):
    logger.info(f"Running search task for search term ID: {search_term_id}")
    # Your task logic here
