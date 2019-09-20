from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class BetaConfig(AppConfig):
    name = "{{ cookiecutter.project_slug }}.beta"
    verbose_name = _("Beta")
