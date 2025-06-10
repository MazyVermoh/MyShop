from django.urls import path
from . import views

app_name = "payments"
urlpatterns = [
    path("tbank/start/<int:order_id>/", views.tbank_start, name="tbank_start"),
    path("tbank/hook/", views.tbank_hook, name="tbank_hook"),
]