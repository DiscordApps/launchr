from django.urls import path

from {{ cookiecutter.project_slug }}.payments.views import (
    PaddleWebhookView, ChangePlanView
)

app_name = "payments"
urlpatterns = [
    path("hook/paddle/", view=PaddleWebhookView.as_view(), name="paddle_webhook"),
    path('change-plan/', view=ChangePlanView.as_view(), name="change_plan"),
]
