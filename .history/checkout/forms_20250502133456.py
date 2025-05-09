# checkout/forms.py
from django import forms
from store.models import PromoCode
from decimal import Decimal

class PromoCodeApplyForm(forms.Form):
    code = forms.CharField(
        max_length=30,
        label='Промокод',
        widget=forms.TextInput(attrs={'placeholder': 'Введите промокод'})
    )

    def clean_code(self):
        code = self.cleaned_data['code'].strip()
        try:
            promo = PromoCode.objects.get(code__iexact=code)
        except PromoCode.DoesNotExist:
            raise forms.ValidationError('Неверный промокод')
        if not promo.is_valid():
            raise forms.ValidationError('Промокод неактивен или истёк')
        return promo  # вместо строки — сам объект