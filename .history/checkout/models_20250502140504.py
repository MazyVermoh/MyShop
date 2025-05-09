from django.db import models
from decimal import Decimal

class PromoCode(models.Model):
    """
    Промокод либо даёт фиксированную скидку в рублях,
    либо процентную скидку от суммы.
    """
    code = models.CharField("Код", max_length=30, unique=True)
    discount_percent = models.PositiveSmallIntegerField(
        "Скидка %", null=True, blank=True,
        help_text="Если задать, то это процент от суммы заказа."
    )
    discount_amount = models.DecimalField(
        "Скидка ₽", max_digits=10, decimal_places=2,
        null=True, blank=True,
        help_text="Если задана, то фиксированная сумма в рублях."
    )
    active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code

    def calculate_discount(self, total: Decimal) -> Decimal:
        """
        Вычисляет величину скидки для заданного total.
        """
        if not self.active:
            return Decimal("0")
        if self.discount_amount:
            # не больше, чем сумма
            return min(self.discount_amount, total)
        if self.discount_percent:
            return (total * Decimal(self.discount_percent) / Decimal("100")).quantize(Decimal("0.01"))
        return Decimal("0")