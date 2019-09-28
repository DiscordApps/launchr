# -*- coding: utf-8 -*-
from celery import shared_task
import logging


logger = logging.getLogger(__name__)


@shared_task
def remove_expired_subscriptions():
    pass
