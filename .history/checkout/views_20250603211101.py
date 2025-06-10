# checkout/views.py
from decimal import Decimal
from uuid import uuid4

from django.conf import settings
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.decorators.http import require_POST

from cart.session_cart import Cart
from payments.gateway import tbank_gateway
from payments.models import TBankPayment
from store.models import Order, OrderItem
from .forms import PromoCodeApplyForm
from .utils import notify_admin_new_order, send_order_confirmation

# ────────────────────────────────────────────────────────────────
# 1. /checkout/  — форма + промокод
# ────────────────────────────────────────────────────────────────
def checkout_view(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if not cart:
        return redirect("cart:detail")

    promo_form = PromoCodeApplyForm(request.POST or None)
    discount = Decimal("0")
    promo_code = ""

    if request.method == "POST" and "apply_promo" in request.POST:
        if promo_form.is_valid():
            promo_obj = promo_form.cleaned_data["code"]
            promo_code = promo_obj.code
            discount = promo_obj.calculate_discount(cart.total_price())

    cart_total = cart.total_price()
    shipping_price = Decimal("0")        # ПВЗ по умолчанию
    final_total = cart_total - discount  # без доставки

    return render(
        request,
        "checkout/checkout.html",
        {
            "cart": cart,
            "cart_total": cart_total,
            "promo_form": promo_form,
            "discount": discount,
            "promo_code": promo_code,
            "final_total": final_total,
            "DADATA_SUGGESTIONS_KEY": settings.DADATA_API_KEY,
        },
    )


# ────────────────────────────────────────────────────────────────
# 2. POST /checkout/process/  — создаём заказ и платёж
# ────────────────────────────────────────────────────────────────
@require_POST
def process_order(request: HttpRequest) -> HttpResponse:
    cart = Cart(request)
    if not cart:
        return redirect("cart:detail")

    promo_code = request.POST.get("promo_code", "")
    discount = Decimal(request.POST.get("discount", "0"))
    shipping_method = request.POST.get("shipping", "courier")
    payment_method = request.POST.get("payment", "card")
    telegram_handle = request.POST.get("telegram", "").lstrip("@")

    shipping_price = Decimal("600.00") if shipping_method == "courier" else Decimal("0")

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        status="pending",
        first_name=request.POST.get("first_name", ""),
        last_name=request.POST.get("last_name", ""),
        email=request.POST.get("email", ""),
        phone=request.POST.get("phone", ""),
        telegram=telegram_handle,
        country=request.POST.get("country", ""),
        city=request.POST.get("city", ""),
        address=request.POST.get("address", ""),
        postcode=request.POST.get("postcode", ""),
        promo_code=promo_code,
        discount=discount,
        shipping_method=shipping_method,
        shipping_price=shipping_price,
        payment_method=payment_method,
    )

    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            price=item["product"].price,
            qty=item["qty"],
            size=item.get("size") or "",
            color_id=item.get("color"),
        )

    send_order_confirmation(order)
    notify_admin_new_order(order)

    total_to_pay = cart.total_price() + shipping_price - discount
    cart.clear()

    # ─── платёж картой через T-Bank ───────────────────────────────
    if payment_method == "card" and not settings.DEBUG:
        # чек по 54-ФЗ
        receipt = {
            "Email": order.email,
            "Taxation": "usn_income",
            "Items": [
                {
                    "Name": f"Order #{order.id}",
                    "Price": int(total_to_pay * 100),
                    "Quantity": 1,
                    "Amount": int(total_to_pay * 100),
                    "Tax": "vat20",
                }
            ],
        }

        resp = tbank_gateway.init_payment(
            order_id=str(order.id),
            amount_rub=total_to_pay,
            description=f"Заказ #{order.id}",
            receipt=receipt,
            success_url=request.build_absolute_uri(
                reverse("checkout:success", args=[order.id])
            ),
            fail_url=request.build_absolute_uri(
                reverse("checkout:failure", args=[order.id])
            ),
        )

        # сохраняем PaymentId в БД
        TBankPayment.objects.create(
            order=order,
            payment_id=resp["PaymentId"],
            amount=resp["Amount"],
            status=resp["Status"],
            raw_response=resp,
        )

        return redirect(resp["PaymentURL"])

    # ─── DEBUG или «Оплата при получении» ─────────────────────────
    return redirect(reverse("checkout:success", args=[order.id]))


# ────────────────────────────────────────────────────────────────
# 3. /checkout/success/<order_id>/
# ────────────────────────────────────────────────────────────────
def payment_success(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    return render(request, "checkout/success.html", {"order": order})


# ────────────────────────────────────────────────────────────────
# 4. /checkout/failure/<order_id>/  (для FailURL)
# ────────────────────────────────────────────────────────────────
def payment_failure(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    return render(request, "checkout/failure.html", {"order": order})


# ────────────────────────────────────────────────────────────────
# 5. /checkout/status/<order_id>/
# ────────────────────────────────────────────────────────────────
def order_status(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)
    items = order.items.all()
    items_total = sum(i.total() for i in items)

    return render(
        request,
        "checkout/order_status.html",
        {
            "order": order,
            "items": items,
            "items_total": items_total,
        },
    )