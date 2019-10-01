import pytest
from django.urls import reverse
from {{cookiecutter.project_slug}}.payments.views import(
    PaddleWebhookView, ChangePlanView
)
from datetime import datetime
from django.utils.timezone import make_aware
from django.conf import settings as django_settings
from django.test import Client
import requests_mock as mocker

pytestmark = pytest.mark.django_db

class TestPricingView:


    def test_get_unauthenticated(
        self, settings: django_settings, client: Client
    ):
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
        settings.USE_PADDLE = True
        settings.PADDLE_VENDOR_ID = "paddle_vendor_id"

        response = client.get(reverse("pricing"))
        assert response.status_code == 200
        assert 'USE_PADDLE' not in response.context
        assert 'PADDLE_VENDOR_ID' not in response.context
        assert response.context['plans'] == settings.SAAS_PLANS


    def test_get_authenticated(
        self, user: django_settings.AUTH_USER_MODEL, settings: django_settings, client: Client
    ):
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

        client.force_login(user=user)
        response = client.get(reverse("pricing"))
        assert response.status_code == 200
        assert response.context['USE_PADDLE'] == settings.USE_PADDLE
        assert response.context['PADDLE_VENDOR_ID'] == settings.PADDLE_VENDOR_ID
        assert response.context['plans'] == settings.SAAS_PLANS

class TestPaddleWebhookView:


    def test_get(self, client: Client):
        response = client.get(reverse("payments:paddle_webhook"))
        assert response.status_code == 405


    def test_post_uuid_does_not_exist(
        self, client: Client, settings
    ):
        settings.PADDLE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwuEU7R9nHgWwWy5p9ws3
