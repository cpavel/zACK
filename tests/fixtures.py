import pytest
from django.contrib.auth.models import User
from model_bakery import baker as baker_lib
from rest_framework.test import APIClient

from ack.env import ENABLE_REAL_API_IN_TESTING, ENABLE_REAL_CELERY_IN_TESTING


@pytest.fixture
def client():
    client = APIClient()
    yield client


@pytest.fixture
def admin_client():
    return "pass"


@pytest.fixture
def user():
    return User.objects.create_user(
        "john", "lennon@thebeatles.com", "johnpassword"
    )


@pytest.fixture
def enable_api_tests():
    return ENABLE_REAL_API_IN_TESTING


@pytest.fixture
def enable_celery_tests():
    return ENABLE_REAL_CELERY_IN_TESTING


@pytest.fixture
def baker():
    yield baker_lib


@pytest.fixture
def baker_make():
    yield baker_lib.make


@pytest.fixture
def reach_out_template():
    return """
Hey there!

My name is Dimitri and I run a company called Lights on
Software out of Toronto, Canada. I saw a recent comment on
HackerNews about software and I thought I'd reach out to
see if I could talk to you about my services.

Let me know!

Dimitri Gidnash
Lights on Software
"""


@pytest.fixture
def city_check_evaluation_template():
    return """
If this generated response suggest a meeting, then it should only be
in Toronto, Canada. If it suggests an over the phone or computer discussion is
acceptable, but a in person meeting is only acceptable if it is in Toronto.
"""


@pytest.fixture(autouse=True)
def fix_django_db(db):
    """
    This fixture does nothing more than auto-use the
    db fixture every single time. It's worth it.
    """
