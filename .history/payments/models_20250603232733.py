# payments/models.py
from django.db import models


class TBankPayment(models.Model):
    order = models.OneToOneField(
        "store.Order",
        on_delete=models.CASCADE,
        related_name="tbank_payment",
    )

    # ← было BigIntegerField / PositiveIntegerField
    payment_id = models.CharField(              # UUID или int-строка
        max_length=64, unique=True
    )

    amount       = models.PositiveIntegerField()   # копейки
    status       = models.CharField(max_length=24)
    raw_response = models.JSONField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering            = ("-created",)
        verbose_name        = "Платёж T-Bank"
        verbose_name_plural = "Платежи T-Bank"

    # helpers
    def is_successful(self) -> bool:
        return self.status in ("CONFIRMED", "AUTHORIZED", "PAYED")

    def __str__(self):
        return f"{self.order_id} / {self.payment_id} / {self.status}"