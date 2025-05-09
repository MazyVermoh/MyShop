# checkout/models.py

from django.db import models
from decimal import Decimal
from django.utils import timezone


class PromoCode(models.Model):
    """
    Промокод либо даёт процентную скидку от суммы,
    либо фиксированную скидку в рублях.
    """
    PERCENT = 'percent'
    FIXED   = 'fixed'

    TYPE_CHOICES = [
        (PERCENT, 'Процентная скидка'),
        (FIXED,   'Фиксированная сумма'),
    ]

    code        = models.CharField(
        'Код', max_length=30, unique=True,
        help_text='Уникальный промокод (без пробелов).'
    )
    discount    = models.DecimalField(
        'Скидка', max_digits=7, decimal_places=2,
        help_text='Процент (0–100) или сумма в рублях в зависимости от типа.'
    )
    type        = models.CharField(
        'Тип скидки', max_length=10,
        choices=TYPE_CHOICES, default=PERCENT
    )
    active      = models.BooleanField(
        'Активен', default=True,
        help_text='Сможет ли клиент применить этот код.'
    )
    valid_from  = models.DateTimeField(
        'Действует с', default=timezone.now
    )
    valid_to    = models.DateTimeField(
        'Действует до', null=True, blank=True,
        help_text='Если пусто — действует бессрочно после valid_from.'
    )

    class Meta:
        verbose_name = 'Промокод'
        verbose_name_plural = 'Промокоды'
        ordering = ['-valid_from']

    def __str__(self):
        return self.code

    def is_valid(self) -> bool:
        """
        Проверяет, что код активен и находится в заданном диапазоне дат.
        """
        now = timezone.now()
        if not self.active or self.valid_from > now:
            return False
        if self.valid_to and now > self.valid_to:
            return False
        return True

    def calculate_discount(self, total_amount: Decimal) -> Decimal:
        """
        Возвращает сумму скидки (Decimal).
        Процентная — округляется до копеек, фиксированная — не больше total_amount.
        """
        if not self.is_valid():
            return Decimal('0.00')

        if self.type == self.PERCENT:
            # процентная скидка
            discount = (total_amount * self.discount / Decimal('100')).quantize(Decimal('0.01'))
            return discount
        else:
            # фиксированная сумма, не превышает total_amount
            return min(self.discount, total_amount)