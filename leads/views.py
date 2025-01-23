from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ModelViewSet

from data.models import SearchTerm

from .serializers import SearchTermSerializer


class SearchTermListView(ModelViewSet):
    queryset = SearchTerm.objects.all()
    serializer_class = SearchTermSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        queryset = super().get_queryset()
        campaign = self.request.query_params.get('campaign', None)
        if campaign is not None:
            queryset = queryset.filter(campaign=campaign)
        return queryset
