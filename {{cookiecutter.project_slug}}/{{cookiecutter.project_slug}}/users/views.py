from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, RedirectView, UpdateView
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserDetailView(LoginRequiredMixin, DetailView):

    model = User
    slug_field = "username"
    slug_url_kwarg = "username"
    template_name = "app/users/user_detail.html"

    def get_object(self):
        return User.objects.get(username=self.request.user.username)



class UserUpdateView(LoginRequiredMixin, UpdateView):

    model = User
    fields = ["name"]
    template_name = "app/users/user_form.html"

    def get_success_url(self):
        return reverse("app:users:detail")

    def get_object(self):
        return User.objects.get(username=self.request.user.username)

    def form_valid(self, form):
        messages.add_message(
            self.request, messages.INFO, _("Infos successfully updated")
        )
        return super().form_valid(form)

