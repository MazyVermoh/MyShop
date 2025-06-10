# payments/urls.py
from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    # 1) старт оплаты (редирект на страницу оплаты в T-Bank)
    #    /payments/tbank/start/<order_id>/
    path("tbank/start/<int:order_id>/", views.tbank_start, name="tbank_start"),

    # 2) webhook от банка
    #    /payments/tbank/webhook/
    path("tbank/webhook/", views.tbank_webhook, name="tbank_webhook"),
]