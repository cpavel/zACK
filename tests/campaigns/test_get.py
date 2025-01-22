import pytest
from django.urls import reverse
from zACK import enums
from campaigns.models import Campaign


@pytest.fixture
def get_campaign_request(api_client):
    def _make_request(id):
        return api_client.get(f"/campaigns/get/{id}")

    return _make_request


@pytest.fixture
def get_url():
    return reverse("campaigns:get_campaign", args=(1,))


def test_get_url(get_url):
    assert get_url == "/campaigns/get/1"


def test_get_campaign_by_id(baker, get_campaign_request):
    user = baker.make(
        "auth.User",
        id=1,
    )
    campaign = baker.make(
        "campaigns.Campaign",
        id=1,
        user=user,
        name="Hello",
        locations=[enums.SearchLocation.HACKER_NEWS],
        search_terms="Hello search term",
        post_evaluation_prompt="Test",
        response_evaluation_prompt="Test",
    )
    response = get_campaign_request(campaign.pk)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user": 1,
        "name": "Hello",
        "locations": [enums.SearchLocation.HACKER_NEWS],
        "search_terms": "Hello search term",
        "post_evaluation_prompt": "Test",
        "response_evaluation_prompt": "Test",
        "prompt_templates": [],
    }


def test_get_campaign_by_id_with_prompt_templates(baker, get_campaign_request):
    user = baker.make(
        "auth.User",
        id=1,
    )
    campaign = baker.make(
        "campaigns.Campaign",
        id=1,
        user=user,
        name="Hello",
        locations=[enums.SearchLocation.HACKER_NEWS],
        search_terms="Hello search term",
        post_evaluation_prompt="Test",
        response_evaluation_prompt="Test",
    )
    prompt_template1 = baker.make(
        "data.PromptTemplate", campaign=campaign, template="Hello template1"
    )
    prompt_template2 = baker.make(
        "data.PromptTemplate", campaign=campaign, template="Hello template2"
    )
    response = get_campaign_request(campaign.pk)

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user": 1,
        "name": "Hello",
        "locations": [enums.SearchLocation.HACKER_NEWS],
        "search_terms": "Hello search term",
        "post_evaluation_prompt": "Test",
        "response_evaluation_prompt": "Test",
        "prompt_templates": [
            {
                "id": prompt_template1.id,
                "campaign_id": campaign.id,
                "template": "Hello template1",
            },
            {
                "id": prompt_template2.id,
                "campaign_id": campaign.id,
                "template": "Hello template2",
            },
        ],
    }
