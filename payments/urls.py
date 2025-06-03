from django.urls import path
from . import views

app_name = "payments"     # обязательно!

urlpatterns = [
    path("tbank/webhook/", views.tbank_webhook, name="tbank_webhook"),
]