import logging

from data.models import PromptTemplate
from rest_framework import serializers

logger = logging.getLogger(__name__)


class PromptTemplateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        required=False
    )  # Allow id field during update

    class Meta:
        model = PromptTemplate
        fields = [
            "id",
            "campaign_id",
            "template",
        ]
