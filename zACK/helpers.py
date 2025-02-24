import os
import datetime
import logging
import time
import json
from django.conf import settings
from html import unescape
from time import sleep
from typing import Optional, Union
import backoff

import openai
from openai.error import RateLimitError
import redis
import requests
from urllib.parse import quote
from django.utils.html import strip_tags
from zACK.celery import app
from data.models import EvaluationTemplate, PromptTemplate, SearchTerm

from .env import (
    OPENAI_ORGANIZATION_ID,
    OPENAI_KEY,
    CUSTOM_LLM_API_BASE_URL,
    CUSTOM_LLM_API_KEY,
    CUSTOM_LLM_MODEL,
    IS_DEV,
)
from .instructions import hacker_news
from .settings import REDIS_HOSTNAME, REDIS_PASSWORD, REDIS_PORT

HN_API_ROOT = "https://hn.algolia.com/api/v1"

LOGS_DIR = "./logs/"
SEARCH_TERM_LOG_FILE_NAME = "{}searchterm-{}.log"
RESULTS_LOG_FILE = os.path.join(LOGS_DIR, "results.log")

os.makedirs(LOGS_DIR, exist_ok=True)

# Initialize logger
logging.basicConfig(filename=LOGS_DIR + "zack.log", filemode="a")
logger = logging.getLogger(__name__)

if IS_DEV:
    logger.setLevel(logging.DEBUG)
    # add StreamHandler log handler
    console_logger = logging.StreamHandler()
    console_logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_logger.setFormatter(formatter)
    logger.addHandler(console_logger)

    logger.info("Running in DEV mode")

    handler = logging.FileHandler(RESULTS_LOG_FILE)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
    logger.addHandler(handler)

# Load system prompts from JSON file with error handling
def load_system_prompt(role: str):
    try:
        with open("/opt/zACK/system_prompts.json", "r") as file:
            data = json.load(file)
            return data.get(role, {}).get("system_prompt", "")
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Error loading system prompt for {role}: {e}")
        return ""

evaluator_system_prompt = load_system_prompt("evaluator")
post_generator_system_prompt = load_system_prompt("post_generator")

# Initialize the LLM client based on environment variables
if OPENAI_ORGANIZATION_ID and OPENAI_KEY:
    openai.organization = OPENAI_ORGANIZATION_ID
    openai.api_key = OPENAI_KEY
    client = openai
else:
    from openai import OpenAI
    client = OpenAI(
        api_key=CUSTOM_LLM_API_KEY,
        base_url=CUSTOM_LLM_API_BASE_URL,
    )

ONE_HOUR = 60 * 60
ONE_DAY = ONE_HOUR * 24

HACKER_NEWS_BASE_ITEM_HOST = "https://news.ycombinator.com/item?id="
HACKER_NEWS_API_HOST = "https://hn.algolia.com/api/v1"
HACKER_NEWS_HOURLY_RATE_LIMIT = 10_000

class HackerNewsRateLimitError(Exception):
    pass

