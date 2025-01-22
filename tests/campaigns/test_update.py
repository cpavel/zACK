import pytest
from django.urls import reverse
from zACK import enums
from campaigns.models import Campaign
from data.models import PromptTemplate


@pytest.fixture
def update_campaign_request(api_client):
    def _make_request(id, data):
        return api_client.put(f"/campaigns/update/{id}", data)

    return _make_request


@pytest.fixture
def update_url():
    return reverse("campaigns:update_campaign", args=(1,))


def test_update_url(update_url):
    assert update_url == "/campaigns/update/1"


def test_update_campaign_partial_data(baker, update_campaign_request):
    user = baker.make(
        "auth.User",
        id=1,
    )
    _ = baker.make(
        "campaigns.Campaign",
        id=1,
        user=user,
        name="Hello",
        locations=[enums.SearchLocation.HACKER_NEWS],
        search_terms="Hello search term",
        post_evaluation_prompt="Test",
        response_evaluation_prompt="Test",
    )
    response = update_campaign_request(
        1,
        {
            "name": "Updated",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user": 1,
        "name": "Updated",
        "locations": [enums.SearchLocation.HACKER_NEWS],
        "search_terms": "Hello search term",
        "post_evaluation_prompt": "Test",
        "response_evaluation_prompt": "Test",
        "prompt_templates": [],
    }


def test_update_campaign(baker, update_campaign_request):
    user = baker.make(
        "auth.User",
        id=1,
    )
    _ = baker.make(
        "campaigns.Campaign",
        id=1,
        user=user,
        name="Hello",
        locations=[enums.SearchLocation.HACKER_NEWS],
        search_terms="Hello search term",
        post_evaluation_prompt="Test",
        response_evaluation_prompt="Test",
    )
    response = update_campaign_request(
        1,
        {
            "name": "Updated",
            "search_terms": "New st",
            "post_evaluation_prompt": "New pep",
            "response_evaluation_prompt": "New rep",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user": 1,
        "name": "Updated",
        "locations": [enums.SearchLocation.HACKER_NEWS],
        "search_terms": "New st",
        "post_evaluation_prompt": "New pep",
        "response_evaluation_prompt": "New rep",
        "prompt_templates": [],
    }


def test_update_campaign_add_prompt_templates(baker, update_campaign_request):
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
    response = update_campaign_request(
        1,
        {
            "name": "New",
            "prompt_templates": [
                {"template": "hello1"},
                {"template": "hello2"},
            ],
        },
    )

    prompt_templates = PromptTemplate.objects.all()

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user": 1,
        "name": "New",
        "locations": [enums.SearchLocation.HACKER_NEWS],
        "search_terms": "Hello search term",
        "post_evaluation_prompt": "Test",
        "response_evaluation_prompt": "Test",
        "prompt_templates": [
            {
                "id": prompt_templates[0].id,
                "campaign_id": campaign.id,
                "template": "hello1",
            },
            {
                "id": prompt_templates[1].id,
                "campaign_id": campaign.id,
                "template": "hello2",
            },
        ],
    }
    assert prompt_templates.count() == 2
    assert prompt_templates[0].template == "hello1"
    assert prompt_templates[1].template == "hello2"


def test_update_campaign_update_existing_prompt_templates(
    baker, update_campaign_request
):
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

    response = update_campaign_request(
        1,
        {
            "name": "New",
            "prompt_templates": [
                {"template": "hello1"},
                {"template": "hello2"},
            ],
        },
    )

    campaign_prompt_templates = PromptTemplate.objects.filter(
        campaign=campaign
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user": 1,
        "name": "New",
        "locations": [enums.SearchLocation.HACKER_NEWS],
        "search_terms": "Hello search term",
        "post_evaluation_prompt": "Test",
        "response_evaluation_prompt": "Test",
        "prompt_templates": [
            {
                "id": campaign_prompt_templates[0].id,
                "campaign_id": campaign.id,
                "template": "hello1",
            },
            {
                "id": campaign_prompt_templates[1].id,
                "campaign_id": campaign.id,
                "template": "hello2",
            },
        ],
    }
    assert campaign_prompt_templates.count() == 2


def test_update_campaign_overwrites_existing_prompt_templates(
    baker, update_campaign_request
):
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

    response = update_campaign_request(
        1,
        {
            "name": "New",
            "prompt_templates": [
                {"template": "hello1"},
                {"template": "hello2"},
                {"template": "hello3"},
            ],
        },
    )

    campaign_prompt_templates = PromptTemplate.objects.filter(
        campaign=campaign
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user": 1,
        "name": "New",
        "locations": [enums.SearchLocation.HACKER_NEWS],
        "search_terms": "Hello search term",
        "post_evaluation_prompt": "Test",
        "response_evaluation_prompt": "Test",
        "prompt_templates": [
            {
                "id": campaign_prompt_templates[0].id,
                "campaign_id": campaign.id,
                "template": "hello1",
            },
            {
                "id": campaign_prompt_templates[1].id,
                "campaign_id": campaign.id,
                "template": "hello2",
            },
            {
                "id": campaign_prompt_templates[2].id,
                "campaign_id": campaign.id,
                "template": "hello3",
            },
        ],
    }
    assert campaign_prompt_templates.count() == 3
