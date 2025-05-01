# checkout/views.py
from uuid import uuid4
from django.conf         import settings
from django.shortcuts    import render, redirect
from django.urls         import reverse_lazy
from django.views.decorators.http import require_POST

from yookassa import Configuration, Payment

from cart.session_cart   import Cart
from store.models        import Order, OrderItem

# 1) инициализируем SDK (разово при импорте модуля)
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY


def checkout_view(request):
    """
    GET /checkout/
    Показываем форму + краткое резюме корзины.
    Если корзина пуста → перенаправляем в cart:detail.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    return render(request, "checkout/checkout.html", {
        "cart":       cart,
        "cart_total": cart.total_price(),
    })


@require_POST
def process_order(request):
    """
    POST /checkout/process/
    • Создаём Order и OrderItem.
    • Генерим платёж в YooKassa и редиректим на confirmation_url.
    """
    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # 1) сохраняем сам заказ со статусом pending
    order = Order.objects.create(
        status     = "pending",
        first_name = request.POST.get("first_name", ""),
        last_name  = request.POST.get("last_name",  ""),
        email      = request.POST.get("email",      ""),
        phone      = request.POST.get("phone",      ""),
        country    = request.POST.get("country",    ""),
        city       = request.POST.get("city",       ""),
        address    = request.POST.get("address",    ""),
        postcode   = request.POST.get("postcode",   ""),
    )

    # 2) сохраняем позиции
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # 3) создаём платёж в YooKassa
    total = cart.total_price()  # Decimal
    payment = Payment.create({
        "amount": {
            "value":    f"{total:.2f}",
            "currency": "RUB",
        },
        "confirmation": {
            "type":       "redirect",
            # после оплаты YooKassa вернёт пользователя сюда:
            "return_url": request.build_absolute_uri(
                              reverse_lazy("checkout:success", args=[order.id])
                          )
        },
        "capture":     True,
        "description": f"Заказ #{order.id} на ABUZADA STORE, сумма {total}₽",
    }, uuid4().hex)

    # 4) очищаем корзину и редиректим на YooKassa
    cart.clear()
    return redirect(payment.confirmation.confirmation_url)


def payment_success(request, order_id):
    """
    GET /checkout/success/<order_id>/
    Пользователь вернулся из YooKassa — показываем страницу «Спасибо».
    Status заказа можно обновить через Webhook (см. docs ниже).
    """
    order = Order.objects.filter(id=order_id).first()
    return render(request, "checkout/success.html", {"order": order})