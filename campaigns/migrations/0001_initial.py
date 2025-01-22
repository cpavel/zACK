# Generated by Django 4.2.1 on 2023-07-28 16:28

import zACK.enums
import zACK.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.TextField(default="", max_length=200)),
                (
                    "run_status",
                    models.TextField(blank=True, max_length=200, null=True),
                ),
                (
                    "locations",
                    zACK.fields.ChoiceArrayField(
                        base_field=models.IntegerField(
                            choices=[(1, "Hacker News"), (2, "Twitter")]
                        ),
                        blank=True,
                        default=zACK.enums.get_default_search_locations,
                        help_text=(
                            "Locations to perform search and sentiment"
                            " analysis."
                        ),
                        size=None,
                    ),
                ),
                (
                    "search_terms",
                    models.TextField(
                        help_text=(
                            "Terms to use for searching posts and comments."
                        ),
                        max_length=200,
                    ),
                ),
                (
                    "post_evaluation_prompt",
                    models.TextField(
                        help_text="Prompt to evaluate initial searched post.",
                        max_length=5000,
                    ),
                ),
                (
                    "response_evaluation_prompt",
                    models.TextField(
                        help_text="Prompt to evaluate built response.",
                        max_length=5000,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        db_constraint=False,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="campaigns",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["user"], name="campaigns_c_user_id_c9c0d8_idx"
                    ),
                    models.Index(
                        fields=["created_at"],
                        name="campaigns_c_created_eda2da_idx",
                    ),
                ],
            },
        ),
    ]
