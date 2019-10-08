from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView, UpdateView

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
