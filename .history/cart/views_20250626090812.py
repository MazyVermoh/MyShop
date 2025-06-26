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
    GET /cart/
    Показываем все позиции, итоговую сумму и количество.
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
    POST /cart/add/<id>/
    Добавить товар или обновить количество.
    """
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    qty   = int(request.POST.get("qty", 1))
    size  = request.POST.get("size") or None
    color = request.POST.get("color") or None
    color = int(color) if color and color.isdigit() else None

    cart.add(
        product_id=product.id,
        qty=qty,
        size=size,
        color=color,
        update=(request.POST.get("update") == "1"),
    )
    return redirect(request.POST.get("next") or reverse("cart:detail"))


@require_POST
def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    POST /cart/update/<id>/
    Изменить количество для конкретного варианта (size/color).
    Поддерживается AJAX.
    """
    cart = Cart(request)
    # Гарантируем минимум 1
    qty = max(1, int(request.POST.get("qty", 1)))

    size  = request.POST.get("size") or None
    color = request.POST.get("color") or None
    color = int(color) if color and color.isdigit() else None

    cart.add(
        product_id=product_id,
        qty=qty,
        size=size,
        color=color,
        update=True,
    )

    # AJAX?
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
    POST /cart/remove/<id>/
    Удалить позицию: конкретный размер/цвет или все варианты товара,
    если size/color не указаны. Поддерживается AJAX.
    """
    cart = Cart(request)

    size  = request.POST.get("size") or None
    color = request.POST.get("color") or None
    color = int(color) if color and color.isdigit() else None

    cart.remove(
        product_id=product_id,
        size=size,
        color=color,
    )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
        })

    return redirect(reverse("cart:detail"))