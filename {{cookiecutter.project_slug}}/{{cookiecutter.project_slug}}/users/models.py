from django.contrib.auth.models import AbstractUser
from django.db.models import CharField, UUIDField, BooleanField, DateTimeField
from django.contrib.postgres.fields import JSONField
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.mail import send_mail

import uuid
import hashlib
from urllib.parse import urlencode
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

from {{cookiecutter.project_slug}}.payments.plan import plan_by_id


class User(AbstractUser):
    """
    This is the user class, a subclass of AbstractUser, see:
    https://docs.djangoproject.com/en/dev/topics/auth/customizing/

    In addition to the functionality which the AbstractUser is providing,
    this model also holds all the fields, methods and properties to
    store the state of a subscription via paddle.
    """
    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Full Name"), blank=True, max_length=255)
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
    vendor_subscription_status = CharField(max_length=30, null=True, blank=True)

    next_billing_date = DateTimeField(default=None, null=True, blank=True)
    cancellation_effective_date = DateTimeField(default=None, null=True, blank=True)

    def get_avatar_url(self):
        """
        Get an avatar for this user.
        If social logins (like Twitter, GitHub, Facebook) are used, this method
        should be updated to return the corresponding avatars on these platforms.
        :return: URL to the user avatar, or a placeholder image
        """
        return f"https://www.gravatar.com/avatar/{hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()}" \
               f"?{urlencode(({'d': 'mp', 's': str('400x400')}))}"

    def get_absolute_url(self):
        """
        Get the absolute URL for an authenticated user. By default, this points
        to a view where the user can get an overview on account specific data
        such as settings, subscription, attached email addresses etc.
        :return: URL to the user's setting overview page
        """
        return reverse("app:users:detail")

    def get_cancel_url(self):
        """
        Get the cancel URL for the Plan the user is currently subscribed to.
        If paddle.js is loaded, the url can be opened as an iFrame by setting
        the class to 'paddle_button'.
        :return: URL to paddles cancel page, None if not a customer
        """
        if self.is_paddle_customer:
            return self.vendor_extra['cancel_url']
        return None

    def get_payment_update_url(self):
        """
        Get the payment update URL for the current user.
        If paddle.js is loaded, the url can be opened as an iFrame by setting
        the class to 'paddle_button'.
        :return: URL to paddles payment update page, None if not a customer
        """
        if self.is_paddle_customer:
            return self.vendor_extra["update_url"]
        return None

    def __str__(self):
        """
        String representation of the current user.
        :return: users email address
        """
        return self.email

    @property
    def is_paddle_customer(self):
        """
        Used to determine if a user is a paddle customer.
        :return: True if customer via paddle, False if not
        """
        return self.vendor == 'paddle'

    @property
    def subscription_status(self):
        """
        Check the users subscription status.
        The subscription status depends on the current Plan the user is attached to
        and the state of the given subscription.
        :return: string, indicating the subscription status
        """
        if self.is_paddle_customer:
            if self.vendor_subscription_status == 'deleted':
                return "cancelled"
            # todo: find out about paddles trial status
            return self.vendor_subscription_status
        if self.has_freemium_subscription:
            return "active"
        if self.has_trialling_subscription:
            return "trial"
        return None

    @property
    def has_active_subscription(self):
        """
        Used to determine if the subscription the current user is attached to
        is active.
        :return: True if active, False if not
        """
        return self.subscription_status == "active"

    @property
    def has_cancelled_subscription(self):
        """
        Used to determine if the subscription the current user is attached to
        has been cancelled.
        :return: True if cancelled, False if not
        """
        return self.subscription_status == "cancelled"

    @property
    def has_freemium_subscription(self):
        """
        Used to determine if the user is currently subscribed via the freemium
        subscription type.
        In order to subscribe users to the freemium subscription type by default,
        set SAAS_SUBSCRIPTION_TYPE='freemium' in settings/base.py.
        :return: True if freemium user, False if not
        """
        return settings.SAAS_SUBSCRIPTION_TYPE == 'freemium' and self.plan_id is None

    @property
    def has_trialling_subscription(self):
        """
        Used to determine if the user is currently running on an active trial subscription.
        In order to subscribe users to the trial subscription type by default,
        set SAAS_SUBSCRIPTION_TYPE='trial' in settings/base.py.
        :return: True if active trial, False if not
        """
        return settings.SAAS_SUBSCRIPTION_TYPE == 'trial' and self.plan_id is None and self.is_trial_active

    @property
    def has_no_subscription(self):
        """
        Used to determine if the user has currently no subscription whatsoever.
        This is the default state for a new user if SAAS_SUBSCRIPTION_TYPE=None in settings/base.py.
        When SAAS_SUBSCRIPTION_TYPE=='trial' is set in settings/base.py, this is the default state
        for every user that did not upgrade to a proper subscription.
        :return: True if the user has no active subscription, False if not
        """
        return ((settings.SAAS_SUBSCRIPTION_TYPE is None or settings.SAAS_SUBSCRIPTION_TYPE == "None")
                and self.plan_id is None) or \
               (settings.SAAS_SUBSCRIPTION_TYPE == 'trial' and self.plan_id is None and not self.is_trial_active)

    @property
    def trial_ends_at(self):
        """
        Used to get the date when the trial the user is attached to runs out.
        :return: timezone aware datetime object
        """
        if settings.SAAS_SUBSCRIPTION_TYPE != 'trial':
            raise ImproperlyConfigured(
                f"Your code calls user.trials_ends_at, but your SAAS_SUBSCRIPTION_TYPE "
                "is {SAAS_SUBSCRIPTION_TYPE} which is not supported. Set "
                "SAAS_SUBSCRIPTION_TYPE = 'trial' in settings/base.py, or remove the call "
                "to user.trial_ends_at")
        return self.date_joined + settings.SAAS_TRIAL_LENGTH

    @property
    def is_trial_active(self):
        """
        Used to determine if the trial the current user is running is active.
        :return: True if active, False if not
        """
        return self.date_joined + settings.SAAS_TRIAL_LENGTH > timezone.now()

    @property
    def has_paid_subscription(self):
        """
        Check if the user is subscribed to a paid plan.
        :return: True if so, False if not
        """
        return self.vendor_subscription_id is not None

    @property
    def plan(self):
        """
        Get the plan the user is currently subscribed to.
        Plans are set in settings/base.py as a list of dictionaries.
        The only requirement for these dictionaries is that the
        dictionary contains 'plan_id' key. If the users plan_id
        is set to None, it is assumed that the user is subscribed to
        the default plan.
        Example:
        SAAS_PLANS = [
            {"plan_id": None, "name": "default"},
            {"plan_id": "pro", "name": "Pro Plan"},
        ]
        :return: Dictionary, None if no plan
        """
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
        from {{cookiecutter.project_slug}}.users.tasks import subscribe_to_mailing_list
        subscribe_to_mailing_list.delay(user_pk=instance.pk)
