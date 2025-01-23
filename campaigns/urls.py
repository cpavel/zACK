from django.urls import path

from .views import (
    CreateCampaignAPIView,
    RetrieveCampaignAPIView,
    UpdateCampaignAPIView,
    DeleteCampaignAPIView,
    StartCampaignAPIView,
    StopCampaignAPIView,
)

app_name = "campaigns"

urlpatterns = [
    path("create", CreateCampaignAPIView.as_view(), name="create_campaign"),
    path("get/<id>", RetrieveCampaignAPIView.as_view(), name="get_campaign"),
    path(
        "update/<id>", UpdateCampaignAPIView.as_view(), name="update_campaign"
    ),
    path(
        "delete/<id>", DeleteCampaignAPIView.as_view(), name="delete_campaign"
    ),
    path("start/<id>", StartCampaignAPIView.as_view(), name="start_campaign"),
    path("stop/<id>", StopCampaignAPIView.as_view(), name="stop_campaign"),
]
