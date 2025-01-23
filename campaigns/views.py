import logging

from campaigns.serializers import CampaignSerializer
from campaigns.models import Campaign
from campaigns.tasks import start_campaign
from campaigns.utils import update_campaign_run_status
from rest_framework import exceptions, generics, status, views
from rest_framework.response import Response


logger = logging.getLogger(__name__)


class CreateCampaignAPIView(generics.CreateAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer

    def handle_exception(self, exc):
        if isinstance(exc, exceptions.ValidationError):
            if "id" in self.request.data:
                logger.warning(
                    "Could not create Campaign with id -- %s",
                    self.request.data["id"],
                )
        return super().handle_exception(exc)

    def perform_create(self, serializer):
        serializer.save(campaign=self.request.data.get('campaign'))
        super().perform_create(serializer)


class RetrieveCampaignAPIView(generics.RetrieveAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    lookup_field = "id"


class UpdateCampaignAPIView(generics.UpdateAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DeleteCampaignAPIView(generics.DestroyAPIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    lookup_field = "id"

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class StartCampaignAPIView(views.APIView):
    queryset = Campaign.objects.all()
    serializer_class = CampaignSerializer
    lookup_field = "id"

    def post(self, request, id):
        try:
            campaign = Campaign.objects.get(id=id)
        except Campaign.DoesNotExist:
            return Response(
                {"error": f"Campaign {id} not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        update_campaign_run_status(campaign, "Queued")
        start_campaign.delay(campaign.pk)

        return Response(
            {"message": "Campaign started."}, status=status.HTTP_200_OK
        )