iORHpFn1L8PkdzNtlZaltck5lD5qcUzmQJiW572LzO8oNFhPgPpTnrvcHfCFTLjc
MmavzroWKiKCf3fn3d7k60D5HDMy4n/+PP6hV2fVnk3Iq3uhxMK5DkKRPqynAFx/
OX20ijvuWGH3rSmmu/JjN0k7QIcMhSdpZuJ7eqtPtBSdg8uRWr8U2ZL2Wufu0xIF
pDBxEK7f+0ECq0x7GftrtvLnbTV4SMblSnN90RMocNsRoul+Ohx4unqLxprPh279
h8iqJspXhb8hKm5PuKuv9N3AXOZzckRTQSFtT/fE3FJm0CToR614r01qc+yqft0e
scTVNY95gug3aqKmjFdwLBVArdycU9+mF7WvmCDUshjot9CDHKXJCkh2Whfwr9Mq
+NN4fu6nd/OF3xaq5jZjN07EyfzYKBU1GBhg3uNfR6v4aogQhKByFwtUUyjV7UaO
yOGH9AMXwv0W/GzDvtZlPwYWUjj9OsJJASG+fYYdwvZRKrs88gTqW0nVXCLgAH3q
a8hsFHngHuJmCkllv/U9JdSiNm2j+ThIXZP+sGb7aT65eYGni7AIBZf56f+gFdCM
IczOqlDDcm8YJ1WNIHvTqg4Qa5/4GcMn69z0NGtYStPbex2AmNwulZaSqXx73qon
7GiVDmdU0t9KRSj9F3nAXVMCAwEAAQ==
    -----END PUBLIC KEY-----"""

        data = {
            'alert_id': '38713417',
            'alert_name': 'subscription_created',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?user=7&subscription=6&hash=1b1770968848660fd12777a809166d920b1d8c0d',
            'checkout_id': '8-9c4ffca208adbe5-959b2ce6a6',
            'currency': 'GBP',
            'email': 'hackett.richmond@example.com',
            'event_time': '2019-10-01 08:34:38',
            'marketing_consent': '1',
            'next_bill_date': '2019-10-28',
            'passthrough': 'adacebde-e424-11e9-a359-2a2ae2dbcce4',
            'quantity': '80',
            'status': 'active',
            'subscription_id': '1',
            'subscription_plan_id': '6',
            'unit_price': 'unit_price',
            'update_url': 'https://checkout.paddle.com/subscription/update?user=2&subscription=5&hash=1bcef50d4889c8be3b4f043768c2b7dafb935f2a',
            'user_id': '7',
            'p_signature': 'Dkee4uL9PSF/212B00LHDmDojT1ZFS0C+L+cEJ3TUZO6TYsEmNdK4cr6v/9GQjsynzZSByNXLfISP19QqHKgv1ydPPJwymzE9gMJzl6zsLegq+f3j/gDiGNCkmQ/Y3zM4OQ5CXs/pu45PG4Re6mlRvzRusOsLbv+/LVwFxsaYn7oH2C15+B69C3ZZhW6NwunJIG580I6r0x9iG6tdsZQpVrIv7mOAUW59/UykukwWwtASZImD4/uWVDJ+8bDFvczqdfF7r9tTq4soSmC7uDwKHNJYLP1g8R/TaBfaFAZtX2tQ9yyFX102mALhKxrFjwDyhiQK4wK035DVxDxjEP2VxdccidEwbAIoQEdCLjSywY6C4CG9wyWVOjniIMrSbgXL4wpHdLmGFx+ee1TZXaxbmrD44mvZw+CksfzIydHeCBHkB91QLgckat2YqTn9YPtxkCHfBnAgxYKp2yvpBtIpu5Pf/nowC2V5bRSKRHF6TR0njM3eqATucnPbe/lXml84KEvfoMd4R9DnNOo/lPZfkOBoxbWuAZWwnM8vxObcM2Pct5WJuj9Fhs9szNzk6LkQzAdtycJf396CZG0ewHt0MC0lGsdBAg3GtAJV672tdfx2JrqQHhJurz1ZccU9xdpSKDi3fa/ww7icGaJb/eHAmGNFWzj3ba27qTT6WetfmM='
        }

        # test user where uuid does not exist
        response = client.post(reverse("payments:paddle_webhook"), data)
        assert response.status_code == 404


    def test_post_uuid_exists(
        self, user: django_settings.AUTH_USER_MODEL, client: Client, django_user_model, settings
    ):
        settings.PADDLE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwuEU7R9nHgWwWy5p9ws3
iORHpFn1L8PkdzNtlZaltck5lD5qcUzmQJiW572LzO8oNFhPgPpTnrvcHfCFTLjc
MmavzroWKiKCf3fn3d7k60D5HDMy4n/+PP6hV2fVnk3Iq3uhxMK5DkKRPqynAFx/
OX20ijvuWGH3rSmmu/JjN0k7QIcMhSdpZuJ7eqtPtBSdg8uRWr8U2ZL2Wufu0xIF
pDBxEK7f+0ECq0x7GftrtvLnbTV4SMblSnN90RMocNsRoul+Ohx4unqLxprPh279
h8iqJspXhb8hKm5PuKuv9N3AXOZzckRTQSFtT/fE3FJm0CToR614r01qc+yqft0e
scTVNY95gug3aqKmjFdwLBVArdycU9+mF7WvmCDUshjot9CDHKXJCkh2Whfwr9Mq
+NN4fu6nd/OF3xaq5jZjN07EyfzYKBU1GBhg3uNfR6v4aogQhKByFwtUUyjV7UaO
yOGH9AMXwv0W/GzDvtZlPwYWUjj9OsJJASG+fYYdwvZRKrs88gTqW0nVXCLgAH3q
a8hsFHngHuJmCkllv/U9JdSiNm2j+ThIXZP+sGb7aT65eYGni7AIBZf56f+gFdCM
IczOqlDDcm8YJ1WNIHvTqg4Qa5/4GcMn69z0NGtYStPbex2AmNwulZaSqXx73qon
7GiVDmdU0t9KRSj9F3nAXVMCAwEAAQ==
    -----END PUBLIC KEY-----"""

        data = {
            'alert_id': '38713417',
            'alert_name': 'subscription_created',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?user=7&subscription=6&hash=1b1770968848660fd12777a809166d920b1d8c0d',
            'checkout_id': '8-9c4ffca208adbe5-959b2ce6a6',
            'currency': 'GBP',
            'email': 'hackett.richmond@example.com',
            'event_time': '2019-10-01 08:34:38',
            'marketing_consent': '1',
            'next_bill_date': '2019-10-28',
            'passthrough': 'adacebde-e424-11e9-a359-2a2ae2dbcce4',
            'quantity': '80',
            'status': 'active',
            'subscription_id': '1',
            'subscription_plan_id': '6',
            'unit_price': 'unit_price',
            'update_url': 'https://checkout.paddle.com/subscription/update?user=2&subscription=5&hash=1bcef50d4889c8be3b4f043768c2b7dafb935f2a',
            'user_id': '7',
            'p_signature': 'Dkee4uL9PSF/212B00LHDmDojT1ZFS0C+L+cEJ3TUZO6TYsEmNdK4cr6v/9GQjsynzZSByNXLfISP19QqHKgv1ydPPJwymzE9gMJzl6zsLegq+f3j/gDiGNCkmQ/Y3zM4OQ5CXs/pu45PG4Re6mlRvzRusOsLbv+/LVwFxsaYn7oH2C15+B69C3ZZhW6NwunJIG580I6r0x9iG6tdsZQpVrIv7mOAUW59/UykukwWwtASZImD4/uWVDJ+8bDFvczqdfF7r9tTq4soSmC7uDwKHNJYLP1g8R/TaBfaFAZtX2tQ9yyFX102mALhKxrFjwDyhiQK4wK035DVxDxjEP2VxdccidEwbAIoQEdCLjSywY6C4CG9wyWVOjniIMrSbgXL4wpHdLmGFx+ee1TZXaxbmrD44mvZw+CksfzIydHeCBHkB91QLgckat2YqTn9YPtxkCHfBnAgxYKp2yvpBtIpu5Pf/nowC2V5bRSKRHF6TR0njM3eqATucnPbe/lXml84KEvfoMd4R9DnNOo/lPZfkOBoxbWuAZWwnM8vxObcM2Pct5WJuj9Fhs9szNzk6LkQzAdtycJf396CZG0ewHt0MC0lGsdBAg3GtAJV672tdfx2JrqQHhJurz1ZccU9xdpSKDi3fa/ww7icGaJb/eHAmGNFWzj3ba27qTT6WetfmM='
        }
        # test user where this uuid exists
        django_user_model.objects.create_user(username="the bla", uuid=data['passthrough'], email=user.email)
        response = client.post(reverse("payments:paddle_webhook"), data)
        assert response.status_code == 200


    def test_post_invalid_uuid(
        self, client: Client, settings
    ):
        settings.PADDLE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwuEU7R9nHgWwWy5p9ws3
