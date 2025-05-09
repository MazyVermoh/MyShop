# checkout/views.py

from uuid import uuid4
from decimal import Decimal
from django.conf      import settings
from django.shortcuts import render, redirect
from django.urls      import reverse_lazy
from django.views.decorators.http import require_POST

from .forms           import PromoCodeApplyForm
from cart.session_cart import Cart
from store.models     import Order, OrderItem

# Инициализация YooKassa SDK (пока не используем, но можно раскомментировать)
# from yookassa import Configuration, Payment
# Configuration.account_id = settings.YOOKASSA_SHOP_ID
# Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def checkout_view(request):
    """
    GET/POST /checkout/
    • Отображаем форму ввода контактных данных + промокод
    • При POST и name="apply_promo" применяем скидку
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    promo_form = PromoCodeApplyForm(request.POST or None)
    promo_code = ""
    discount   = Decimal("0")

    # Если пользователь нажал кнопку «Применить» в форме промокода
    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo_code = promo_form.cleaned_data["code"]
            promo_obj  = promo_form.get_promo(promo_code)
            discount   = promo_obj.calculate_discount(cart.total_price())
        # если форма невалидна — она сама покажет ошибку

    # Считаем итоговые суммы
    cart_total  = cart.total_price()
    final_total = cart_total - discount

    return render(request, "checkout/checkout.html", {
        "cart":        cart,
        "cart_total":  cart_total,
        "promo_form":  promo_form,
        "promo_code":  promo_code,
        "discount":    discount,
        "final_total": final_total,
    })


@require_POST
def process_order(request):
    """
    POST /checkout/process/
    Создаём Order + OrderItem и очищаем корзину.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Создаём заказ с учётом промокода и скидки
    order = Order.objects.create(
        status     = "new",
        first_name = request.POST["first_name"],
        last_name  = request.POST.get("last_name", ""),
        email      = request.POST["email"],
        phone      = request.POST.get("phone", ""),
        country    = request.POST["country"],
        city       = request.POST["city"],
        address    = request.POST["address"],
        postcode   = request.POST.get("postcode", ""),
        promo_code = request.POST.get("promo_code", ""),
        discount   = Decimal(request.POST.get("discount", "0")),
    )

    # Сохраняем позиции заказа
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # Очищаем корзину и перенаправляем на страницу «Спасибо»
    cart.clear()
    return redirect(reverse_lazy("checkout:success", args=[order.id]))


def payment_success(request, order_id):
    """
    GET /checkout/success/<order_id>/
    Показываем страницу «Спасибо за заказ».
    """
    order = Order.objects.filter(id=order_id).first()
    return render(request, "checkout/success.html", {"order": order})