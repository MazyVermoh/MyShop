from django.shortcuts import render, redirect
from cart.session_cart import Cart
from store.models import Order, OrderItem

def checkout_view(request):
    cart = Cart(request)

    # Пустую корзину оформлять нельзя
    if len(cart) == 0:
        return redirect("cart:detail")

    # MVP-режим: создаём заказ сразу после POST-запроса
    if request.method == "POST":
        order = Order.objects.create(
            first_name = request.POST.get("first_name", "Гость"),
            email      = request.POST.get("email",      "no@mail"),
            country    = request.POST.get("country",    "-"),
            city       = request.POST.get("city",       "-"),
            address    = request.POST.get("address",    "-"),
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

        cart.clear()
        # TODO: позже сделаем «Спасибо за заказ»
        return redirect("home")

    return render(request, "checkout/checkout.html", {
        "cart": cart,
        "total": cart.total_price(),
    })