from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework.authtoken import views

from ui import views as ui_views

admin.site.site_header = "ACK Admin"

urlpatterns = [
    path("", ui_views.index),
    path("admin/", admin.site.urls),
    path("leads/", include("leads.urls")),
    path("campaigns/", include("campaigns.urls", namespace="campaigns")),
    path("api_auth/", views.obtain_auth_token, name="api_auth"),
    path("__reload__/", include("django_browser_reload.urls")),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
