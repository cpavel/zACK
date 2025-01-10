import pytest
from django.core.exceptions import ValidationError

from data.models import PromptTemplate


def test_prompt_template_profile_length_signal():
    current_count = PromptTemplate.objects.count()

    # Test standard behaviour.
    _ = PromptTemplate.objects.create(
        template="Simple template.",
        min_profile_length=1,
        max_profile_length=20,
    )

    current_count += 1
    assert current_count == PromptTemplate.objects.count()

    # Test standard empty profile behaviour.
    _ = PromptTemplate.objects.create(
        template="Simple template.",
        min_profile_length=None,
        max_profile_length=None,
    )

    current_count += 1
    assert current_count == PromptTemplate.objects.count()

    # Test incorrect min greater than max.
    with pytest.raises(ValidationError) as exc_info:
        PromptTemplate.objects.create(
            template="Simple template.",
            min_profile_length=100,
            max_profile_length=2,
        )

    assert "min_profile_length must be a larger value" in str(exc_info.value)

    # No increase.
    assert current_count == PromptTemplate.objects.count()

    # Test incorrect min not set when max is set.
    with pytest.raises(ValidationError) as exc_info:
        PromptTemplate.objects.create(
            template="Simple template.",
            min_profile_length=None,
            max_profile_length=2,
        )

    assert "min_profile_length must not be None" in str(exc_info.value)
