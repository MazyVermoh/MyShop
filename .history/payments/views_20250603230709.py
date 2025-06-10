from __future__ import annotations

"""
payments/views.py
~~~~~~~~~~~~~~~~~
-  /payments/tbank/start/<order_id>/  – (необязательно) принудительно создаёт платёж ещё раз
-  /payments/tbank/hook/             – веб-хук: T-Bank шлёт POST-уведомления

если нужен только веб-хук – route «start» можно убрать
"""

import json
from http import HTTPStatus
from typing import Any, Dict

from django.conf import settings
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseBadRequest,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_http_methods

from payments import tbank as tbank_gateway                       # ← наш wrapper
from payments.models import TBankPayment
from store.models import Order

# ----------------------------------------------------------------------
#  1. (опционально) ручной старт оплаты картой
# ----------------------------------------------------------------------
@require_http_methods(["GET"])
def tbank_start(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    Дать пользователю кнопку «Оплатить сейчас», если счёт был создан,
    но он передумал в моменте.  Вызывает /Init ещё раз и редиректит
    на platёжную форму T-Bank.

    Если вам не нужна эта функциональность – удалите весь view + маршрут.
    """
    order = get_object_or_404(Order, id=order_id)

    # заказ уже оплачен – сразу успешная страница
    if getattr(order, "status", "") == "paid":
        return redirect("checkout:success", order.id)

    # (re)-создаём платёж
    resp = tbank.init_payment(
        order_id=str(order.id),
        amount_rub=order.total_to_pay(),          # или иное поле
        description=f"Заказ #{order.id}",
        receipt=None,                             # сформируйте чек при желании
        success_url=request.build_absolute_uri(
            reverse("checkout:success", args=[order.id])
        ),
        fail_url=request.build_absolute_uri(
            reverse("checkout:failure", args=[order.id])
        ),
    )

    # сохраняем / обновляем запись в БД
    pay, _ = TBankPayment.objects.update_or_create(
        order=order,
        defaults={
            "payment_id": resp["PaymentId"],
            "amount": resp["Amount"],
            "status": resp["Status"],
            "raw_response": resp,
        },
    )
    pay.refresh_from_db()                         # на всякий случай

    return redirect(resp["PaymentURL"])


# ----------------------------------------------------------------------
#  2. веб-хук от банка
# ----------------------------------------------------------------------
@csrf_exempt                       # T-Bank не присылает CSRF-cookie
@require_POST
def tbank_hook(request: HttpRequest) -> HttpResponse:
    """
    Получаем POST-уведомление от T-Bank, валидируем Token,
    обновляем запись платежа + статус заказа.
    """

    # ---- разбираем тело ------------------------------------------------
    if request.META.get("CONTENT_TYPE", "").startswith("application/json"):
        try:
            data: Dict[str, Any] = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("invalid json")
    else:                                           # x-www-form-urlencoded
        data = request.POST.dict()

    # ---- валидируем подпись -------------------------------------------
    if not tbank.validate_webhook(data.copy()):     # .copy() → не портим dict
        return HttpResponseBadRequest("wrong token")

    payment_id = data.get("PaymentId")
    status     = data.get("Status")

    if not payment_id or not status:
        return HttpResponseBadRequest("missing fields")

    # ---- обновляем запись платёжа -------------------------------------
    try:
        payment = TBankPayment.objects.select_related("order").get(
            payment_id=payment_id
        )
    except TBankPayment.DoesNotExist:
        # чужой PaymentId – игнорируем, но отвечаем 200 (иначе банк ретраит)
        return HttpResponse("ignored", status=HTTPStatus.OK)

    payment.status       = status
    payment.raw_response = data
    payment.save(update_fields=["status", "raw_response", "updated"])

    # ---- успешный ли статус? ------------------------------------------
    SUCCESS_STATUSES = {"CONFIRMED", "AUTHORIZED", "COMPLETED"}

    if status in SUCCESS_STATUSES:
        _mark_order_paid(payment.order)

    return JsonResponse({"Success": True})


# ----------------------------------------------------------------------
#  Вспом-функции
# ----------------------------------------------------------------------
def _mark_order_paid(order: Order) -> None:
    """
    Переводим заказ в состояние «paid» (или ваше собственное),
    ничего не делаем, если уже оплачен.
    """
    if getattr(order, "status", "") == "paid":
        return

    order.status = "paid"
    order.save(update_fields=["status", "updated"])

    # 👉  тут можно:
    #   • отправить письмо клиенту
    #   • уведомить менеджера
    #   • вызвать любой другой post-processing