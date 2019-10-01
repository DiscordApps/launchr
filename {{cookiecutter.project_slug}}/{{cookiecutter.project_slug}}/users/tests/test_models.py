import pytest
from django.conf import settings
from datetime import timedelta
from django.core.exceptions import ImproperlyConfigured

pytestmark = pytest.mark.django_db


def test_get_avatar_url(user: settings.AUTH_USER_MODEL):
    user.email = "foo@bar.com"
    assert user.get_avatar_url() == "https://www.gravatar.com/avatar/f3ada405ce890b6f8204094deb12d8a8?d=mp&s=400x400"


def test_get_cancel_url(user: settings.AUTH_USER_MODEL):
    assert user.get_cancel_url() is None

    user.vendor = 'paddle'
    user.vendor_extra = {"cancel_url": "https://cancel_url"}
    assert user.get_cancel_url() == "https://cancel_url"


def test_get_payment_update_url(user: settings.AUTH_USER_MODEL):
    assert user.get_payment_update_url() is None

    user.vendor = 'paddle'
    user.vendor_extra = {"update_url": "https://update_url"}
    assert user.get_payment_update_url() == "https://update_url"


def test_is_paddle_customer(user: settings.AUTH_USER_MODEL):
    assert user.is_paddle_customer == False

    user.vendor = 'paddle'
    assert user.is_paddle_customer == True


def test_subscription_status(user: settings.AUTH_USER_MODEL):
    settings.SAAS_TRIAL_LENGTH = timedelta(days=14)
    user.vendor = "paddle"
    user.vendor_subscription_status = 'deleted'
    assert user.subscription_status == "cancelled"

    user.vendor_subscription_status = 'active'
    assert user.subscription_status == 'active'

    user.vendor = None
    user.vendor_subscription_status = None
    settings.SAAS_SUBSCRIPTION_TYPE = "freemium"
    assert user.subscription_status == 'active'

    settings.SAAS_SUBSCRIPTION_TYPE = 'trial'
    assert user.subscription_status == "trial"

    settings.SAAS_SUBSCRIPTION_TYPE = None
    assert user.subscription_status is None

    settings.SAAS_SUBSCRIPTION_TYPE = 'trial'
    user.date_joined = user.date_joined - settings.SAAS_TRIAL_LENGTH - timedelta(days=1)
    assert user.subscription_status is None


def test_has_active_subscription(user: settings.AUTH_USER_MODEL):
    user.vendor = 'paddle'
    user.vendor_subscription_status = 'active'
    assert user.has_active_subscription == True

    user.vendor_subscription_status = 'cancelled'
    assert user.has_active_subscription == False


def test_has_cancelled_subscription(user: settings.AUTH_USER_MODEL):
    user.vendor = 'paddle'
    user.vendor_subscription_status = 'deleted'
    assert user.has_cancelled_subscription == True

    user.vendor_subscription_status = 'cancelled'
    assert user.has_cancelled_subscription == True

    user.vendor_subscription_status = 'active'
    assert user.has_cancelled_subscription == False


def test_get_absolute_url(user: settings.AUTH_USER_MODEL):
    assert user.get_absolute_url() == '/app/users/'


def test_str(user: settings.AUTH_USER_MODEL):
    assert user.__str__() == user.email


def test_has_freemium_subscription(user: settings.AUTH_USER_MODEL, settings):
    settings.SAAS_SUBSCRIPTION_TYPE = "freemium"
    assert user.has_freemium_subscription == True

    user.plan_id = "abcde"
    assert user.has_freemium_subscription == False

    user.plan_id = None
    settings.SAAS_SUBSCRIPTION_TYPE = "trial"
    assert user.has_freemium_subscription == False


def test_has_trialling_subscription(user: settings.AUTH_USER_MODEL, settings):
    settings.SAAS_SUBSCRIPTION_TYPE = "trial"
    settings.SAAS_TRIAL_LENGTH = timedelta(days=14)
    assert user.has_trialling_subscription == True

    user.plan_id = "abcde"
    assert user.has_trialling_subscription == False

    user.plan_id = None
    user.date_joined = user.date_joined - settings.SAAS_TRIAL_LENGTH - timedelta(days=1)
    assert user.has_trialling_subscription == False


def test_has_no_subscription(user: settings.AUTH_USER_MODEL, settings):
    settings.SAAS_TRIAL_LENGTH = timedelta(days=14)
    settings.SAAS_SUBSCRIPTION_TYPE = "None"
    assert user.has_no_subscription == True

    user.plan_id = "abcd"
    assert user.has_no_subscription == False

    user.plan_id = None
    settings.SAAS_SUBSCRIPTION_TYPE = None
    assert user.has_no_subscription == True

    user.plan_id = "abcd"
    assert user.has_no_subscription == False

    user.plan_id = None
    settings.SAAS_SUBSCRIPTION_TYPE = 'trial'
    assert user.has_no_subscription == False

    user.plan_id = "abcd"
    assert user.has_no_subscription == False

    user.plan_id = None
    user.date_joined = user.date_joined - settings.SAAS_TRIAL_LENGTH - timedelta(days=1)
    assert user.has_no_subscription == True


def test_trial_ends_at(user: settings.AUTH_USER_MODEL, settings):
    settings.SAAS_SUBSCRIPTION_TYPE = 'trial'
    settings.SAAS_TRIAL_LENGTH = timedelta(days=14)
    assert user.trial_ends_at == user.date_joined + timedelta(days=14)

    with pytest.raises(ImproperlyConfigured):
        settings.SAAS_SUBSCRIPTION_TYPE = None
        user.trial_ends_at


def test_is_trial_active(user: settings.AUTH_USER_MODEL):
    settings.SAAS_TRIAL_LENGTH = timedelta(days=14)
    assert user.is_trial_active == True

    user.date_joined = user.date_joined - settings.SAAS_TRIAL_LENGTH - timedelta(days=1)
    assert user.is_trial_active == False


def test_has_paid_subscription(user: settings.AUTH_USER_MODEL):
    assert user.has_paid_subscription == False

    user.vendor_subscription_id = "abcd"
    assert user.has_paid_subscription == True


def test_plan(user: settings.AUTH_USER_MODEL, settings):
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

    assert user.plan == settings.SAAS_PLANS[0]

    user.plan_id = "starter_plan_id"
    assert user.plan == settings.SAAS_PLANS[1]

    user.plan_id = "pro_plan_id"
    assert user.plan == settings.SAAS_PLANS[2]
