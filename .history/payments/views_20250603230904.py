# payments/views.py
from __future__ import annotations

from decimal import Decimal
from http import HTTPStatus

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from payments import tbank                         # ← ВАЖНО: правильный импорт
from payments.models import TBankPayment
from store.models import Order


# ─────────────────────────────────────────────────────────────────────────────
# 1) старт оплаты по кнопке «Оплатить»
#    URL: /payments/tbank/start/<order_id>/
# ─────────────────────────────────────────────────────────────────────────────
@require_http_methods(["GET"])
def tbank_start(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order, id=order_id)

    # если заказ уже оплачен — сразу на «Спасибо»
    if order.status == "paid":
        return redirect(reverse("checkout:success", args=[order.id]))

    # итоговая сумма (скидки / доставка / промокод — как у вас заведено)
    to_pay = Decimal(order.total_price) + Decimal(order.shipping_price) - Decimal(order.discount)

    # (54-ФЗ) чек — минимально-допустимый
    receipt = {
        "Email": order.email,
        "Taxation": "usn_income",
        "Items": [{
            "Name": f"Order #{order.id}",
            "Price": int(to_pay * 100),
            "Quantity": 1,
            "Amount": int(to_pay * 100),
            "Tax": "none",
        }],
    }

    resp = tbank.init_payment(
        order_id=str(order.id),
        amount_rub=float(to_pay),
        description=f"Заказ #{order.id}",
        receipt=receipt,
        success_url=request.build_absolute_uri(
            reverse("checkout:success", args=[order.id])
        ),
        fail_url=request.build_absolute_uri(
            reverse("checkout:failure", args=[order.id])
        ),
    )

    # сохраняем / обновляем запись PaymentId
    pay_obj, _ = TBankPayment.objects.update_or_create(
        order=order,
        defaults={
            "payment_id": resp["PaymentId"],
            "amount":     resp["Amount"],
            "status":     resp["Status"],
            "raw_response": resp,
        },
    )

    # для demo-режима вернётся фейковый URL «/payments/demo/pay/<uuid>»
    return redirect(resp["PaymentURL"])


# ─────────────────────────────────────────────────────────────────────────────
# 2) webhook от T-Bank
#    URL: /payments/tbank/webhook/
# ─────────────────────────────────────────────────────────────────────────────
@csrf_exempt                            # T-Bank не присылает CSRF-cookie
@require_http_methods(["POST"])
def tbank_webhook(request: HttpRequest) -> HttpResponse:
    try:
        payload: dict = request.json if hasattr(request, "json") else request.body
        if isinstance(payload, (bytes, bytearray)):
            import json
            payload = json.loads(payload)
    except Exception:
        return HttpResponseBadRequest("invalid-json")

    # проверяем подпись
    if not tbank.validate_webhook(payload):
        return HttpResponseBadRequest("bad-token")

    payment_id = payload.get("PaymentId")
    status     = payload.get("Status")

    if not payment_id or not status:
        return HttpResponseBadRequest("missing-fields")

    try:
        payment = TBankPayment.objects.select_related("order").get(payment_id=payment_id)
    except TBankPayment.DoesNotExist:
        # не наш платёж — молча игнорируем
        return HttpResponse("ignored", status=HTTPStatus.OK)

    # обновляем запись платежа
    payment.status = status
    payment.raw_response = payload
    payment.save(update_fields=["status", "raw_response", "updated"])

    # успешная оплата → помечаем заказ
    if status in {"CONFIRMED", "AUTHORIZED"}:
        order = payment.order
        order.status = "paid"
        order.save(update_fields=["status", "updated"])

    return HttpResponse("OK", status=HTTPStatus.OK)