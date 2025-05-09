from django.urls import path
from . import views

app_name = "checkout"

urlpatterns = [
    path("",         views.checkout_view, name="index"),
    path("process/", views.process_order, name="process"),
    path("success/<int:order_id>/", views.payment_success, name="success"),
    path("status/<int:order_id>/",  views.order_status, name="order_status"),
]