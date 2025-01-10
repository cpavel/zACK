import pytest
from django.urls import reverse
from ack import enums
from data.models import PromptTemplate
from campaigns.models import Campaign


@pytest.fixture
def campaign_data(baker):
    user = baker.make("auth.User")

    return {
        "user": user.pk,
        "name": "My Campaign",
        "locations": [enums.SearchLocation.TWITTER],
        "search_terms": "Hello hello hello I am a search term",
        "post_evaluation_prompt": "Hello this is an evaluation prompt",
        "response_evaluation_prompt": (
            "Hello I am a response evaluation prompt"
        ),
    }


@pytest.fixture
def create_campaign_request(api_client):
    def _make_request(data):
        return api_client.post("/campaigns/create", data)

    return _make_request


@pytest.fixture
def create_url():
    return reverse("campaigns:create_campaign")


def test_create_url(create_url):
    assert create_url == "/campaigns/create"


def test_create_base_campaign(create_campaign_request, campaign_data):
    response = create_campaign_request(campaign_data)
    campaign = Campaign.objects.first()

    assert response.status_code == 201
    assert campaign.name == "My Campaign"
    assert campaign.locations == [enums.SearchLocation.TWITTER]
    assert campaign.search_terms == "Hello hello hello I am a search term"
    assert (
        campaign.post_evaluation_prompt == "Hello this is an evaluation prompt"
    )
    assert (
        campaign.response_evaluation_prompt
        == "Hello I am a response evaluation prompt"
    )


def test_create_campaign_with_user_id(
    baker, create_campaign_request, campaign_data
):
    user = baker.make("auth.User")
    campaign_data["user"] = user.pk
    response = create_campaign_request(campaign_data)
    campaign = Campaign.objects.first()

    assert response.status_code == 201
    assert campaign.name == "My Campaign"
    assert campaign.locations == [enums.SearchLocation.TWITTER]
    assert campaign.search_terms == "Hello hello hello I am a search term"
    assert (
        campaign.post_evaluation_prompt == "Hello this is an evaluation prompt"
    )
    assert (
        campaign.response_evaluation_prompt
        == "Hello I am a response evaluation prompt"
    )
    assert campaign.user_id == user.pk


def test_create_campaign_with_prompt_template(
    create_campaign_request, campaign_data
):
    data = campaign_data
    data["prompt_templates"] = [{"template": "hello"}]
    response = create_campaign_request(campaign_data)
    campaign = Campaign.objects.first()
    prompt_templates = PromptTemplate.objects.all()

    print(response.json())
    assert response.status_code == 201
    assert campaign.name == "My Campaign"
    assert campaign.locations == [enums.SearchLocation.TWITTER]
    assert campaign.search_terms == "Hello hello hello I am a search term"
    assert (
        campaign.post_evaluation_prompt == "Hello this is an evaluation prompt"
    )
    assert (
        campaign.response_evaluation_prompt
        == "Hello I am a response evaluation prompt"
    )
    assert prompt_templates.count() == 1
    prompt_template = prompt_templates.first()
    assert prompt_template.template == "hello"
    assert prompt_template.campaign_id == campaign.id


def test_create_campaign_with_multiple_prompt_template(
    create_campaign_request, campaign_data
):
    data = campaign_data
    data["prompt_templates"] = [
        {"template": "hello1"},
        {"template": "hello2"},
        {"template": "hello3"},
    ]
    response = create_campaign_request(campaign_data)
    campaign = Campaign.objects.first()
    prompt_templates = PromptTemplate.objects.all()

    print(response.json())
    assert response.status_code == 201
    assert campaign.name == "My Campaign"
    assert campaign.locations == [enums.SearchLocation.TWITTER]
    assert campaign.search_terms == "Hello hello hello I am a search term"
    assert (
        campaign.post_evaluation_prompt == "Hello this is an evaluation prompt"
    )
    assert (
        campaign.response_evaluation_prompt
        == "Hello I am a response evaluation prompt"
    )
    assert prompt_templates.count() == 3
    for index, pt in enumerate(prompt_templates):
        assert pt.template == f"hello{index+1}"
        assert pt.campaign_id == campaign.id
