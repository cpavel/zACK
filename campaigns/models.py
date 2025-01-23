from django.contrib.auth.models import User
from django.db.models import (
    PROTECT,
    BigAutoField,
    TextField,
    IntegerField,
    ForeignKey,
    Index,
    UniqueConstraint,
    CharField,
    BooleanField,
)
from zACK import enums
from zACK.mixins import TimeStampMixin
from zACK.fields import ChoiceArrayField


class Campaign(TimeStampMixin):
    id = BigAutoField(primary_key=True)

    # General Information
    name = TextField(null=False, blank=False, default="", max_length=200)
    user = ForeignKey(
        User,
        related_name="campaigns",
        db_constraint=False,
        on_delete=PROTECT,
        default=None,
        null=True,
    )
    is_running = BooleanField(default=False)

    # Search Configurations
    locations = ChoiceArrayField(
        base_field=IntegerField(choices=enums.SearchLocation.choices),
        default=enums.get_default_search_locations,
        blank=True,
        help_text="Locations to perform search and sentiment analysis.",
    )
    search_terms = TextField(
        max_length=200,
        null=False,
        blank=False,
        help_text="Terms to use for searching posts and comments.",
    )
    twitter_search_terms = TextField(
        max_length=200,
        null=True,
        blank=True,
        help_text="Terms to use for searching Twitter posts.",
    )
    post_evaluation_prompt = TextField(
        max_length=5000,
        null=False,
        blank=False,
        help_text="Prompt to evaluate initial searched post.",
    )
    response_evaluation_prompt = TextField(
        max_length=5000,
        null=False,
        blank=False,
        help_text="Prompt to evaluate built response.",
    )

    class Meta:
        indexes = [
            Index(fields=["user"]),
            Index(fields=["created_at"]),
        ]
        constraints = [
            UniqueConstraint(
                fields=["user", "name"],
                name="unique_campaign_name_per_user",
            ),
        ]


class CampaignLeadSearchResult:
    def __init__(self, campaign, location, username, profile_about, profile_url, comment, comment_url):
        self.campaign = campaign
        self.location = location
        self.username = username
        self.profile_about = profile_about
        self.profile_url = profile_url
        self.comment = comment
        self.comment_url = comment_url
        self.post_evaluate_request_text = None
        self.post_evaluate_response_text = None
        self.post_score = None
        self.prompt_template = None
        self.prompt_request_text = None
        self.prompt_response_text = None
        self.evaluate_request_text = None
        self.evaluate_response_text = None
        self.score = None
