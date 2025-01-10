import pytest
from django.urls import reverse
from ack import enums
from campaigns.models import Campaign
from data.models import PromptTemplate


@pytest.fixture
def get_campaign_request(api_client):
    def _make_request(id):
        return api_client.delete(f"/campaigns/delete/{id}")

    return _make_request


@pytest.fixture
def delete_url():
    return reverse("campaigns:delete_campaign", args=(1,))


def test_delete_url(delete_url):
    assert delete_url == "/campaigns/delete/1"


def test_delete_campaign_by_id(baker, get_campaign_request):
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

    assert response.status_code == 204
    assert not Campaign.objects.filter(id=campaign.pk).exists()


def test_delete_campaign_by_id_only_deletes_that_campaign(
    baker, get_campaign_request
):
    user = baker.make(
        "auth.User",
        id=1,
    )
    campaign = baker.make(
        "campaigns.Campaign",
        user=user,
        name="Hello",
        locations=[enums.SearchLocation.HACKER_NEWS],
        search_terms="Hello search term",
        post_evaluation_prompt="Test",
        response_evaluation_prompt="Test",
    )
    other_campaign = baker.make(
        "campaigns.Campaign",
        user=user,
        name="Other",
        locations=[enums.SearchLocation.HACKER_NEWS],
        search_terms="Hello search term2",
        post_evaluation_prompt="Test2",
        response_evaluation_prompt="Test2",
    )
    response = get_campaign_request(campaign.pk)

    assert response.status_code == 204
    assert not Campaign.objects.filter(id=campaign.pk).exists()
    assert Campaign.objects.filter(id=other_campaign.pk).exists()


def test_delete_campaign_by_id_with_prompt_templates(
    baker, get_campaign_request
):
    user = baker.make(
        "auth.User",
        id=1,
    )
    campaign = baker.make(
        "campaigns.Campaign",
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

    assert response.status_code == 204
    assert not Campaign.objects.filter(id=campaign.pk).exists()
    assert not PromptTemplate.objects.filter(
        id__in=[prompt_template1.pk, prompt_template2.pk]
    ).exists()
