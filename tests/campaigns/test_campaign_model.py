from campaigns.models import Campaign


def test_campaign_relations(baker):
    user = baker.make("auth.User")
    campaign = Campaign.objects.create(user=user)
    prompt_template1 = baker.make("data.PromptTemplate", campaign=campaign)
    prompt_template2 = baker.make("data.PromptTemplate", campaign=campaign)
    prompt_template3 = baker.make("data.PromptTemplate", campaign=campaign)

    assert campaign.user == user
    assert user.campaigns.first() == campaign
    assert campaign.prompt_templates.count() == 3
    assert list(campaign.prompt_templates.all()) == [
        prompt_template1,
        prompt_template2,
        prompt_template3,
    ]
