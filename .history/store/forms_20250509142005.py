from django import forms
from .models import Subscriber


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscriber
        fields = ("email",)
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Ваш e‑mail",
                    "autocomplete": "email",
                    "required": True,
                    "class": "newsletter-input",
                }
            )
        }