# Use redis_client for the normal redis client, and this class
# if you need to customize it.
class RedisClient:
    def __init__(self):
        self._client = redis.Redis(
            host=settings.REDIS_HOSTNAME,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD
        )

    def set_int(self, key: str, value: int, ttl: Optional[int] = None) -> None:
        if not isinstance(value, int):
            raise ValueError(
                f"Expected int not `{type(value)}` for key `{key}`"
            )

        typed_value = f"int#{value}"
        self._client.set(key, typed_value, ex=ttl)

    def set_str(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        if not isinstance(value, str):
            raise ValueError(
                f"Expected str not `{type(value)}` for key `{key}`"
            )

        typed_value = f"str#{value}"
        self._client.set(key, typed_value, ex=ttl)

    def get(self, key: str) -> Optional[Union[str, int]]:
        _value = self._client.get(key)
        if _value is None:
            return None
        _value = _value.decode("utf-8")

        _type, value = _value.split("#", maxsplit=1)
        if _type == "int":
            return int(value)
        if _type == "str":
            return str(value)
        else:
            raise NotImplementedError("Unimplemented type")

        return value

    def set(self, *args, **kwargs) -> None:
        raise NotImplementedError(
            "This method is intentionally disallowed. Use type specific"
            " methods instead."
        )


def get_redis_client():
    client = RedisClient()
    return client


redis_client = get_redis_client()


class HackerNewsClient:
    def __init__(self, redis_client: Optional[RedisClient] = None) -> None:
        self.redis_client = redis_client or get_redis_client()

    def rate_limit_key(self) -> str:
        unix_timestamp = int(time.time())
        hourly_unix_timestamp = unix_timestamp - (unix_timestamp % ONE_HOUR)
        key = "zACK.helpers.HackerNewsClient.rate_limit_remaining."
        key += str(hourly_unix_timestamp)
        return key

    def check_rate_limit(self, remaining_rate: int):
        key = self.rate_limit_key()
        remaining = self.redis_client.get(key)
        if not remaining:
            remaining = 10_000
            self.redis_client.set_int(key, remaining)

        if remaining < remaining_rate:
            # Must not be banned, so keep below limit conservatively.
            raise HackerNewsRateLimitError(
                "Too close to HackerNews rate limit."
            )

        return remaining

    # TODO: Consider locks or atomic decrement.
    def decrement_hacker_news_rate_limit(self):
        key = self.rate_limit_key()
        value = self.redis_client.get(key) or HACKER_NEWS_HOURLY_RATE_LIMIT
        value -= 1
        self.redis_client.set_int(key, value)

    def search_hacker_news(self, term: Optional[str] = None):
        logger.info("Initiating search for term: %s", term)

        self.check_rate_limit(remaining_rate=2000)

        unix_timestamp = str(int(time.time()) - ONE_DAY)
        url = HACKER_NEWS_API_HOST + "/search_by_date?"
        url += "tags=comment"
        url += "&numericFilters=created_at_i>" + unix_timestamp
        url += "&query=" + quote(term)

        logger.info("Search URL: %s", url)

        retries = 3
        response = self.get(url)
        while not response.status_code == 200:
            logger.warning("Response: %i. Retrying", response.status_code)
            if retries < 1:
                response.raise_for_status()

            sleep(0.5)
            retries -= 1
            response = self.get(url)

        hits = response.json().get("hits", [])
        logger.info("Hits collected: %i", len(hits))

        for hit in hits:
            logger.info("Found comment by %s: %s", hit["author"], hit["comment_text"])

        return response

    def get_hacker_news_profile(self, username: str, force: bool = False) -> tuple[str, str]:
        logger.info("Fetching profile for user: %s", username)

        self.check_rate_limit(remaining_rate=300)

        key = f"zACK.helpers.get_hacker_news_profile.{username}.about"
        profile_about = redis_client.get(key)
        url = "https://hn.algolia.com/api/v1/users/" + username
        hacker_news_url = "https://news.ycombinator.com/user?id=" + username
        if not profile_about:
            response = self.get(url)
            profile_about = response.json().get("about", "")
            profile_about = profile_about.strip() if profile_about else ""
            redis_client.set_str(key, value=profile_about, ttl=ONE_DAY)
            logger.info("Profile about for %s: %s", username, profile_about)

        return profile_about, hacker_news_url

    def get_hacker_news_context(self, search_term_hits):
        for rec in search_term_hits:
            # Strip special characters and html tags
            comment = unescape(strip_tags(rec["comment_text"]))
            comment_url = HACKER_NEWS_BASE_ITEM_HOST + rec["objectID"]
            username = rec["author"]

            # TODO: Get other metrics like profile age, etc.
            profile_about, profile_url = (
                hacker_news_client.get_hacker_news_profile(username)
            )

            profile_about = unescape(strip_tags(profile_about))

            yield username, comment, comment_url, profile_about, profile_url

    def get(self, *args, **kwargs):
        self.decrement_hacker_news_rate_limit()
        return requests.get(*args, **kwargs)


hacker_news_client = HackerNewsClient()


def get_hacker_news_client():
    return HackerNewsClient()


def get_openai_models():
    return openai.Model.list()


def build_hacker_news_post_evaluation(template: str, prompt: str):
    response = hacker_news.post_evaluation_1
    response += prompt
    response += hacker_news.post_evaluation_2
    response += template
    response += hacker_news.post_evaluation_3
    return response


def build_hacker_news_response_evaluation(template: str, prompt: str):
    response = hacker_news.aoi_evaluation_1
    response += prompt
    response += hacker_news.aoi_evaluation_2
    response += template
    response += hacker_news.aoi_evaluation_3
    return response


def build_hacker_news_oai_instruction(
    prompt_template: PromptTemplate, comment: str, profile_about: str, username: str,
):
    prompt_request = hacker_news.oai_instruction_1
    prompt_request += prompt_template.template
    prompt_request += hacker_news.oai_instruction_2
    prompt_request += comment
    prompt_request += hacker_news.oai_instruction_3
    prompt_request += username
    prompt_request += hacker_news.oai_instruction_4
    prompt_request += profile_about
    prompt_request += hacker_news.oai_instruction_5

    return prompt_request


def get_oai_model() -> str:
    if datetime.date.today().year >= 2025:
        # Don't forget to update the ^^^^ too!
        logger.critical("You must upgrade the openai model below to latest!")

    return "gpt-3.5-turbo"


@backoff.on_exception(
    backoff.expo, RateLimitError, max_tries=settings.BACKOFF_MAX_TRIES
)
def chat_completion(prompt: str, role: str):
    model = get_oai_model()
    system_prompt = evaluator_system_prompt if role == "evaluator" else post_generator_system_prompt
    response = client.chat.completions.create(
        model=CUSTOM_LLM_MODEL if CUSTOM_LLM_API_KEY else model,
        messages=[
            {
                "role": "system",
                "content": system_prompt if CUSTOM_LLM_API_KEY else role,
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=2000,
        temperature=0.7,
        top_p=1,
        n=1,
        stream=False,
        frequency_penalty=0,
        presence_penalty=0.5,
        stop=[]
    )

    try:
        content = response.choices[0].message.content
    except Exception:
        logger.error("No response generated by ChatCompletion API.")
        return None

    return content


def run_evaluation(prompt: str):
    return chat_completion(prompt, "evaluator")


def run_reword(prompt: str):
    return chat_completion(prompt, "post_generator")


def merge_defaults(_dict, defaults):
    # Merge in defaults if not present as keys in kwargs.
    _dict_copy = _dict.copy()
    _dict.update(defaults)
    _dict.update(_dict_copy)
    return _dict


TASK_DEFAULTS = {
    "bind": True,
    "max_retries": 5,
    "retry_backoff": True,
}

def process_search_results(search_results, campaign):
    for result in search_results:
        # Ensure campaign is provided
        lead_result = LeadSearchResult(
            campaign=campaign,  # Ensure this is provided
            search_term=result['search_term'],
            location=result['location'],
            username=result['username'],
            profile_about=result['profile_about'],
            profile_url=result['profile_url'],
            comment=result['comment'],
            # Add other required fields if necessary
        )
        # Evaluate the lead result
        evaluate_lead(lead_result)

def evaluate_lead(lead_result):
    # Implement evaluation logic based on system_prompts.json
    evaluation_criteria = settings.SYSTEM_PROMPTS['evaluator']['evaluation_criteria']
    score = evaluate_post(lead_result.comment, evaluation_criteria)
    if score >= 3:  # Example threshold
        response = generate_response(lead_result.comment, score, settings.SYSTEM_PROMPTS['post_generator'])
        if response:
            logger.info(f"Generated response: {response}")
            # Handle response (e.g., log, store, or post)

def evaluate_post(post, evaluation_criteria):
    # Implement evaluation logic based on system_prompts.json
    score = 0
    # Example: Check for keywords in post
    for criterion, description in evaluation_criteria.items():
        if any(keyword in post for keyword in description.split()):
            score += 1
    return score

def generate_response(post, score, post_generator):
    # Implement response generation logic
    if score >= 3:  # Example threshold
        response = f"Response to post: {post}"
        # Use LLM to generate a detailed response
        return response
    return None

@app.task
def search_and_respond(search_term_id):
    search_term = SearchTerm.objects.get(id=search_term_id)
    # Simulate search on Hacker News
    posts = ["Example post about GPU costs", "Another post about AI optimization"]
    evaluation_criteria = settings.SYSTEM_PROMPTS['evaluator']['evaluation_criteria']
    post_generator = settings.SYSTEM_PROMPTS['post_generator']

    for post in posts:
        score = evaluate_post(post, evaluation_criteria)
        response = generate_response(post, score, post_generator)
        if response:
            if IS_DEV:
                logger.info(f"Post: {post}, Score: {score}, Response: {response}")
            else:
                # Implement posting logic in production
                pass


class TwitterClient:
    def __init__(self, api_key, api_secret_key, access_token, access_token_secret):
        self.api_key = api_key
        self.api_secret_key = api_secret_key
        self.access_token = access_token
        self.access_token_secret = access_token_secret

    def search_twitter(self, query, count=100):
        url = "https://api.twitter.com/1.1/search/tweets.json"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        params = {
            "q": query,
            "count": count,
            "result_type": "recent",
            "tweet_mode": "extended"
        }
        response = requests.get(url, headers=headers, params=params)
        return response


def search_twitter(query, count=100):
    twitter_client = TwitterClient(
        api_key=settings.TWITTER_API_KEY,
        api_secret_key=settings.TWITTER_API_SECRET_KEY,
        access_token=settings.TWITTER_ACCESS_TOKEN,
        access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
    )
    return twitter_client.search_twitter(query, count)
