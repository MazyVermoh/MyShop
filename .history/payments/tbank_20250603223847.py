"""
payments/tbank.py
~~~~~~~~~~~~~~~~~
Мини-обёртка над HTTP-API T-Bank.

Режимы:
    TBANK_MODE=demo   → ничего не вызывает, отдаёт «фейковые» ответы для локальной разработки.
    TBANK_MODE=prod   → реальные HTTPS-запросы в банк.

Функции:
    init_payment(...)
    get_payment_status(...)
    validate_webhook(...)
"""

from __future__ import annotations

import hashlib
import json
import uuid
from typing import Any, Dict

import requests
from django.conf import settings


# ----------------------------------------------------------------------
#  Настройки / константы
# ----------------------------------------------------------------------
API_URL = "https://securepay.tinkoff.ru/v2/"           # при необходимости измените
_TIMEOUT = 15                                          # секунд


# ----------------------------------------------------------------------
#  Вспом. функции
# ----------------------------------------------------------------------
def _sign(data: Dict[str, Any]) -> str:
    """
    Генерируем SHA-256 подпись так же, как того требует T-Bank:
    • Берём ВСЕ поля, кроме Token, Receipt, DATA.
    • Сортируем по ключу.
    • Склеиваем значения + пароль.
    """
    pieces: list[str] = [
        str(data.get(k, "")) for k in sorted(data.keys())
        if k not in ("Token", "Receipt", "DATA")
    ]
    pieces.append(settings.TBANK_PASSWORD)
    return hashlib.sha256("".join(pieces).encode()).hexdigest()


def _post(method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """ Унифицированный POST → JSON. """
    url = f"{API_URL}{method}"
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, json=payload, headers=headers, timeout=_TIMEOUT)
    resp.raise_for_status()
    return resp.json()


# ----------------------------------------------------------------------
#  Публичный API
# ----------------------------------------------------------------------
def init_payment(
    *,
    order_id: str,
    amount_rub: float,
    description: str,
    receipt: Dict[str, Any] | None = None,
    success_url: str,
    fail_url: str,
) -> Dict[str, Any]:
    """
    Шлём запрос /Init и получаем:
        {Success, PaymentId, Amount, Status, PaymentURL, ...}
    В demo-режиме генерируем заглушку локально.
    """
    if settings.TBANK_MODE.lower() == "demo":
        payment_id = str(uuid.uuid4())
        return {
            "Success": True,
            "PaymentId": payment_id,
            "Amount": int(amount_rub * 100),
            "Status": "NEW",
            "PaymentURL": f"/payments/demo/pay/{payment_id}",   # фиктивный URL
        }

    payload: Dict[str, Any] = {
        "TerminalKey": settings.TBANK_TERMINAL_KEY,
        "OrderId": order_id,
        "Amount": int(amount_rub * 100),        # копейки
        "Description": description,
        "SuccessURL": success_url,
        "FailURL": fail_url,
    }
    if receipt:
        payload["Receipt"] = receipt

    payload["Token"] = _sign(payload)
    return _post("Init", payload)


def get_payment_status(payment_id: str) -> Dict[str, Any]:
    """
    /GetState — узнаём текущее состояние платежа.
    В demo-режиме всегда «CONFIRMED».
    """
    if settings.TBANK_MODE.lower() == "demo":
        return {
            "Success": True,
            "PaymentId": payment_id,
            "Status": "CONFIRMED",
            "Amount": None,
        }

    payload = {
        "TerminalKey": settings.TBANK_TERMINAL_KEY,
        "PaymentId": payment_id,
    }
    payload["Token"] = _sign(payload)
    return _post("GetState", payload)


def validate_webhook(data: Dict[str, Any]) -> bool:
    """
    Проверяем Token, который T-Bank положил в POST-webhook.
    """
    return data.get("Token") == _sign(data)