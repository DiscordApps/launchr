from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, RedirectView, UpdateView


class DashboardView(LoginRequiredMixin, TemplateView):

     template_name = "app/dashboard.html"
