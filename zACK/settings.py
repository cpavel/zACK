from pathlib import Path
import os

from .env import (
    DJANGO_DEBUG,
    DJANGO_SECRET_KEY,
    RUNNING_ENVIRONMENT,
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
    DB_NAME,
)
from .env import ENV_REDIS_HOSTNAME, ENV_REDIS_PORT, ENV_REDIS_PASSWORD
from .settings_helpers import one

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = DJANGO_SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
assert isinstance(DJANGO_DEBUG, bool)
DEBUG = DJANGO_DEBUG

STATIC_DIR = f"{BASE_DIR}/static"
STATIC_ROOT = STATIC_DIR

STATIC_URL = "/static/"


ALLOWED_HOSTS = [
    "localhost",  # Local.
    "127.0.0.1",  # Local.
    "159.203.34.127",  # Prod IP.
    "builtwithml.org",  # Prod domain.
    "www.builtwithml.org",  # Prod alt domain.
    "api.zack.test",
]

CSRF_TRUSTED_ORIGINS = [
    "https://builtwithml.org",
    "https://www.builtwithml.org",
]


EXTERNAL_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "django_browser_reload",
    "django_extensions",
    "rest_framework",
    "rest_framework.authtoken",
    "tailwind",
]

INTERNAL_APPS = [
    "zACK",
    "data",
    "leads",
    "campaigns",
    "ui",
]

INSTALLED_APPS = EXTERNAL_APPS + INTERNAL_APPS

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
]


MIDDLEWARE = [  # ORDER MATTERS! DO NOT SORT!
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

ROOT_URLCONF = "zACK.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "zACK.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": DB_HOST,
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation.NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "en-us"
TIME_ZONE = "EST"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TAILWIND_APP_NAME = "ui"

REST_FRAMEWORK = {
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

REDIS_HOSTNAME = os.getenv('REDIS_HOSTNAME', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_IMPORTS = ("zACK.tasks",)

# TODO: Set in pytest.
IS_TEST = RUNNING_ENVIRONMENT == "test"
IS_STAGING = RUNNING_ENVIRONMENT == "staging"
IS_DEV = RUNNING_ENVIRONMENT == "dev"
IS_PROD = RUNNING_ENVIRONMENT == "prod"

BACKOFF_MAX_TRIES = 3 if IS_TEST or not IS_PROD else 5
SEARCH_LIMIT = 1 if IS_TEST or not IS_PROD else 20

assert one(IS_DEV, IS_PROD, IS_STAGING)

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Optional: Celery settings
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
