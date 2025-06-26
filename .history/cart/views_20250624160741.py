# cart/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.urls import reverse
from django.http import HttpRequest, HttpResponse, JsonResponse

from store.models import Product
from .session_cart import Cart


def cart_detail(request: HttpRequest) -> HttpResponse:
    """
    Показывает содержимое корзины: товары, их количество,
    выбранный размер, мини-изображение, а также общую сумму и
    число позиций.
    """
    cart = Cart(request)
    return render(request, "cart/detail.html", {
        "cart":        cart,
        "total_qty":   cart.total_qty(),
        "total_price": cart.total_price(),
    })


@require_POST
def cart_add(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Добавляет товар в корзину или обновляет его количество/размер.
    Если запрос AJAX — возвращает JSON с обновлёнными данными.
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

    # Если AJAX, возвращаем актуальные цифры
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        # пересчёт итоговой строки
        current_qty = cart.cart.get(str(product.id), {}).get("qty", qty)
        row_total = product.price * current_qty
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
            "row_total":   f"{row_total:.2f}",
        })

    # иначе перенаправляем обратно
    return redirect(request.POST.get("next") or reverse("cart:detail"))


@require_POST
def cart_update(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Обновляет количество и/или размер существующей позиции.
    """
    cart = Cart(request)
    qty = max(1, int(request.POST.get("qty", 1)))
    size = request.POST.get("size") or None

    cart.add(
        product_id=product_id,
        qty=qty,
        size=size,
        update=True,
    )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        product = get_object_or_404(Product, id=product_id)
        row_total = product.price * qty
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
            "row_total":   f"{row_total:.2f}",
        })

    return redirect(reverse("cart:detail"))


@require_POST
def cart_remove(request: HttpRequest, product_id: int) -> HttpResponse:
    """
    Удаляет позицию из корзины.
    """
    cart = Cart(request)
    cart.remove(product_id)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "total_qty":   cart.total_qty(),
            "total_price": str(cart.total_price()),
        })

    return redirect(reverse("cart:detail"))