from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, UUIDField, BooleanField, DateTimeField
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail
import uuid

from django.conf import settings

from {{cookiecutter.project_slug}}.payments.plan import plan_by_id


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    uuid = UUIDField(default=uuid.uuid4, editable=False, unique=True)

    plan_id = CharField(max_length=50, blank=True, null=True)

    is_customer = BooleanField(default=False)

    class VENDORS(object):
        PADDLE = "paddle"
        STRIPE = "stripe"
    vendor = CharField(max_length=50, null=True, blank=True)
    vendor_user_id = CharField(max_length=50, null=True, blank=True)
    vendor_subscription_id = CharField(max_length=50, null=True, blank=True)
    vendor_plan_id = CharField(max_length=50, null=True, blank=True)
    vendor_extra = JSONField(default=dict)

    subscription_status = CharField(max_length=30, null=True, blank=True)
    next_billing_date = DateTimeField(default=None, null=True, blank=True)
    cancellation_effective_date = DateTimeField(default=None, null=True, blank=True)

    def get_absolute_url(self):
        return reverse("app:users:detail")

    def get_cancel_url(self):
        if self.is_paddle_customer:
            return self.vendor_extra['cancel_url']

    def get_payment_update_url(self):
        if self.is_paddle_customer:
            return self.vendor_extra["update_url"]

    def __str__(self):
        return self.email

    @property
    def is_paddle_customer(self):
        return self.vendor == 'paddle'

    @property
    def has_active_subscription(self):
        return self.subscription_status == "active"

    @property
    def has_cancelled_subscription(self):
        return self.subscription_status == "deleted"

    @property
    def has_subscription(self):
        return self.vendor_subscription_id is not None

    @property
    def plan(self):
        return plan_by_id(self.plan_id)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def send_registration_mail(sender, instance=None, created=False, **kwargs):
    if created:
        send_mail(
            "New Registration",
            message="{email} has just registered".format(email=instance.email),
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL"),
            recipient_list=[settings.SAAS_INFO_MAIL]
        )


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def subscribe_to_mailing_list(sender, instance=None, created=False, **kwargs):
    if created:
        from {{ cookiecutter.project_slug }}.users.tasks import subscribe_to_mailing_list
        subscribe_to_mailing_list.delay(user_pk=instance.pk)
