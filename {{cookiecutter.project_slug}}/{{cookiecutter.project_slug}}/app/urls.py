from django.urls import include, path

from {{ cookiecutter.project_slug }}.app.views import (
    AppHomeView
)

app_name = "app"
urlpatterns = [
    path("", view=AppHomeView.as_view(), name="home"),
    path("users/", include("{{ cookiecutter.project_slug }}.users.urls", namespace="users")),
]
