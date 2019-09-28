# -*- coding: utf-8 -*-
from django.conf import settings


def plan_by_id(plan_id):
    for plan in settings.SAAS_PLANS:
        if plan_id == plan['plan_id']:
            return plan
    return None
