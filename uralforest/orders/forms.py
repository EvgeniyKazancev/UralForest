from django import forms

from .models import Order


class CheckoutForm(forms.ModelForm):
    consent = forms.BooleanField(label="Согласие на обработку персональных данных", required=True, initial=True)

    class Meta:
        model = Order
        fields = [
            "customer_name", "phone", "email", "company", "comment",
            "delivery_method", "address", "payment_method", "consent",
        ]
        widgets = {
            "customer_name": forms.TextInput(attrs={"placeholder": "Ваше имя", "class": "form-control"}),
            "phone": forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__", "class": "form-control", "data-phone": "1"}),
            "email": forms.EmailInput(attrs={"placeholder": "E-mail", "class": "form-control"}),
            "company": forms.TextInput(attrs={"placeholder": "Компания (для юрлиц)", "class": "form-control"}),
            "comment": forms.Textarea(attrs={"placeholder": "Комментарий к заказу", "rows": 3, "class": "form-control"}),
            "delivery_method": forms.Select(attrs={"class": "form-control"}),
            "address": forms.TextInput(attrs={"placeholder": "Адрес доставки", "class": "form-control"}),
            "payment_method": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False
        self.fields["company"].required = False
        self.fields["comment"].required = False
        self.fields["address"].required = False
        self.fields["payment_method"].choices = Order.PaymentMethod.choices
