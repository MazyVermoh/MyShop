from __future__ import annotations

"""payments/views.py
Webhook и (опционально) REST‑endpoint для T‑Bank.

Маршруты:
    /payments/tbank/webhook/  – банк шлёт уведомления POST

Чтобы протестировать вручную:
    curl -X POST https://<domain>/payments/tbank/webhook/ \
         -H "Content-Type: application/json" \
         -d '{"PaymentId":123,"OrderId":"12","Status":"CONFIRMED", ... , "Token":"..."}'
"""

import json
from http import HTTPStatus

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

from payments.gateway import tbank_gateway
from payments.models import TBankPayment
from checkout.models import Order


@csrf_exempt  # банк не умеет отправлять CSRF‑cookie
def tbank_webhook(request: HttpRequest) -> HttpResponse:
    """Получает POST‑уведомление от T‑Bank и обновляет статус оплаты."""

    if request.method != "POST":
        return HttpResponse(status=HTTPStatus.METHOD_NOT_ALLOWED)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("invalid json")

    # 1) проверяем Token
    token = payload.pop("Token", "")
    if token != tbank_gateway._calc_token(payload):  # pylint: disable=protected-access
        return HttpResponseBadRequest("wrong token")

    payment_id = payload.get("PaymentId")
    order_id = payload.get("OrderId")
    status = payload.get("Status")
    amount = payload.get("Amount")

    if not all([payment_id, order_id, status]):
        return HttpResponseBadRequest("missing fields")

    # 2) обновляем запись платежа
    try:
        pay = TBankPayment.objects.get(payment_id=payment_id)
    except TBankPayment.DoesNotExist:
        # безопасный fall‑through: игнорируем чужие PaymentId
        return HttpResponse("ignored", status=HTTPStatus.OK)

    pay.status = status
    pay.save(update_fields=["status", "updated"])

    # 3) если успешный платеж – помечаем заказ оплаченным
    if pay.is_successful():
        _mark_order_paid(pay.order, amount)

    return HttpResponse("OK")


def _mark_order_paid(order: Order, amount: int | None) -> None:
    """Хелпер: меняет статус заказа и пишет лог‑запись."""

    if hasattr(order, "status"):
        order.status = "paid"  # либо соответствующее поле в вашей модели
        order.save(update_fields=["status", "updated"])

    # при желании: отправить письмо клиенту, push‑нотификацию, …
