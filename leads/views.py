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
