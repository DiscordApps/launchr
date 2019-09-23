# -*- coding: utf-8 -*-
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def plan_by_id(plan_id):
    for plan in settings.SAAS_PLANS:
        if plan_id == plan['plan_id']:
            return plan
    return None
