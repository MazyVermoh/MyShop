# checkout/views.py
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from cart.session_cart import Cart


# ─────────────────────────────────────────────
#  Страница оформления   GET /checkout/
# ─────────────────────────────────────────────
def checkout_view(request):
    """
    Отображает форму оформления + резюме корзины.
    Если корзина пуста — переадресация обратно в неё.
    """
    cart = Cart(request)

    if len(cart) == 0:                       # пустая корзина → назад
        return redirect("cart:detail")

    context = {
        "cart":          cart,
        "cart_total":    cart.total_price(),
    }
    return render(request, "checkout/checkout.html", context)


# ─────────────────────────────────────────────
#  Обработка формы     POST /checkout/process/
# ─────────────────────────────────────────────
def process_order(request):
    """
    MVP-заглушка: очищаем корзину и шлём пользователя на главную.
    Позже здесь:
        • валидация формы            (имя, адрес, e-mail …)
        • создание Order / OrderItem
        • вызов YooKassa API
        • письмо-подтверждение покупателю
    """
    if request.method == "POST":
        Cart(request).clear()               # обнуляем корзину
        return redirect(reverse_lazy("home"))

    # если открыли GET-ом, отправляем обратно на форму
    return redirect(reverse_lazy("checkout:index"))