from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
{% if cookiecutter.private_beta == 'y' -%}
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from {{cookiecutter.project_slug}}.beta.models import Invite
from {{cookiecutter.project_slug}}.beta.forms import InviteForm


def check_invite(request):

    form = InviteForm(request.GET)
    if form.is_valid():
        if Invite.objects.get(code=form.cleaned_data["code"]).exists():
            return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)
    raise ImmediateHttpResponse(
        response=redirect(reverse("beta:request-invite"))
    )
{% endif %}

class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        {%- if cookiecutter.private_beta == 'y' %}
        if getattr(settings, 'SAAS_PRIVATE_BETA', False):
            return check_invite(request)
        {%- endif %}
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        {%- if cookiecutter.private_beta == 'y' %}
        if getattr(settings, 'SAAS_PRIVATE_BETA', False):
            return check_invite(request)
        {%- endif %}
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)
