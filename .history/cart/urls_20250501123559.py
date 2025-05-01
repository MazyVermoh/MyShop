# cart/urls.py
from django.urls import path

from . import views


app_name = "cart"

urlpatterns = [
    # страница «Моя корзина»
    path("", views.cart_detail, name="detail"),

    # операции с товарами
    path("add/<int:product_id>/",    views.cart_add,    name="add"),
    path("update/<int:product_id>/", views.cart_update, name="update"),
    path("remove/<int:product_id>/", views.cart_remove, name="remove"),
]