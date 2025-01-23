from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import (
    CASCADE,
    SET_NULL,
    BigAutoField,
    BooleanField,
    DateTimeField,
    ForeignKey,
    IntegerField,
    ManyToManyField,
    Model,
    PositiveIntegerField,
    TextField,
)
from campaigns.models import Campaign
from zACK import enums

from .validators import prompt_template_profile_length_validation


class SearchTerm(Model):
    id = BigAutoField(primary_key=True)

    user = ForeignKey(
        User,
        related_name="search_terms",
        db_constraint=False,
        on_delete=CASCADE,
        default=None,
        null=True,
    )
    term = TextField(max_length=200, null=False, blank=False)
    location = IntegerField(
        choices=enums.SearchLocation.choices,
        default=enums.SearchLocation.HACKER_NEWS,
        null=False,
    )

    run_status = TextField(max_length=200, null=True, blank=True)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class EvaluationTemplate(Model):
    id = BigAutoField(primary_key=True)

    template = TextField(max_length=5000, null=False, blank=False)

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class PromptTemplate(Model):
    def save(self, *args, **kwargs):
        self.run_multi_field_validation()
        super(PromptTemplate, self).save(*args, **kwargs)

    id = BigAutoField(primary_key=True)

    campaign = ForeignKey(
        Campaign,
        on_delete=CASCADE,
        default=None,
        null=True,
        related_name="prompt_templates",
    )

    # TODO: Remove once Campaign is finalized
    search_terms = ManyToManyField(
        SearchTerm,
        db_constraint=False,
        related_name="prompt_templates",
    )

    # TODO: Remove once Campaign is finalized
    # If null, prompt response is always considerable.
    evaluation_template = ForeignKey(
        EvaluationTemplate,
        related_name="prompt_templates",
        db_constraint=False,
        on_delete=SET_NULL,
        default=None,
        null=True,
    )

    template = TextField(max_length=5000, null=False, blank=False)

    # Validation:
    # If max_profile_length is set, min_profile_length must be
    # set and min_profile_length must not be larger.
    #
    # Use:
    # If min_profile_length is not set, then the profile
    # information will not be used, but the template will, even
    # if there is extensive information in the profile. Use a
    # low max_profile_length to disclude a template if this is
    # sub-optimal for a given template.
    #
    # If it is set, however, then the template will not be
    # used, so if a user that cares about comments even from
    # profiles that have no meaningful data, they should always
    # set a fallback prompt template where min_profile_length
    # is set to None.
    min_profile_length = PositiveIntegerField(
        default=None,
        null=True,
    )

    max_profile_length = PositiveIntegerField(
        default=None,
        null=True,
    )

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def run_multi_field_validation(self):
        prompt_template_profile_length_validation(self)


# TODO: Create 60 day or similar cleanup job for these.
# TODO: Link to search term since templates are many to many.
# TODO: Add score, different than rating since it is human given.
class PromptResponse(Model):
    id = BigAutoField(primary_key=True)

    prompt_template = ForeignKey(
        User,
        related_name="prompt_responses",
        on_delete=SET_NULL,
        db_constraint=False,
        default=None,
        null=True,
    )

    # If null, there was an error connecting to ChatGPT.
    response = TextField(blank=False, null=True)

    # Is always true if there is no evaluation template, unless
    # there was an error generating a response.
    is_considerable = BooleanField(null=False)
    score = IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(100),
        ],
        default=None,
        null=False,
    )

    rating = IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ],
        default=None,
        null=True,
    )

    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


class Campaign(Model):
    name = TextField(max_length=255)
    description = TextField(blank=True, null=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