iORHpFn1L8PkdzNtlZaltck5lD5qcUzmQJiW572LzO8oNFhPgPpTnrvcHfCFTLjc
MmavzroWKiKCf3fn3d7k60D5HDMy4n/+PP6hV2fVnk3Iq3uhxMK5DkKRPqynAFx/
OX20ijvuWGH3rSmmu/JjN0k7QIcMhSdpZuJ7eqtPtBSdg8uRWr8U2ZL2Wufu0xIF
pDBxEK7f+0ECq0x7GftrtvLnbTV4SMblSnN90RMocNsRoul+Ohx4unqLxprPh279
h8iqJspXhb8hKm5PuKuv9N3AXOZzckRTQSFtT/fE3FJm0CToR614r01qc+yqft0e
scTVNY95gug3aqKmjFdwLBVArdycU9+mF7WvmCDUshjot9CDHKXJCkh2Whfwr9Mq
+NN4fu6nd/OF3xaq5jZjN07EyfzYKBU1GBhg3uNfR6v4aogQhKByFwtUUyjV7UaO
yOGH9AMXwv0W/GzDvtZlPwYWUjj9OsJJASG+fYYdwvZRKrs88gTqW0nVXCLgAH3q
a8hsFHngHuJmCkllv/U9JdSiNm2j+ThIXZP+sGb7aT65eYGni7AIBZf56f+gFdCM
IczOqlDDcm8YJ1WNIHvTqg4Qa5/4GcMn69z0NGtYStPbex2AmNwulZaSqXx73qon
7GiVDmdU0t9KRSj9F3nAXVMCAwEAAQ==
    -----END PUBLIC KEY-----"""

        # test invalid uuid
        data = {
            'alert_id': '1729760535',
            'alert_name': 'subscription_created',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?user=7&subscription=6&hash=1b1770968848660fd12777a809166d920b1d8c0d',
            'checkout_id': '8-9c4ffca208adbe5-959b2ce6a6',
            'currency': 'GBP',
            'email': 'hackett.richmond@example.com',
            'event_time': '2019-10-01 09:13:15',
            'marketing_consent': '1',
            'next_bill_date': '2019-10-28',
            'passthrough': 'foo',
            'quantity': '80',
            'status': 'active',
            'subscription_id': '1',
            'subscription_plan_id': '6',
            'unit_price': 'unit_price',
            'update_url': 'https://checkout.paddle.com/subscription/update?user=2&subscription=5&hash=1bcef50d4889c8be3b4f043768c2b7dafb935f2a',
            'user_id': '7',
            'p_signature': 'XfHAM3yFCGu/ij4IPENHcSciGDzlMwy2PgjQETESUb/ekVnqGIBXy4RSDdI6dr3FgQKTtN6uZ/2OlgHd1fyK4hMr540kVN/XBqX+lqmPK16O0+TH0MfaFG/+qYNtjVw9Yv+WpYfK6ACpXcpOhCxburJxJPGjGRFlzkTG0PxM9vHpDV25PF+m7dWg+WWg4hifpg5G+51YDjXoQa8y6+QNUV9r2f7bRH9s5ABBJDyb+7L6vbM3Lz5HT5PYPc4rlGMl3JkZzBHBkaWtDNB+PNPemaObxsscDLUagT8TLWUrabB8Xsc4PvoyRSGzUw7HUKP0zJ05iCtwkXvfSg8DQWE4d7b8/+G03Uhq0pYLQ77wq/4W1gN8uXVtZ5OGA8eAauVwD15Aq1DlGPTz8NE+QCbvaawsYVZzB4LV1VFG0E+sRAz9lg74yH2XGlT0gTigCMuOm3EASOkaVqSI0yLMj0heWkdwLuTlYYkMPVKyJ6llOVAvJlC6nnoIsaMacwkv34nYg/3s9qNMUfpxO69cqYTTSZh3JGXQ7hEl6QplVG5FhL1KE6pB+JnLQqyOcvalpHd8+BU9DeUzSF/facPQSucN0PyWIXeyKxQLcZOupnzA6ri+/+U51K+PSNq0uJ7Dqqq+9+62JvtR4lQ9ib6X1OFKDlzPkRgzMmeyXmFEaWQr5P8='
        }
        response = client.post(reverse("payments:paddle_webhook"), data)
        assert response.status_code == 400


    def test_post_invalid_signature(
        self, client: Client, settings
    ):
        settings.PADDLE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwuEU7R9nHgWwWy5p9ws3
iORHpFn1L8PkdzNtlZaltck5lD5qcUzmQJiW572LzO8oNFhPgPpTnrvcHfCFTLjc
MmavzroWKiKCf3fn3d7k60D5HDMy4n/+PP6hV2fVnk3Iq3uhxMK5DkKRPqynAFx/
OX20ijvuWGH3rSmmu/JjN0k7QIcMhSdpZuJ7eqtPtBSdg8uRWr8U2ZL2Wufu0xIF
pDBxEK7f+0ECq0x7GftrtvLnbTV4SMblSnN90RMocNsRoul+Ohx4unqLxprPh279
h8iqJspXhb8hKm5PuKuv9N3AXOZzckRTQSFtT/fE3FJm0CToR614r01qc+yqft0e
scTVNY95gug3aqKmjFdwLBVArdycU9+mF7WvmCDUshjot9CDHKXJCkh2Whfwr9Mq
+NN4fu6nd/OF3xaq5jZjN07EyfzYKBU1GBhg3uNfR6v4aogQhKByFwtUUyjV7UaO
yOGH9AMXwv0W/GzDvtZlPwYWUjj9OsJJASG+fYYdwvZRKrs88gTqW0nVXCLgAH3q
a8hsFHngHuJmCkllv/U9JdSiNm2j+ThIXZP+sGb7aT65eYGni7AIBZf56f+gFdCM
IczOqlDDcm8YJ1WNIHvTqg4Qa5/4GcMn69z0NGtYStPbex2AmNwulZaSqXx73qon
7GiVDmdU0t9KRSj9F3nAXVMCAwEAAQ==
    -----END PUBLIC KEY-----"""

        data = {
            'alert_id': '38713417',
            'alert_name': 'subscription_created',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?user=7&subscription=6&hash=1b1770968848660fd12777a809166d920b1d8c0d',
            'checkout_id': '8-9c4ffca208adbe5-959b2ce6a6',
            'currency': 'GBP',
            'email': 'hackett.richmond@example.com',
            'event_time': '2019-10-01 08:34:38',
            'marketing_consent': '1',
            'next_bill_date': '2019-10-28',
            'passthrough': 'adacebde-e424-11e9-a359-2a2ae2dbcce4',
            'quantity': '80',
            'status': 'active',
            'subscription_id': '1',
            'subscription_plan_id': '6',
            'unit_price': 'unit_price',
            'update_url': 'https://checkout.paddle.com/subscription/update?user=2&subscription=5&hash=1bcef50d4889c8be3b4f043768c2b7dafb935f2a',
            'user_id': '7',
            'p_signature': 'XfHAM3yFCGu/ij4IPENHcSciGDzlMwy2PgjQETESUb/ekVnqGIBXy4RSDdI6dr3FgQKTtN6uZ/2OlgHd1fyK4hMr540kVN/XBqX+lqmPK16O0+TH0MfaFG/+qYNtjVw9Yv+WpYfK6ACpXcpOhCxburJxJPGjGRFlzkTG0PxM9vHpDV25PF+m7dWg+WWg4hifpg5G+51YDjXoQa8y6+QNUV9r2f7bRH9s5ABBJDyb+7L6vbM3Lz5HT5PYPc4rlGMl3JkZzBHBkaWtDNB+PNPemaObxsscDLUagT8TLWUrabB8Xsc4PvoyRSGzUw7HUKP0zJ05iCtwkXvfSg8DQWE4d7b8/+G03Uhq0pYLQ77wq/4W1gN8uXVtZ5OGA8eAauVwD15Aq1DlGPTz8NE+QCbvaawsYVZzB4LV1VFG0E+sRAz9lg74yH2XGlT0gTigCMuOm3EASOkaVqSI0yLMj0heWkdwLuTlYYkMPVKyJ6llOVAvJlC6nnoIsaMacwkv34nYg/3s9qNMUfpxO69cqYTTSZh3JGXQ7hEl6QplVG5FhL1KE6pB+JnLQqyOcvalpHd8+BU9DeUzSF/facPQSucN0PyWIXeyKxQLcZOupnzA6ri+/+U51K+PSNq0uJ7Dqqq+9+62JvtR4lQ9ib6X1OFKDlzPkRgzMmeyXmFEaWQr5P8='
        }

        # test invalid signature
        data['alert_id'] = "foobar"
        response = client.post(reverse("payments:paddle_webhook"), data)
        assert response.status_code == 403


    def test_post_invalid_action(
        self, user: django_settings.AUTH_USER_MODEL, client: Client, django_user_model, settings
    ):
        settings.PADDLE_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwuEU7R9nHgWwWy5p9ws3
