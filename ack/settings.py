from pathlib import Path

from .env import (
    DJANGO_DEBUG,
    DJANGO_SECRET_KEY,
    RUNNING_ENVIRONMENT,
    DB_USER,
    DB_PASSWORD,
    DB_HOST,
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
    "142.93.50.205",  # Zach Aysan's dev IP.
    "142.93.164.53",  # Prod IP.
    "builtwithml.org",  # Prod domain.
    "www.builtwithml.org",  # Prod alt domain.
    "api.ack.test",
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
    "ack",
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

ROOT_URLCONF = "ack.urls"

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

WSGI_APPLICATION = "ack.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": DB_HOST,
        "NAME": "ack",
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

REDIS_HOSTNAME = ENV_REDIS_HOSTNAME
REDIS_PORT = ENV_REDIS_PORT
REDIS_PASSWORD = ENV_REDIS_PASSWORD

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_IMPORTS = ("ack.tasks",)

# TODO: Set in pytest.
IS_TEST = RUNNING_ENVIRONMENT == "test"
IS_STAGING = RUNNING_ENVIRONMENT == "staging"
IS_DEV = RUNNING_ENVIRONMENT == "dev"
IS_PROD = RUNNING_ENVIRONMENT == "prod"

BACKOFF_MAX_TRIES = 3 if IS_TEST or not IS_PROD else 5
SEARCH_LIMIT = 1 if IS_TEST or not IS_PROD else 20

assert one(IS_DEV, IS_PROD, IS_STAGING)
