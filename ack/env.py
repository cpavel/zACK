import os
import os.path
from dotenv import load_dotenv

# Load .env into environment variable if exists
load_dotenv()

DB_USER = os.environ.get("DB_USER", "admin")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "admin")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_NAME = os.environ.get("DB_NAME", "zackdb")

ENV_REDIS_HOSTNAME = os.environ.get("REDIS_HOSTNAME", "localhost")
ENV_REDIS_PORT = os.environ.get("REDIS_PORT", 6379)
ENV_REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD", "")

RUNNING_ENVIRONMENT = os.environ.get("RUNNING_ENVIRONMENT", "dev")
OPENAI_ORGANIZATION_ID = os.environ.get("OPENAI_ORGANIZATION_ID", "")
OPENAI_KEY = os.environ.get("OPENAI_KEY", "")
DJANGO_SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "default_secret_key")

CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# Bools
DJANGO_DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
ENABLE_REAL_CELERY_IN_TESTING = os.environ.get("ENABLE_REAL_CELERY_IN_TESTING", "True") == "True"
ENABLE_REAL_API_IN_TESTING = os.environ.get("ENABLE_REAL_API_IN_TESTING", "True") == "True"

CUSTOM_LLM_API_BASE_URL = os.environ.get("CUSTOM_LLM_API_BASE_URL", "")
CUSTOM_LLM_API_KEY = os.environ.get("CUSTOM_LLM_API_KEY", "")
