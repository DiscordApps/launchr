from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


class AppHomeView(LoginRequiredMixin, TemplateView):
    template_name = "app/home.html"
