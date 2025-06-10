# payments/urls.py
from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("tbank/start/<int:order_id>/", views.tbank_start,   name="tbank_start"),
    path("tbank/webhook/",              views.tbank_webhook, name="tbank_webhook"),

    # --- ⬇️ добавляем ЭТО --------------------------------------
    path(
        "demo/pay/<uuid:pid>/",         # pid = payment_id (UUID)
        views.tbank_demo_pay,
        name="tbank_demo_pay",
    ),
]