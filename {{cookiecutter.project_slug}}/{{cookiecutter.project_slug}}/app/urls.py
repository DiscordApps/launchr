from django.urls import include, path

from {{ cookiecutter.project_slug }}.app.views import (
    DashboardView
)

app_name = "users"
urlpatterns = [
    path("", view=DashboardView.as_view(), name="dashboard"),
    path("users/", include("{{ cookiecutter.project_slug }}.users.urls", namespace="users")),
]
