from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    PROTECT,
    BigAutoField,
    TextField,
    IntegerField,
    ForeignKey,
    Index,
)
from campaigns.models import Campaign
from data.models import SearchTerm
from zACK import enums
from zACK.mixins import TimeStampMixin


class Lead(TimeStampMixin):
    id = BigAutoField(primary_key=True)

    campaign = ForeignKey(
        Campaign,
        on_delete=PROTECT,
        default=None,
        null=True,
        related_name="leads",
    )
    # TODO: Deprecate once Campaigns replace Search terms
    search_term = ForeignKey(
        SearchTerm,
        related_name="leads",
        db_constraint=False,
        on_delete=PROTECT,
        default=None,
        null=True,
    )
    location = IntegerField(
        choices=enums.SearchLocation.choices,
        default=enums.SearchLocation.HACKER_NEWS,
        null=False,
    )
    username = TextField(null=False, blank=False, default="")
    profile_about = TextField(null=False, blank=False, default="")
    profile_url = TextField(null=False, blank=False, default="")
    comment = TextField(null=False, blank=False, default="")
    comment_url = TextField(null=False, blank=False, default="")
    prompt_response_text = TextField(blank=False, null=True, default="")
    evaluate_response_text = TextField(blank=False, null=True, default="")
    post_evaluate_response_text = TextField(blank=False, null=True, default="")

    post_score = IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        default=1,
        null=False,
        help_text=(
            "Score the initial post received as to relevancy, on a scale of"
            " 1-100."
        ),
    )
    score = IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        default=1,
        null=False,
        help_text=(
            "Score the response received as to relevancy, on a scale of 1-100."
        ),
    )

    class Meta:
        indexes = [
            Index(fields=["search_term"]),
            Index(fields=["created_at"]),
        ]
