from django.contrib import admin
from .models import Campaign

def start_campaign(modeladmin, request, queryset):
    for campaign in queryset:
        campaign.is_running = True
        campaign.save()

def stop_campaign(modeladmin, request, queryset):
    for campaign in queryset:
        campaign.is_running = False
        campaign.save()

start_campaign.short_description = "Start selected campaigns"
stop_campaign.short_description = "Stop selected campaigns"

class CampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at', 'is_running')
    actions = [start_campaign, stop_campaign]
    search_fields = ('name', 'search_terms')

# Check if the Campaign model is already registered
if not admin.site.is_registered(Campaign):
    admin.site.register(Campaign, CampaignAdmin)
