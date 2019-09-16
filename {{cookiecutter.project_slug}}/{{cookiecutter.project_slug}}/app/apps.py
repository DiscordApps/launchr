from django.apps import AppConfig as _AppConfig
from django.utils.translation import gettext_lazy as _


class AppConfig(_AppConfig):
    name = "{{ cookiecutter.project_slug }}.app"
    verbose_name = _("App")

    def ready(self):
        try:
            import {{ cookiecutter.project_slug }}.users.signals  # noqa F401
        except ImportError:
            pass
