from django.urls import path

from {{ cookiecutter.project_slug }}.users.views import UserDetailView, UserUpdateView

app_name = "users"
urlpatterns = [
    path("~update/", view=UserUpdateView.as_view(), name="update"),
    path("/", view=UserDetailView.as_view(), name="detail"),
]
