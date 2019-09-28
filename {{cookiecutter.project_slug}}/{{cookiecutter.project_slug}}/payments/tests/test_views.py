# -*- coding: utf-8 -*-
from test_plus.test import TestCase

from django.test.client import Client


class PaddleTestCase(TestCase):

    def test_subscription_created_hook(self):
        """
        data = {
            'alert_id': ['123'],
            'alert_name': ['subscription_created'],
            'cancel_url': ['https://checkout.paddle.com/subscription/cancel?[redacted]'],
            'checkout_id': ['2e004acc-ddd8-11e9-8a34-2a2ae2dbcce4'],
            'currency': ['EUR'],
            'email': ['user@email.com'],
            'event_time': ['2019-09-20 09:03:46'],
            'marketing_consent': ['0'],
            'next_bill_date': ['2019-10-20'],
            'passthrough': ['09d0931d-9ed9-467a-8009-23214548faa4'],
            'quantity': ['1'],
            'status': ['active'],
            'subscription_id': ['456'],
            'subscription_plan_id': ['789'],
            'unit_price': ['19.00'],
            'update_url': ['https://checkout.paddle.com/subscription/update?[redacted]'],
            'user_id': ['0123'],
            'p_signature': ['[redacted]']
        }
        """

    def test_subscription_updated(self):
        """
        data = {
            'alert_id': ['123'],
            'alert_name': ['subscription_updated'],
            'cancel_url': ['https://checkout.paddle.com/subscription/cancel?[redacted]'],
            'checkout_id': ['d0e62a28-ddd7-11e9-8a34-2a2ae2dbcce4'],
            'currency': ['EUR'],
            'email': ['user@email.com'],
            'event_time': ['2019-09-21 10:24:19'],
            'marketing_consent': ['0'],
            'new_price': ['49'],
            'new_quantity': ['1'],
            'new_unit_price': ['49'],
            'next_bill_date': ['2019-10-21'],
            'old_next_bill_date': ['2019-10-21'],
            'old_price': ['19'],
            'old_quantity': ['1'],
            'old_status': ['active'],
            'old_subscription_plan_id': ['456'],
            'old_unit_price': ['19'],
            'passthrough': ['09d0931d-9ed9-467a-8009-23214548faa4'],
            'status': ['active'],
            'subscription_id': ['789'],
            'subscription_plan_id': ['012'],
            'update_url': ['https://checkout.paddle.com/subscription/update?[redacted]'],
            'user_id': ['345'],
            'p_signature': ['redacted']
        }
        """

    def test_subscription_cancelled(self):
        """
        data = {
            'alert_id': ['123'],
            'alert_name': ['subscription_cancelled'],
            'cancellation_effective_date': ['2019-10-21'],
            'checkout_id': ['b37784f0-ddd7-11e9-8a34-2a2ae2dbcce4'],
            'currency': ['EUR'],
            'email': ['user@email.com'],
            'event_time': ['2019-09-21 12:40:42'],
            'marketing_consent': ['0'],
            'passthrough': ['09d0931d-9ed9-467a-8009-23214548faa4'],
            'quantity': ['1'],
            'status': ['deleted'],
            'subscription_id': ['456'],
            'subscription_plan_id': ['789'],
            'unit_price': ['19.00'],
            'user_id': ['012'],
            'p_signature': ['[redacted]']
        }
        """

    def test_update_paddle_plan(self):
        """
        data = {
        'success': True,
        'response': {
            'subscription_id': 1999843,
            'user_id': 1856132,
            'plan_id': 570975,
            'next_payment': {
                'amount': 79,
                'currency': 'EUR',
                'date': '2019-10-21'
                }
            }
        }
        """


class UserTestCase(TestCase):
    def setUp(self):
        self.user = self.make_user()
        self.other_user = self.make_user(username="other_user")
        self.client = Client()
