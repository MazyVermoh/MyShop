# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    # 1) Старт оплаты через T-Bank (редирект на платежную страницу)
    #    URL: /payments/tbank/start/<order_id>/
    path("tbank/start/<int:order_id>/", views.tbank_start, name="tbank_start"),

    # 2) Webhook-эндпоинт для приёма уведомлений от T-Bank
    #    URL: /payments/tbank/webhook/
    path("tbank/webhook/", views.tbank_webhook, name="tbank_webhook"),

    # 3) Заглушка демо-платёжной формы (демонстрационный платёж)
    #    URL: /payments/demo/pay/<pid>/
    path("demo/pay/<uuid:pid>/", views.tbank_demo_pay, name="tbank_demo_pay"),
]