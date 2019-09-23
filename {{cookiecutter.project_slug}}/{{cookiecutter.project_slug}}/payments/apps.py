from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PaymentsConfig(AppConfig):
    name = "{{ cookiecutter.project_slug }}.payments"
    verbose_name = _("Payments")
