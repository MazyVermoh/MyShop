# cart/views.py

from __future__ import annotations
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, JsonResponse

from store.models import Product
from .session_cart import Cart


def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Показывает все строки корзины, итоговую сумму и общее кол-во штук.
    """
    cart = Cart(request)
    context = {
        "cart":        cart,
        "total_qty":   cart.total_qty(),
        "total_price": cart.total_price(),
    }
    return render(request, "cart/detail.html", context)


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Добавить товар (или увеличить кол-во) для данной пары (product, size).
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    qty  = int(request.POST.get("qty", 1))
    size = request.POST.get("size") or None

    cart.add(
        product_id=product.id,
        qty=qty,
        size=size,
        update=request.POST.get("update") == "1",
    )
    return redirect(request.POST.get("next") or reverse("cart:detail"))


@require_POST
def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Обновить кол-во для строки с данным (product, size).
    Поддерживается AJAX-запросы для динамического обновления.
    """
    cart = Cart(request)
    qty  = max(1, int(request.POST.get("qty", 1)))
    size = request.POST.get("size") or None

    cart.add(
        product_id=product_id,
        qty=qty,
        size=size,
        update=True,
    )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        prod = get_object_or_404(Product, id=product_id)
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
            "row_total":   str(prod.price * qty),
        })
    return redirect(reverse("cart:detail"))


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Удалить строку по (product, size).
    Поддерживается AJAX-запросы для динамического обновления.
    """
    cart = Cart(request)
    size = request.POST.get("size") or None

    cart.remove(product_id, size=size)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
        })
    return redirect(reverse("cart:detail"))