from django import forms

from .models import LeadRequest


class LeadForm(forms.ModelForm):
    consent = forms.BooleanField(
        label="Согласие на обработку персональных данных",
        required=True,
        initial=True,
    )

    class Meta:
        model = LeadRequest
        fields = ["kind", "name", "phone", "email", "material", "message", "contact_method", "consent"]
        widgets = {
            "kind": forms.HiddenInput(),
            "name": forms.TextInput(attrs={"placeholder": "Ваше имя", "class": "form-control"}),
            "phone": forms.TextInput(attrs={"placeholder": "+7 (___) ___-__-__", "class": "form-control", "data-phone": "1"}),
            "email": forms.EmailInput(attrs={"placeholder": "E-mail (необязательно)", "class": "form-control"}),
            "material": forms.TextInput(attrs={"placeholder": "Материал или объём (например, брус 150×150, 5 м³)", "class": "form-control"}),
            "message": forms.Textarea(attrs={"placeholder": "Комментарий", "rows": 3, "class": "form-control"}),
            "contact_method": forms.Select(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = False
        self.fields["material"].required = False
        self.fields["message"].required = False
        self.fields["contact_method"].required = False
