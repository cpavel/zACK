from campaigns.models import Campaign
from django.utils import timezone
import pytz


def update_campaign_run_status(campaign: Campaign, status: str):
    tz_est = pytz.timezone('EST')
    current_time = timezone.now().astimezone(tz_est)
    formatted_time = current_time.strftime('%b %d, %I:%M%p')

    campaign.run_status = f"[{formatted_time}] {status}"
    campaign.save()
