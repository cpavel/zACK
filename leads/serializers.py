from rest_framework.serializers import (
    CharField,
    DateTimeField,
    IntegerField,
    Serializer,
    PrimaryKeyRelatedField,
)
from leads.models import Lead
from campaigns.models import Campaign


class SearchTermSerializer(Serializer):
    id = IntegerField(read_only=True)

    term = CharField(max_length=200)

    created_at = DateTimeField(read_only=True)
    updated_at = DateTimeField(read_only=True)


class LeadSerializer(Serializer):
    id = IntegerField(read_only=True)
    campaign = PrimaryKeyRelatedField(queryset=Campaign.objects.all(), required=False)

    class Meta:
        model = Lead
        fields = [
            "id",
            "campaign",
            "location",
            "username",
            "profile_about",
            "profile_url",
            "comment",
            "comment_url",
            "prompt_response_text",
            "evaluate_response_text",
            "post_evaluate_response_text",
            "post_score",
            "score",
        ]

    def create(self, validated_data):
        campaign = validated_data.pop("campaign", None)
        lead = Lead.objects.create(campaign=campaign, **validated_data)
        return lead

    def update(self, instance, validated_data):
        campaign = validated_data.pop("campaign", None)
        for field, value in validated_data.items():
            setattr(instance, field, value)
        if campaign is not None:
            instance.campaign = campaign
        instance.save()
        return instance
