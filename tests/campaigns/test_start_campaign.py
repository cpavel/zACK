import pytest
from unittest.mock import patch
from django.urls import reverse
from ack import enums
from leads.models import Lead
from campaigns.models import Campaign
from campaigns.actions import find_leads


@pytest.fixture
def mock_start_campaign():
    with patch("campaigns.views.start_campaign") as mock:
        yield mock.delay


@pytest.fixture
def start_campaign_request(api_client):
    def _make_request(id):
        return api_client.post(f"/campaigns/start/{id}")

    return _make_request


@pytest.fixture
def start_url():
    return reverse("campaigns:start_campaign", args=(1,))


def test_start_url(start_url):
    assert start_url == "/campaigns/start/1"


def test_start_campaign_creates_celery_task(
    baker,
    start_campaign_request,
    mock_start_campaign,
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

    response = start_campaign_request(campaign.pk)

    campaign.refresh_from_db()

    assert response.status_code == 200
    assert "Queued" in campaign.run_status
    mock_start_campaign.assert_called_once_with(campaign.pk)

# TODO: Ideally Hacker News API result is mocked
def test_find_leads_no_hackernews_hits(
    baker,
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
        search_terms="AJNSDKFNASDKFNASKGAKSDFNKASFAJS",
        post_evaluation_prompt="Test",
        response_evaluation_prompt="Test",
    )

    find_leads(campaign)

    campaign.refresh_from_db()

    assert "Finished" in campaign.run_status
    assert Lead.objects.count() == 0


def test_find_leads_has_hackernews_hits(
    baker,
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
        search_terms="Django",
        post_evaluation_prompt="Test",
        response_evaluation_prompt="Test",
    )
    _ = baker.make(
        "data.PromptTemplate", campaign=campaign, template="Hey! This is TJ"
    )
    _ = baker.make(
        "data.PromptTemplate", campaign=campaign, template="Hi there, TJ here."
    )

    find_leads(campaign)

    campaign.refresh_from_db()

    assert "Finished" in campaign.run_status
    assert Lead.objects.count() == 1
    lead = Lead.objects.first()
    assert lead.campaign == campaign
    assert 1 <= lead.post_score <= 100
    assert 1 <= lead.score <= 100
