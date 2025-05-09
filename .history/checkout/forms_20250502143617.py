from django import forms
from store.models import PromoCode

class PromoCodeApplyForm(forms.Form):
    code = forms.CharField(
        label="Промокод",
        max_length=30,
        widget=forms.TextInput(attrs={"placeholder": "Введите код"})
    )

    def clean_code(self):
        raw = self.cleaned_data["code"].strip()
        try:
            promo = PromoCode.objects.get(code__iexact=raw, active=True)
        except PromoCode.DoesNotExist:
            raise forms.ValidationError("Неверный или неактивный промокод")
        return promo  # возвращаем сразу объект PromoCode

    def get_discount(self, total):
        """
        После валидного clean_code вызывать:
            discount = form.get_discount(cart.total_price())
        """
        promo: PromoCode = self.cleaned_data["code"]
        return promo.calculate_discount(total)