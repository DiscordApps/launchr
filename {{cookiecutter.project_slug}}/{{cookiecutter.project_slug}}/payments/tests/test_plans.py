import pytest
from django.conf import settings
from {{ cookiecutter.project_slug }}.payments.plan import plan_by_id

pytestmark = pytest.mark.django_db

def test_plan_by_id(user: settings.AUTH_USER_MODEL, settings):
    settings.SAAS_PLANS = [
        {
            "name": "free",
            "price": "free",
            "default": True,
            "display": True,
            "subscribable": False,
            "plan_id": None,
            "description": "Free Plan Description",
            "features": []
        },
        {
            "name": "Starter",
            "price": "19€",
            "default": False,
            "display": True,
            "subscribable": True,
            "plan_id": "starter_plan_id",
            "description": "Starter Plan Description",
            "features": []
        },
        {
            "name": "Pro",
            "price": "49€",
            "default": False,
            "display": True,
            "subscribable": True,
            "plan_id": "pro_plan_id",
            "description": "Pro Plan Description",
            "features": []
        }
    ]

    assert plan_by_id(None) == settings.SAAS_PLANS[0]
    assert plan_by_id("starter_plan_id") == settings.SAAS_PLANS[1]
    assert plan_by_id("pro_plan_id") == settings.SAAS_PLANS[2]
    assert plan_by_id("foo") is None
