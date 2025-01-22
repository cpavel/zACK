import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    class _APIClient(APIClient):
        def generic(
            self,
            method,
            path,
            data="",
            content_type="application/octet-stream",
            secure=True,
            **extra,
        ):
            return super().generic(
                method, path, data, content_type, secure, **extra
            )

    return _APIClient(HTTP_HOST="api.zack.test", secure=True)


pytest_plugins = ["tests.fixtures"]