iORHpFn1L8PkdzNtlZaltck5lD5qcUzmQJiW572LzO8oNFhPgPpTnrvcHfCFTLjc
MmavzroWKiKCf3fn3d7k60D5HDMy4n/+PP6hV2fVnk3Iq3uhxMK5DkKRPqynAFx/
OX20ijvuWGH3rSmmu/JjN0k7QIcMhSdpZuJ7eqtPtBSdg8uRWr8U2ZL2Wufu0xIF
pDBxEK7f+0ECq0x7GftrtvLnbTV4SMblSnN90RMocNsRoul+Ohx4unqLxprPh279
h8iqJspXhb8hKm5PuKuv9N3AXOZzckRTQSFtT/fE3FJm0CToR614r01qc+yqft0e
scTVNY95gug3aqKmjFdwLBVArdycU9+mF7WvmCDUshjot9CDHKXJCkh2Whfwr9Mq
+NN4fu6nd/OF3xaq5jZjN07EyfzYKBU1GBhg3uNfR6v4aogQhKByFwtUUyjV7UaO
yOGH9AMXwv0W/GzDvtZlPwYWUjj9OsJJASG+fYYdwvZRKrs88gTqW0nVXCLgAH3q
a8hsFHngHuJmCkllv/U9JdSiNm2j+ThIXZP+sGb7aT65eYGni7AIBZf56f+gFdCM
IczOqlDDcm8YJ1WNIHvTqg4Qa5/4GcMn69z0NGtYStPbex2AmNwulZaSqXx73qon
7GiVDmdU0t9KRSj9F3nAXVMCAwEAAQ==
    -----END PUBLIC KEY-----"""

        # test invalid action
        data = {'alert_id': '50588081', 'alert_name': 'subscription_payment_failed', 'amount': '62.94', 'attempt_number': 'attempt_number', 'cancel_url': 'https://checkout.paddle.com/subscription/cancel?user=2&subscription=5&hash=a85ced48fe6f6b1a3872ef501156d911781908e7', 'checkout_id': '5-1228ae93ffdf5e5-31e6270533', 'currency': 'EUR', 'email': 'emanuel77@example.com', 'event_time': '2019-10-01 10:43:12', 'instalments': '8', 'marketing_consent': '', 'next_retry_date': '2019-10-29', 'order_id': '3', 'passthrough': 'adacebde-e424-11e9-a359-2a2ae2dbcce4', 'quantity': '19', 'status': 'active', 'subscription_id': '3', 'subscription_payment_id': '7', 'subscription_plan_id': '6', 'unit_price': 'unit_price', 'update_url': 'https://checkout.paddle.com/subscription/update?user=4&subscription=7&hash=a98d812951615ae44d38988c06b5d3cefe0704fa', 'user_id': '3', 'p_signature': 'cVJvbifnazFSuVsy3CUYwqDEAABqyMOoAPh8uJ4IBQxGfEh+9nxUCFDoATHtd7NXGNs/kKcOHxjxPPyfvK7LJp+yOkNXHyX3ACU0vpI77caPl8XRjq0vRA0MhyMvkQwq1H5Ti7XI5k7B1EYT8k/oovIffe60ow9cVoJKtlvHF/rnZfxhfViI8cMxtdEj5tt9wyCqB1ehghEZEKLGp3AcbR8FXPUS27tsN55yI/A/0MGjNtjoGuwYwji5sUt2vk4W9ZKgzoOuNi9nw8LfBDJ8DbMkIA/JWXaOuaj6X5FU3OItmXVKhE+OBSDjRlZe/VXH7/rpP+rHt1fdkdbBcJvQPMzN6rm4gAkQjO21d6PcGf37NrfvGweyZ9XIJ4Y/q/OU+rHmgusruZyt32YdMdU+EaJ32mpgx90PniBKQ4l6bw+0ITf+Ujf8YUgYFSpMkdMr/iaZ9U+xHpiql+tkC4Mw80T5lfoLdSdBFZuOmIkF0d7s31KP4JEFNO5PSwbKKEcR/b6e5yZCWpmBKPDjuVDd3Y4n4xkzsNXvugKpPZpRDqhY2tRf650AEcpF16AplEDUbbHELhgD1oe+ZAtmWv68SGraI5EOxZ8Jd7rLxRGycoWsnx5HWC2/mQpAzETR9nOQmwfIEmypXSsT22MnT4ZTXeb21OMVdRnIU+ZJ1kg/vpA='}
        django_user_model.objects.create_user(username="the bla", uuid=data['passthrough'], email=user.email)
        response = client.post(reverse("payments:paddle_webhook"), data)
        assert response.status_code == 404


    def test_is_signed_success(self):
        data = {
            'alert_id': '1600749114',
            'alert_name': 'subscription_created',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?user=7&subscription=6&hash=1b1770968848660fd12777a809166d920b1d8c0d',
            'checkout_id': '8-9c4ffca208adbe5-959b2ce6a6',
            'currency': 'GBP',
            'email': 'hackett.richmond@example.com',
            'event_time': '2019-10-01 08:14:25',
            'marketing_consent': '1',
            'next_bill_date': '2019-10-28',
            'passthrough': 'Example String',
            'quantity': '80',
            'status': 'active',
            'subscription_id': '1',
            'subscription_plan_id': '6',
            'unit_price': 'unit_price',
            'update_url': 'https://checkout.paddle.com/subscription/update?user=2&subscription=5&hash=1bcef50d4889c8be3b4f043768c2b7dafb935f2a',
            'user_id': '7',
            'p_signature': 'PjTv5k6zsErNYQQA995Zy8OJrzrDkxL0DkAh8/zp1wCAfq1eDKUc/P0s88mANlU0VqotOtCFmGTJiTwXjd7UWBWZAKZeyOSlDU9TUmljp8TQ1+eJ4yNicbH2BrU5dTQXkSrpIQQ6v2ZegVc4rDYG1iPINHvGIh8TYAVW6lZE94doiDXOnJyiYdhHher2LdVt/tMaB6BcPLxZyvj5DeeXGXxMsySwhD9Q1lwIpRtdo9xkRGKDMgrsFbhanVdh5LdNBH4lBMknRlS5yRLyqKGfUKX3W0i7GF5AW7dQlK/Afje9vr/CQ2JqdajLhpuJfgHg8e7eEhhwGXTQYk865tyHNfMjsEasWJnq1hryI+yOxJEQ5lnvgIZ0tKZ7rSywZbQcUwSAYxEwL031ulkva05OAHzCaSK90mBIAl+BNLi+068yp/mLSSr+KcoEbem0CIeSKqalhZYAIsJI55V7ByvpCW3Kpy+Nj+zWOkYRFOrAcOCBM7SqyIm8LR0cGrFuGM9mE+I4gqxkiV1fxyYM2zFa9IpLhFZa15GG3BGzZsRHr/+0i9tAq9DJjBbI0wn0hN/XpdjeVklitVendTvaYcKFRRSQzS3h/jJFJwFdUZHdk73km/UoefNtYSzTLYa7r+FMbb7ouIT4804Hd9S0NcSXniN36cTMmAaalSIi9YYyNxM='
        }
        pubkey = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwuEU7R9nHgWwWy5p9ws3
iORHpFn1L8PkdzNtlZaltck5lD5qcUzmQJiW572LzO8oNFhPgPpTnrvcHfCFTLjc
MmavzroWKiKCf3fn3d7k60D5HDMy4n/+PP6hV2fVnk3Iq3uhxMK5DkKRPqynAFx/
OX20ijvuWGH3rSmmu/JjN0k7QIcMhSdpZuJ7eqtPtBSdg8uRWr8U2ZL2Wufu0xIF
pDBxEK7f+0ECq0x7GftrtvLnbTV4SMblSnN90RMocNsRoul+Ohx4unqLxprPh279
h8iqJspXhb8hKm5PuKuv9N3AXOZzckRTQSFtT/fE3FJm0CToR614r01qc+yqft0e
scTVNY95gug3aqKmjFdwLBVArdycU9+mF7WvmCDUshjot9CDHKXJCkh2Whfwr9Mq
+NN4fu6nd/OF3xaq5jZjN07EyfzYKBU1GBhg3uNfR6v4aogQhKByFwtUUyjV7UaO
yOGH9AMXwv0W/GzDvtZlPwYWUjj9OsJJASG+fYYdwvZRKrs88gTqW0nVXCLgAH3q
a8hsFHngHuJmCkllv/U9JdSiNm2j+ThIXZP+sGb7aT65eYGni7AIBZf56f+gFdCM
IczOqlDDcm8YJ1WNIHvTqg4Qa5/4GcMn69z0NGtYStPbex2AmNwulZaSqXx73qon
7GiVDmdU0t9KRSj9F3nAXVMCAwEAAQ==
-----END PUBLIC KEY-----"""
        view = PaddleWebhookView()
        assert view.is_signed(payload=data, pubkey=pubkey) == True


    def test_is_signed_error(self):
        data = {
            'alert_id': '1600749114',
            'alert_name': 'subscription_created',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?user=7&subscription=6&hash=1b1770968848660fd12777a809166d920b1d8c0d',
            'checkout_id': '8-9c4ffca208adbe5-959b2ce6a6',
            'currency': 'GBP',
            'email': 'hackett.richmond@example.com',
            'event_time': '2019-10-01 08:14:25',
            'marketing_consent': '1',
            'next_bill_date': '2019-10-28',
            'passthrough': 'Example String',
            'quantity': '80',
            'status': 'active',
            'subscription_id': '1',
            'subscription_plan_id': '6',
            'unit_price': 'unit_price',
            'update_url': 'https://checkout.paddle.com/subscription/update?user=2&subscription=5&hash=1bcef50d4889c8be3b4f043768c2b7dafb935f2a',
            'user_id': '7',
            'p_signature': 'PjTv5k6zsErNYQQA995Zy8OJrzrDkxL0DkAh8/zp1wCAfq1eDKUc/P0s88mANlU0VqotOtCFmGTJiTwXjd7UWBWZAKZeyOSlDU9TUmljp8TQ1+eJ4yNicbH2BrU5dTQXkSrpIQQ6v2ZegVc4rDYG1iPINHvGIh8TYAVW6lZE94doiDXOnJyiYdhHher2LdVt/tMaB6BcPLxZyvj5DeeXGXxMsySwhD9Q1lwIpRtdo9xkRGKDMgrsFbhanVdh5LdNBH4lBMknRlS5yRLyqKGfUKX3W0i7GF5AW7dQlK/Afje9vr/CQ2JqdajLhpuJfgHg8e7eEhhwGXTQYk865tyHNfMjsEasWJnq1hryI+yOxJEQ5lnvgIZ0tKZ7rSywZbQcUwSAYxEwL031ulkva05OAHzCaSK90mBIAl+BNLi+068yp/mLSSr+KcoEbem0CIeSKqalhZYAIsJI55V7ByvpCW3Kpy+Nj+zWOkYRFOrAcOCBM7SqyIm8LR0cGrFuGM9mE+I4gqxkiV1fxyYM2zFa9IpLhFZa15GG3BGzZsRHr/+0i9tAq9DJjBbI0wn0hN/XpdjeVklitVendTvaYcKFRRSQzS3h/jJFJwFdUZHdk73km/UoefNtYSzTLYa7r+FMbb7ouIT4804Hd9S0NcSXniN36cTMmAaalSIi9YYyNxM='
        }
        pubkey = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAwuEU7R9nHgWwWy5p9ws3
