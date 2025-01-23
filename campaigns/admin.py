from django.contrib import admin
from .models import Campaign
import os
from django.urls import path, reverse
from django.utils.html import format_html
from django.http import HttpResponse

def start_campaign(modeladmin, request, queryset):
    for campaign in queryset:
        if os.getenv('IS_DEV') == 'true':
            # Execute search and response generation locally
            campaign.is_running = True
            campaign.save()
            # Add logic to start the campaign's search and response generation

def stop_campaign(modeladmin, request, queryset):
    for campaign in queryset:
        campaign.is_running = False
        campaign.save()

start_campaign.short_description = "Start selected campaigns"
stop_campaign.short_description = "Stop selected campaigns"

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    actions = [start_campaign, stop_campaign]
    search_fields = ('name', 'search_terms')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                r"<path:object_id>/start-campaign/",
                self.admin_site.admin_view(lambda request, object_id: start_campaign(self, request, Campaign.objects.filter(pk=object_id))),
                name="start-campaign",
            ),
            path(
                r"<path:object_id>/stop-campaign/",
                self.admin_site.admin_view(lambda request, object_id: stop_campaign(self, request, Campaign.objects.filter(pk=object_id))),
                name="stop-campaign",
            ),
            path(
                r"<path:object_id>/view-campaign-logs/",
                self.admin_site.admin_view(self.view_campaign_logs),
                name="view-campaign-logs",
            ),
        ]
        return custom_urls + urls

    def record_actions(self, obj):
        return format_html(
            (
                '<a class="button" href="{}">Start</a>&nbsp;<a class="button"'
                ' href="{}">Stop</a>&nbsp;<a class="button"'
                ' href="{}">View Logs</a>'
            ),
            reverse("admin:start-campaign", args=[obj.pk]),
            reverse("admin:stop-campaign", args=[obj.pk]),
            reverse("admin:view-campaign-logs", args=[obj.pk]),
        )

    def view_campaign_logs(self, request, object_id, *args, **kwargs):
        log_file_path = f"/opt/zACK/logs/campaign-{object_id}.log"

        try:
            with open(log_file_path, "r") as file:
                file_content = file.read()
        except FileNotFoundError:
            file_content = "No logs found"

        return HttpResponse(file_content, content_type="text/plain")

    record_actions.short_description = "Start | Stop | View Logs"
    record_actions.allow_tags = True

# Check if the Campaign model is already registered
if not admin.site.is_registered(Campaign):
    admin.site.register(Campaign, CampaignAdmin)
