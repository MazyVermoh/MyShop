# payments/models.py
from django.db import models


class TBankPayment(models.Model):
    """
    Хранит информацию о транзакции T-Банка, связанной с заказом.
    Суммы — всегда в копейках (целые int).
    """

    # связь «один к одному» с моделью заказа
    order = models.OneToOneField(
        "checkout.Order",
        on_delete=models.CASCADE,
        related_name="tbank_payment",
    )

    payment_id = models.BigIntegerField(unique=True)  # ID, который вернул /v2/Init
    amount = models.PositiveIntegerField()            # сумма в копейках
    status = models.CharField(max_length=24)          # NEW | CONFIRMED | REJECTED …
    raw_response = models.JSONField()                 # полный JSON ответа Init

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created",)
        verbose_name = "Платёж T-Bank"
        verbose_name_plural = "Платежи T-Bank"

    # ――― business helpers ―――――――――――――――――――――――――――――――――――――――――――――
    def is_successful(self) -> bool:
        """True, если оплата прошла успешно."""
        return self.status in ("CONFIRMED", "AUTHORIZED", "PAYED")

    def __str__(self) -> str:  # noqa: DunderStr
        return f"{self.order.id} / {self.payment_id} / {self.status}"