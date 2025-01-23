import logging
from campaigns.models import Campaign

from campaigns.actions import find_leads
from campaigns.utils import update_campaign_run_status
from zACK.celery import app

logger = logging.getLogger(__name__)


@app.task
def start_campaign(campaign_id):
    try:
        campaign = Campaign.objects.get(id=campaign_id)
    except Campaign.DoesNotExist:
        logger.info(f"Couldn't find Campaign {campaign_id} during start task.")
        update_campaign_run_status(f"Could not find Campaign with id: {campaign_id}")
        return

    find_leads(campaign=campaign)


def start_campaign_if_needed(campaign):
    if campaign.run_status == 'run':
        # Logic to start the campaign
        start_campaign.delay(campaign.id)  # Assuming start_campaign is a Celery task
