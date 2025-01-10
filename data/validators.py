from django.core.exceptions import ValidationError


def prompt_template_profile_length_validation(instance):
    if instance.max_profile_length is None:
        return

    if instance.min_profile_length is None:
        raise ValidationError(
            "max_profile_length is set so min_profile_length must not be None."
        )

    if instance.max_profile_length < instance.min_profile_length:
        raise ValidationError(
            f"max_profile_length is set to {instance.max_profile_length} so"
            " min_profile_length must be a larger value instead of"
            f" {instance.min_profile_length}"
        )
