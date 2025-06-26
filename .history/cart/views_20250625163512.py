"""
cart/views.py

Четыре view-функции для управления корзиной,
работают с классом Cart из cart.session_cart.
"""

from __future__ import annotations

from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpRequest, HttpResponse

from store.models import Product
from .session_cart import Cart
from django.http import JsonResponse
from django.views.decorators.http import require_POST

# ───────────────────────────────────────────────────────────────
# 1. Страница «Моя корзина»
#    GET /cart/
# ───────────────────────────────────────────────────────────────
def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Показываем все позиции, итоговую сумму и количество.
    Шаблон пока будет simple (`templates/cart/detail.html`).
    """
    cart = Cart(request)
    context = {
        "cart":          cart,
        "total_qty":     cart.total_qty(),
        "total_price":   cart.total_price(),
    }
    return render(request, "cart/detail.html", context)


# ───────────────────────────────────────────────────────────────
# 2. Добавить товар
#    POST /cart/add/<id>/
# ───────────────────────────────────────────────────────────────
@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    qty   = int(request.POST.get("qty", 1))
    size  = request.POST.get("size")   or None
    color = request.POST.get("color")  or None
    color = int(color) if color and color.isdigit() else None

    cart.add(
        product_id=product.id,
        qty=qty,
        size=size,
        color=color,
        update=request.POST.get("update") == "1",
    )
    # после добавления — обратно на страницу, откуда пришёл пользователь
    return redirect(request.POST.get("next") or reverse("cart:detail"))


# ───────────────────────────────────────────────────────────────
# 3. Изменить количество
#    POST /cart/update/<id>/
# ───────────────────────────────────────────────────────────────
@require_POST
def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request)
    qty = max(1, int(request.POST.get("qty", 1)))   # не даём <=0
    cart.add(product_id, qty=qty, update=True)
    return redirect(reverse("cart:detail"))


# ───────────────────────────────────────────────────────────────
# 4. Удалить позицию
#    POST /cart/remove/<id>/
# ───────────────────────────────────────────────────────────────
@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    cart = Cart(request)
    cart.remove(product_id)
    return redirect(reverse("cart:detail"))

# --- UPDATE ---
@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    qty = max(1, int(request.POST.get("qty", 1)))
    cart.add(product_id, qty=qty, update=True)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        prod = get_object_or_404(Product, id=product_id)
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
            "row_total":   str(prod.price * qty),
        })
    return redirect("cart:detail")
# --- REMOVE ---
@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    cart.remove(product_id)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
        })
    return redirect("cart:detail")