iORHpFn1L8PkdzNtlZaltck5lD5qcUzmQJiW572LzO8oNFhPgPpTnrvcHfCFTLjc
MmavzroWKiKCf3fn3d7k60D5HDMy4n/+PP6hV2fVnk3Iq3uhxMK5DkKRPqynAFx/
OX20ijvuWGH3rSmmu/JjN0k7QIcMhSdpZuJ7eqtPtBSdg8uRWr8U2ZL2Wufu0xIF
pDBxEK7f+0ECq0x7GftrtvLnbTV4SMblSnN90RMocNsRoul+Ohx4unqLxprPh279
h8iqJspXhb8hKm5PuKuv9N3AXOZzckRTQSFtT/fE3FJm0CToR614r01qc+yqft0e
scTVNY95gug3aqKmjFdwLBVArdycU9+mF7WvmCDUshjot9CDHKXJCkh2Whfwr9Mq
+NN4fu6nd/OF3xaq5jZjN07EyfzYKBU1GBhg3uNfR6v4aogQhKByFwtUUyjV7UaO
yOGH9AMXwv0W/GzDvtZlPwYWUjj9OsJJASG+fYYdwvZRKrs88gTqW0nVXCLgAH3q
a8hsFHngHuJmCkllv/U9JdSiNm2j+ThIXZP+sGb7aT65eYGni7AIBZf56f+gFdCM
IczOqlDDcm8YJ1WNIHvTqg4Qa5/4GcMn69z0NGtYStPbex2AmNwulZaSqXx73qon
7GiVDmdU0t9KRSj9F3nAXVMCAwEAAQ==
-----END PUBLIC KEY-----"""
        data['alert_id'] = 'foo'
        view = PaddleWebhookView()
        assert view.is_signed(payload=data, pubkey=pubkey) == False


    def test_subscription_created(self, user: django_settings.AUTH_USER_MODEL):
        data = {
            'alert_id': '123',
            'alert_name': 'subscription_created',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?[redacted]',
            'checkout_id': '2e004acc-ddd8-11e9-8a34-2a2ae2dbcce4',
            'currency': 'EUR',
            'email': 'user@email.com',
            'event_time': '2019-09-20 09:03:46',
            'marketing_consent': '0',
            'next_bill_date': '2019-10-20',
            'passthrough': '09d0931d-9ed9-467a-8009-23214548faa4',
            'quantity': '1',
            'status': 'active',
            'subscription_id': '456',
            'subscription_plan_id': '789',
            'unit_price': '19.00',
            'update_url': 'https://checkout.paddle.com/subscription/update?[redacted]',
            'user_id': '0123',
            'p_signature': '[redacted]'
        }
        view = PaddleWebhookView()
        view.payload = data
        view.user = user
        view.subscription_created()

        assert user.vendor == "paddle"
        assert user.vendor_user_id == data['user_id']
        assert user.vendor_subscription_id == data['subscription_id']
        assert user.plan_id == data['subscription_plan_id']
        assert user.vendor_extra == {
            "cancel_url": data['cancel_url'],
            "update_url": data['update_url']
        }
        assert user.next_billing_date == make_aware(datetime.strptime(data['next_bill_date'], "%Y-%m-%d"))
        assert user.cancellation_effective_date is None
        assert user.vendor_subscription_status == data['status']
        assert user.plan_id == data['subscription_plan_id']
        assert user.is_customer == True


    def test_subscription_updated(
        self, user: django_settings.AUTH_USER_MODEL
    ):
        data = {
            'alert_id': '123',
            'alert_name': 'subscription_updated',
            'cancel_url': 'https://checkout.paddle.com/subscription/cancel?[redacted]',
            'checkout_id': 'd0e62a28-ddd7-11e9-8a34-2a2ae2dbcce4',
            'currency': 'EUR',
            'email': 'user@email.com',
            'event_time': '2019-09-21 10:24:19',
            'marketing_consent': '0',
            'new_price': '49',
            'new_quantity': '1',
            'new_unit_price': '49',
            'next_bill_date': '2019-10-21',
            'old_next_bill_date': '2019-10-21',
            'old_price': '19',
            'old_quantity': '1',
            'old_status': 'active',
            'old_subscription_plan_id': '456',
            'old_unit_price': '19',
            'passthrough': '09d0931d-9ed9-467a-8009-23214548faa4',
            'status': 'active',
            'subscription_id': '789',
            'subscription_plan_id': '012',
            'update_url': 'https://checkout.paddle.com/subscription/update?[redacted]',
            'user_id': '345',
            'p_signature': 'redacted'
        }
        view = PaddleWebhookView()
        view.payload = data
        view.user = user
        view.subscription_updated()

        assert user.vendor == "paddle"
        assert user.vendor_user_id == data['user_id']
        assert user.vendor_subscription_id == data['subscription_id']
        assert user.plan_id == data['subscription_plan_id']
        assert user.vendor_extra == {
            "cancel_url": data['cancel_url'],
            "update_url": data['update_url']
        }
        assert user.next_billing_date == make_aware(datetime.strptime(data['next_bill_date'], "%Y-%m-%d"))
        assert user.cancellation_effective_date is None
        assert user.vendor_subscription_status == data['status']
        assert user.plan_id == data['subscription_plan_id']
        assert user.is_customer == True


    def test_subscription_cancelled(
        self, user: django_settings.AUTH_USER_MODEL
    ):
        data = {
            'alert_id': '123',
            'alert_name': 'subscription_cancelled',
            'cancellation_effective_date': '2019-10-21',
            'checkout_id': 'b37784f0-ddd7-11e9-8a34-2a2ae2dbcce4',
            'currency': 'EUR',
            'email': 'user@email.com',
            'event_time': '2019-09-21 12:40:42',
            'marketing_consent': '0',
            'passthrough': '09d0931d-9ed9-467a-8009-23214548faa4',
            'quantity': '1',
            'status': 'deleted',
            'subscription_id': '456',
            'subscription_plan_id': '789',
            'unit_price': '19.00',
            'user_id': '012',
            'p_signature': '[redacted]'
        }
        view = PaddleWebhookView()
        view.payload = data
        view.user = user
        view.subscription_cancelled()

        assert user.vendor == "paddle"
        assert user.vendor_user_id == data['user_id']
        assert user.vendor_subscription_id == data['subscription_id']
        assert user.plan_id == data['subscription_plan_id']
        assert user.vendor_extra == {}
        assert user.next_billing_date is None
        assert user.cancellation_effective_date == make_aware(
            datetime.strptime(data['cancellation_effective_date'], "%Y-%m-%d")
        )
        assert user.vendor_subscription_status == data['status']
        assert user.plan_id == data['subscription_plan_id']
        assert user.is_customer == True


class TestChangePlanView:

    def test_get_not_allowed(
        self, user: django_settings.AUTH_USER_MODEL, client: Client, settings: django_settings
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'
        client.force_login(user)

        # test get, not allowed
        assert client.get(reverse("payments:change_plan")).status_code == 405


    def test_invalid_form(
        self, user: django_settings.AUTH_USER_MODEL, client: Client, settings: django_settings
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'
        client.force_login(user)

        # test invalid form
        data = {"plan_id": ""}
        assert client.post(reverse("payments:change_plan"), data).status_code == 302


    def test_invalid_plan_id(
        self, user: django_settings.AUTH_USER_MODEL, client: Client, settings: django_settings
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'
        client.force_login(user)
        # test invalid plan id
        data = {"plan_id": "non existent"}
        assert client.post(reverse("payments:change_plan"), data).status_code == 302


    def test_valid_request(
        self, user: django_settings.AUTH_USER_MODEL, client: Client, settings: django_settings, requests_mock: mocker,
        django_user_model: django_settings.AUTH_USER_MODEL
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'
        client.force_login(user)
        # test valid request
        request_data = {
            'success': True,
            'response': {
                'subscription_id': '1999843',
                'user_id': 1856132,
                'plan_id': "pro_plan_id",
                'next_payment': {
                    'amount': 79,
                    'currency': 'EUR',
                    'date': '2019-10-21'
                }
            }
        }

        requests_mock.post(
            "https://vendors.paddle.com/api/2.0/subscription/users/update",
            status_code=200,
            json=request_data
        )
        data = {"plan_id": "pro_plan_id"}
        assert client.post(reverse("payments:change_plan"), data).status_code == 302
        user = django_user_model.objects.get(pk=user.pk)
        assert user.vendor_subscription_id == request_data['response']['subscription_id']

    def test_update_paddle_plan_invalid_plan(
        self, user: django_settings.AUTH_USER_MODEL, settings: django_settings,
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'

        # test invalid plans
        view = ChangePlanView()
        assert view.update_paddle_plan(user=user, plan_id=None) == False
        assert view.update_paddle_plan(user=user, plan_id="some stuff") == False

    def test_update_paddle_plan_invalid_status_code(
        self, user: django_settings.AUTH_USER_MODEL, settings: django_settings, requests_mock: mocker
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'
        # test invalid status code
        requests_mock.post("https://vendors.paddle.com/api/2.0/subscription/users/update", status_code=999)
        view = ChangePlanView()
        assert view.update_paddle_plan(user=user, plan_id='pro_plan_id') == False

    def test_update_paddle_plan_unsuccsessfull_request(
        self, user: django_settings.AUTH_USER_MODEL, settings: django_settings, requests_mock: mocker
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'
        # test paddle unsuccsessful request
        requests_mock.post(
            "https://vendors.paddle.com/api/2.0/subscription/users/update",
            status_code=200,
            json={"success": False}
        )
        view = ChangePlanView()
        assert view.update_paddle_plan(user=user, plan_id='pro_plan_id') == False

    def test_update_paddle_plan_valid_request(
        self, user: django_settings.AUTH_USER_MODEL, settings: django_settings, requests_mock: mocker
    ):
        settings.SAAS_PLANS = [
            {"plan_id": None, },
            {"plan_id": "starter_plan_id", },
            {"plan_id": "pro_plan_id", }
        ]

        settings.PADDLE_VENDOR_ID = 'the vend id'
        settings.PADDLE_AUTH_CODE = 'the auth'
        # test valid request
        data = {
            'success': True,
            'response': {
                'subscription_id': 1999843,
                'user_id': 1856132,
                'plan_id': "pro_plan_id",
                'next_payment': {
                    'amount': 79,
                    'currency': 'EUR',
                    'date': '2019-10-21'
                }
            }
        }

        requests_mock.post(
            "https://vendors.paddle.com/api/2.0/subscription/users/update",
            status_code=200,
            json=data
        )
        view = ChangePlanView()
        assert view.update_paddle_plan(user=user, plan_id='pro_plan_id') == True
        assert user.vendor_subscription_id == data['response']['subscription_id']
