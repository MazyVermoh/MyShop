"""
T-Bank (T-Касса) API wrapper.

------------------------
Минимальный набор методов:
    • init_payment()   – создание платежа (Init)
    • get_state()      – проверка статуса (GetState)
    • confirm()        – подтверждение 2-стадийной оплаты (Confirm)
    • cancel()         – полный или частичный возврат (Cancel)

Расчёт Token соответствует документации:
    SHA-256(конкатенация_непустых_параметров_по_алфавиту + Password)
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

import requests
from django.conf import settings


class TBankGateway:
    """
    Обёртка над REST-v2 T-Кассы.
    Используется как singleton: один экземпляр на всё приложение.
    """

    # Единая точка входа (для demo и prod одинаково)
    BASE_URL = "https://securepay.tinkoff.ru/v2/"

    def __init__(self, terminal_key: str, password: str, demo: bool = True) -> None:
        self.terminal_key = terminal_key
        self.password = password
        self.demo = demo

    # --------------------------------------------------------------------- #
    # Public API
    # --------------------------------------------------------------------- #
    def init_payment(
        self,
        *,
        order_id: str,
        amount_rub: float,
        description: str = "",
        receipt: dict | None = None,
        success_url: str = "",
        fail_url: str = "",
        **extra: Any,
    ) -> Dict[str, Any]:
        """
        Создаёт платёж и возвращает ответ /v2/Init.
        amount_rub → банк ожидает сумму *в копейках* (int).
        """

        payload: Dict[str, Any] = {
            "OrderId": order_id,
            "Amount": int(round(amount_rub * 100)),
            "Description": description[:250],
            "SuccessURL": success_url,
            "FailURL": fail_url,
            **extra,
        }
        if receipt:
            # Банку нужно JSON-строка, а не объект
            payload["Receipt"] = receipt

        return self._post("Init", payload)

    def get_state(self, payment_id: int) -> Dict[str, Any]:
        return self._post("GetState", {"PaymentId": payment_id})

    def confirm(self, payment_id: int, amount_rub: float | None = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"PaymentId": payment_id}
        if amount_rub is not None:
            payload["Amount"] = int(round(amount_rub * 100))
        return self._post("Confirm", payload)

    def cancel(self, payment_id: int, amount_rub: float | None = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"PaymentId": payment_id}
        if amount_rub is not None:
            payload["Amount"] = int(round(amount_rub * 100))
        return self._post("Cancel", payload)

    # --------------------------------------------------------------------- #
    # Internal helpers
    # --------------------------------------------------------------------- #
    def _post(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Формирует Token, отправляет POST и возвращает JSON-ответ.
        """

        url = f"{self.BASE_URL}{method}"

        # Банк требует TerminalKey в теле запроса
        payload["TerminalKey"] = self.terminal_key

        # Receipt (если был dict) нужно сериализовать в JSON-строку
        if isinstance(payload.get("Receipt"), dict):
            payload["Receipt"] = json.dumps(payload["Receipt"], ensure_ascii=False)

        payload["Token"] = self._calc_token(payload)

        response = requests.post(url, json=payload, timeout=15)
        response.raise_for_status()
        return response.json()

    def _calc_token(self, data: Dict[str, Any]) -> str:
        """
        Правила T-Bank:
          • исключаем поле Token
          • пропускаем пустые значения
          • сортируем ключи по алфавиту
          • конкатенируем значения + Password
          • SHA-256 → hex
        """

        # Приводим bool/None/числа к строкам
        prepared: list[tuple[str, str]] = []
        for k, v in data.items():
            if k == "Token" or v in (None, ""):
                continue
            prepared.append((k, str(v)))

        prepared.sort(key=lambda item: item[0])
        concatenated = "".join(v for _, v in prepared) + self.password
        return hashlib.sha256(concatenated.encode()).hexdigest()


# ------------------------------------------------------------------------- #
# Singleton-инстанс, готовый к использованию в проекте
# ------------------------------------------------------------------------- #

tbank_gateway = TBankGateway(
    terminal_key=settings.TBANK_TERMINAL_KEY,
    password=settings.TBANK_PASSWORD,
    demo=settings.TBANK_MODE == "demo",
)