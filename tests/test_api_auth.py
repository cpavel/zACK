from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token


def test_api_auth(client):
    assert Token.objects.count() == 0
    user = User.objects.create_user(username="bob", password="testpass")
    url = reverse("api_auth")
    response = client.post(url, {"username": "bob", "password": "testpass"})

    assert response.status_code == status.HTTP_200_OK
    assert "token" in response.data
    token = response.data["token"]
    assert Token.objects.get(key=token).user == user
    assert Token.objects.count() == 1
