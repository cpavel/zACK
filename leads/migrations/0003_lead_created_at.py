# Generated by Django 4.2.1 on 2023-07-26 15:07

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("leads", "0002_remove_lead_prompt_response_message_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="lead",
            name="created_at",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
