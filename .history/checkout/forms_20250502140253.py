# checkout/forms.py

from decimal import Decimal
from django import forms
from .models import PromoCode  # Вашу модель промокодов

class PromoCodeApplyForm(forms.Form):
    code = forms.CharField(
        label="Промокод",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Введите код"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # сюда сохранится найденный объект промокода
        self.promo = None

    def clean_code(self):
        code = self.cleaned_data["code"].strip()
        try:
            # ищем активный промокод (поле active=True)
            self.promo = PromoCode.objects.get(code__iexact=code, active=True)
        except PromoCode.DoesNotExist:
            raise forms.ValidationError("Неверный или неактивный промокод")
        return code

    def get_discount(self, total: Decimal) -> Decimal:
        """
        Возвращает сумму скидки для переданной общей стоимости total.
        Если тип скидки — процент, считаем процент, иначе — фиксированная сумма.
        """
        if not self.promo:
            return Decimal("0")
        # Предполагаем, что в модели PromoCode есть поля:
        #   discount_type — "percent" или "fixed"
        #   discount_value — Decimal
        if self.promo.discount_type == PromoCode.DISCOUNT_PERCENT:
            # процент от total
            raw = total * self.promo.discount_value / Decimal("100")
            return raw.quantize(Decimal("0.01"))
        # фиксированная сумма
        return min(self.promo.discount_value, total)