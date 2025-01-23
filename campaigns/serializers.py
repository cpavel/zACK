import logging

from data.serializers import PromptTemplateSerializer
from campaigns.models import Campaign
from data.models import PromptTemplate
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class CampaignSerializer(serializers.ModelSerializer):
    prompt_templates = PromptTemplateSerializer(many=True, required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    campaign = serializers.PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False)

    class Meta:
        model = Campaign
        fields = [
            "id",
            "user",
            "name",
            "locations",
            "search_terms",
            "twitter_search_terms",
            "post_evaluation_prompt",
            "response_evaluation_prompt",
            "prompt_templates",
            "campaign",
        ]

    def save(self):
        with transaction.atomic(using="default"):
            campaign = super().save()

        logger.info(
            "Created Campaign %s for User %s",
            campaign.pk,
            campaign.user_id,
        )
        return campaign

    def create(self, validated_data):
        prompt_templates_data = validated_data.pop("prompt_templates", [])
        campaign = Campaign.objects.create(**validated_data)

        for prompt_template_data in prompt_templates_data:
            PromptTemplate.objects.create(
                campaign=campaign, **prompt_template_data
            )

        return campaign

    def update(self, instance, validated_data):
        prompt_templates_data = validated_data.pop("prompt_templates", [])

        # Delete old PromptTemplates and create new ones
        with transaction.atomic():
            PromptTemplate.objects.filter(campaign=instance).delete()

            for prompt_template_data in prompt_templates_data:
                PromptTemplate.objects.create(
                    campaign=instance, **prompt_template_data
                )

        # Update parent Campaign
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance
