import pytest
from django.conf import settings
from django.urls import reverse, resolve

pytestmark = pytest.mark.django_db

def test_update():
    assert reverse("app:users:update") == "/app/users/~update/"
    assert resolve("/app/users/~update/").view_name == "app:users:update"
