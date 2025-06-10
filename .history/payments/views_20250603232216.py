# payments/views.py

from decimal import Decimal
import json
from http import HTTPStatus

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from payments import tbank                         # ← импорт нашего обёрточного модуля
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

    # рассчитаем итог к оплате (у вас в модели Order есть метод total(), а не total_price)
    to_pay_decimal: Decimal = order.total()

    # формируем чек (54-ФЗ)
    receipt = {
        "Email": order.email,
        "Taxation": "usn_income",
        "Items": [
            {
                "Name": f"Заказ #{order.id}",
                "Price": int(to_pay_decimal * 100),
                "Quantity": 1,
                "Amount": int(to_pay_decimal * 100),
                "Tax": "vat20",
            }
        ],
    }

    # строим URL для возврата после успешной оплаты и неуспешной
    success_url = request.build_absolute_uri(
        reverse("checkout:success", args=[order.id])
    )
    fail_url = request.build_absolute_uri(
        reverse("checkout:failure", args=[order.id])
    )

    # отправляем init-запрос в T-Bank
    resp = tbank.init_payment(
        order_id=str(order.id),
        amount_rub=float(to_pay_decimal),
        description=f"Заказ #{order.id}",
        receipt=receipt,
        success_url=success_url,
        fail_url=fail_url,
    )

    # сохраняем или обновляем запись в таблице TBankPayment
    pay_obj, _ = TBankPayment.objects.update_or_create(
        order=order,
        defaults={
            "payment_id":   resp["PaymentId"],
            "amount":       resp["Amount"],
            "status":       resp["Status"],
            "raw_response": resp,
        },
    )

    # редиректим пользователя на PaymentURL (для demo-режима это будет /payments/demo/pay/<uuid>)
    return redirect(resp["PaymentURL"])


# ─────────────────────────────────────────────────────────────────────────────
# 2) webhook от T-Bank
#    URL: /payments/tbank/webhook/
# ─────────────────────────────────────────────────────────────────────────────
@csrf_exempt
@require_http_methods(["POST"])
def tbank_webhook(request: HttpRequest) -> HttpResponse:
    # разбираем JSON-payload (T-Bank присылает application/json)
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("invalid-json")

    # проверяем подпись
    if not tbank.validate_webhook(payload):
        return HttpResponseBadRequest("bad-token")

    payment_id = payload.get("PaymentId")
    status     = payload.get("Status")

    if not payment_id or not status:
        return HttpResponseBadRequest("missing-fields")

    # находим запись платежа по payment_id
    try:
        payment = TBankPayment.objects.select_related("order").get(payment_id=payment_id)
    except TBankPayment.DoesNotExist:
        # чужой PaymentId — игнорируем
        return HttpResponse("ignored", status=HTTPStatus.OK)

    # обновляем статус и raw_response
    payment.status = status
    payment.raw_response = payload
    payment.save(update_fields=["status", "raw_response", "updated"])

    # если платеж прошёл — помечаем заказ как оплаченный
    if payment.is_successful():
        order = payment.order
        order.status = "paid"
        order.save(update_fields=["status", "updated"])

    return HttpResponse("OK", status=HTTPStatus.OK)