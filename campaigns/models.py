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
    RUN_STATUS_CHOICES = [
        ('do_not_run', 'Do Not Run'),
        ('run', 'Run'),
    ]
    run_status = CharField(
        max_length=20,
        choices=RUN_STATUS_CHOICES,
        default='do_not_run',
    )

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
