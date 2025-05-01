# checkout/views.py
from django.shortcuts   import redirect
from django.urls        import reverse_lazy
from django.conf        import settings
from yookassa import Configuration, Payment
from cart.session_cart import Cart

# перед первым вызовом обязательно инициализируем:
Configuration.account_id = settings.YOOKASSA_SHOP_ID
Configuration.secret_key = settings.YOOKASSA_SECRET_KEY

def process_order(request):
    if request.method != "POST":
        return redirect(reverse_lazy("checkout:index"))

    cart = Cart(request)
    if len(cart) == 0:
        return redirect("cart:detail")

    # Собираем сумму в копейках (ЮKassa принимает в целых рублях*100)
    total_rub = cart.total_price()  
    amount = {
        "value":    f"{total_rub:.2f}",
        "currency": "RUB",
    }

    # Создаём платёж в YooKassa
    payment = Payment.create({
        "amount": amount,
        "confirmation": {
            "type":      "redirect",
            "return_url": request.build_absolute_uri(reverse_lazy("checkout:success"))
        },
        "capture": True,  # сразу списать
        "description": f"Заказ в ABUZADA STORE, сумма {total_rub}₽",
    }, uuid4().hex)

    # Сохраняем Order в БД (статус pending) и OrderItem’ы (как было)
    order = Order.objects.create(
        # …заполняем данные из формы…
        status="pending",
        first_name = request.POST.get("first_name", "Гость"),
        # … и т.д.
    )
    for item in cart:
        OrderItem.objects.create(
            order    = order,
            product  = item["product"],
            price    = item["product"].price,
            qty      = item["qty"],
            size     = item.get("size") or "",
            color_id = item.get("color"),
        )

    # Очищаем корзину только после успешного создания платежа
    cart.clear()

    # Перенаправляем пользователя на страницу подтверждения YooKassa
    return redirect(payment.confirmation.confirmation_url)