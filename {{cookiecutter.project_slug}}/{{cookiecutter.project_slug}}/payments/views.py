from django.views.generic import TemplateView, UpdateView, FormView
from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseNotAllowed, HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.timezone import make_aware
from django.contrib.auth.mixins import LoginRequiredMixin

from {{cookiecutter.project_slug}}.users.models import User
from {{cookiecutter.project_slug}}.payments.forms import ChangePlanForm
from {{cookiecutter.project_slug}}.payments.plan import plan_by_id

import requests
from datetime import datetime
import logging
import collections
import base64
from uuid import UUID

from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA
import phpserialize


logger = logging.getLogger(__name__)


class PricingView(TemplateView):
    template_name = "payments/pricing.html"

    def get_context_data(self, **kwargs):
        data = super(PricingView, self).get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            data["USE_PADDLE"] = settings.USE_PADDLE
            data["PADDLE_VENDOR_ID"] = settings.PADDLE_VENDOR_ID
            data["plans"] = settings.SAAS_PLANS
        return data


class PaddleWebhookView(UpdateView):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(PaddleWebhookView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponseNotAllowed(permitted_methods="POST")

    @staticmethod
    def is_signed(payload, pubkey):
        # Convert key from PEM to DER - Strip the first and last lines and newlines, and decode
        public_key_encoded = pubkey[26:-25].replace('\n', '')
        public_key_der = base64.b64decode(public_key_encoded)

        # input_data represents all of the POST fields sent with the request
        # Get the p_signature parameter & base64 decode it.
        signature = payload['p_signature']

        # Remove the p_signature parameter
        del payload['p_signature']

        # Ensure all the data fields are strings
        for field in payload:
            payload[field] = str(payload[field])

        # Sort the data
        sorted_data = collections.OrderedDict(sorted(payload.items()))
        # and serialize the fields
        serialized_data = phpserialize.dumps(sorted_data)

        # verify the data
        key = RSA.importKey(public_key_der)
        digest = SHA.new() # type: ignore
        digest.update(serialized_data)
        verifier = pkcs1_15.new(key)
        signature = base64.b64decode(signature)
        return verifier.verify(digest, signature)

    def post(self, request, *args, **kwargs):

        """
        if not self.is_signed(
            payload=request.POST.copy(),
            pubkey=settings.PADDLE_PUBLIC_KEY,
        ):
            logger.error(
                 "Received Paddle webhook with invalid signature"
                  extra={"body": request.body}
            )
            raise PermissionDenied
        """
        self.payload = request.POST

        # get the user associated with this request
        try:
            user_uuid = UUID(self.payload.get("passthrough"), version=4)
        except ValueError:
            logger.error(
                "Received Paddle webhook with an invalid uuid.",
                extra={"body": request.body, "uuid": self.payload.get("passthrough")}
            )
            raise PermissionDenied

        try:
            self.user = User.objects.get(uuid=user_uuid)
        except User.DoesNotExist:
            logger.error(
                "Received Paddle webhook with a user that does not exist.",
                extra={"body": request.body, "uuid": user_uuid}
            )
            raise Http404

        # call the function for this {event}_{action} combination
        self.action = self.payload.get("alert_name", False)
        fname = self.action

        if fname in self.ALLOWED_FUNCTIONS:
            getattr(self, fname)()
        else:
            logger.error("Unrecognized action sent", extra={"body": self.payload})

        return HttpResponse("ok")

    ALLOWED_FUNCTIONS = [
        "subscription_created",
        "subscription_updated",
        "subscription_cancelled"
    ]

    def subscription_created(self):
        # set vendor params
        self.user.vendor = self.user.VENDORS.PADDLE
        self.user.vendor_user_id = self.payload['user_id']
        self.user.vendor_subscription_id = self.payload['subscription_id']
        self.user.vendor_plan_id = self.payload['subscription_plan_id']
        self.user.vendor_extra = {
            "cancel_url": self.payload['cancel_url'],
            "update_url": self.payload['update_url']
        }

        self.user.next_billing_date = make_aware(
            datetime.strptime(self.payload['next_bill_date'], "%Y-%m-%d")
        )
        self.user.cancellation_effective_date = None
        self.user.subscription_status = self.payload['status']
        self.user.plan_id = self.user.vendor_plan_id
        self.user.is_customer = True
        self.user.save()

    def subscription_updated(self):
        # set vendor params
        self.user.vendor = self.user.VENDORS.PADDLE
        self.user.vendor_user_id = self.payload['user_id']
        self.user.vendor_subscription_id = self.payload['subscription_id']
        self.user.vendor_plan_id = self.payload['subscription_plan_id']
        self.user.vendor_extra = {
            "cancel_url": self.payload['cancel_url'],
            "update_url": self.payload['update_url']
        }

        self.user.next_billing_date = make_aware(
            datetime.strptime(self.payload['next_bill_date'], "%Y-%m-%d")
        )
        self.user.cancellation_effective_date = None
        self.user.subscription_status = self.payload['status']
        self.user.plan_id = self.user.vendor_plan_id
        self.user.is_customer = True
        self.user.save()

    def subscription_cancelled(self):
        # set vendor params
        self.user.vendor = self.user.VENDORS.PADDLE
        self.user.vendor_user_id = self.payload['user_id']
        self.user.vendor_subscription_id = self.payload['subscription_id']
        self.user.vendor_plan_id = self.payload['subscription_plan_id']
        self.user.vendor_extra = {}

        self.user.next_billing_date = None
        self.user.cancellation_effective_date = make_aware(
            datetime.strptime(self.payload['cancellation_effective_date'], "%Y-%m-%d")
        )

        self.user.subscription_status = self.payload['status']
        self.user.plan_id = self.user.vendor_plan_id
        self.user.is_customer = True
        self.user.save()


def update_paddle_plan(user, plan_id):
    plan = plan_by_id(plan_id)
    if not plan:
        logger.error(
            "A user tried to change to a non-existing plan",
            extra={"plan_id": plan_id, "user": user}
        )
        return False

    payload = {
        "vendor_id": settings.PADDLE_VENDOR_ID,
        "vendor_auth_code": settings.PADDLE_AUTH_CODE,
        "subscription_id": user.vendor_subscription_id,
        "plan_id": plan['plan_id'],
        "passthrough": str(user.uuid)
    }
    r = requests.post(
        url="https://vendors.paddle.com/api/2.0/subscription/users/update",
        data=payload
    )
    if not r.status_code == 200:
        logger.error(
            "There was an error changing a users plan",
            extra={"request": r, "user": user}
        )
        return False

    data = r.json()

    if not data['success']:
        logger.error(
            "There was an error changing a users plan",
            extra={"request": r, "data": data, "user": user}
        )
        return False

    user.vendor_subscription_id = data['response']['subscription_id']
    user.vendor_user_id = data['response']['user_id']
    user.vendor_plan_id = data['response']['plan_id']
    user.next_billing_date = make_aware(
        datetime.strptime(data['response']['next_payment']['date'], "%Y-%m-%d")
    )
    user.cancellation_effective_date = None
    user.plan_id = user.vendor_plan_id
    user.is_customer = True
    user.save()
    return True


class ChangePlanView(LoginRequiredMixin, FormView):

    form_class = ChangePlanForm

    def form_valid(self, form):
        if not update_paddle_plan(self.request.user, form.cleaned_data["plan_id"]):
            messages.add_message(
                self.request,
                messages.ERROR,
                'There was an error changing your plan. Please try again or contact support.'
            )
            return HttpResponseRedirect(reverse("pricing"))
        messages.add_message(self.request, messages.SUCCESS, 'Successfully changed plan')
        return HttpResponseRedirect(reverse("app:home"))

    def form_invalid(self, form):
        messages.add_message(
            self.request,
            messages.ERROR,
            'There was an error changing your plan. Please try again or contact support.'
        )
        return HttpResponseRedirect(self.request.build_absolute_uri())
