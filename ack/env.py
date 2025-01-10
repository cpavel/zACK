import os
import os.path
from dotenv import load_dotenv

# Load .env into environment variable if exists
load_dotenv()

DB_USER = os.environ["DB_USER"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]

ENV_REDIS_HOSTNAME = os.environ["REDIS_HOSTNAME"]
ENV_REDIS_PORT = os.environ["REDIS_PORT"]
ENV_REDIS_PASSWORD = os.environ["REDIS_PASSWORD"]

RUNNING_ENVIRONMENT = os.environ.get("RUNNING_ENVIRONMENT", "dev")
OPENAI_ORGANIZATION_ID = os.environ["OPENAI_ORGANIZATION_ID"]
OPENAI_KEY = os.environ["OPENAI_KEY"]
DJANGO_SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

CELERY_BROKER_URL = os.environ["CELERY_BROKER_URL"]
CELERY_RESULT_BACKEND = os.environ["CELERY_RESULT_BACKEND"]

# Bools
DJANGO_DEBUG = os.environ["DJANGO_DEBUG"] == "True"
ENABLE_REAL_CELERY_IN_TESTING = (
    os.environ["ENABLE_REAL_CELERY_IN_TESTING"] == "True"
)
ENABLE_REAL_API_IN_TESTING = os.environ["ENABLE_REAL_API_IN_TESTING"] == "True"
