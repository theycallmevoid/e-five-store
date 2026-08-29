import re

from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        min_length=2,
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Your full name", "autocomplete": "name"}),
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "0550 00 00 00", "inputmode": "tel", "autocomplete": "tel"}),
    )
    wilaya_id = forms.UUIDField(widget=forms.HiddenInput())
    commune_id = forms.UUIDField(widget=forms.HiddenInput())
    hub_id = forms.UUIDField(required=False, widget=forms.HiddenInput())
    address = forms.CharField(
        min_length=3,
        max_length=250,
        widget=forms.TextInput(attrs={"placeholder": "Street, district, number", "autocomplete": "street-address"}),
    )
    delivery_type = forms.ChoiceField(
        choices=(("home", "Home delivery"), ("pickup-point", "Pickup point")),
        widget=forms.RadioSelect,
    )

    def clean_phone(self):
        raw = self.cleaned_data["phone"].strip()
        digits = re.sub(r"\D", "", raw)
        if digits.startswith("213"):
            digits = digits[3:]
        if digits.startswith("0"):
            digits = digits[1:]
        if not re.fullmatch(r"[5-7]\d{8}", digits):
            raise forms.ValidationError("Enter a valid Algerian phone number.")
        return f"+213{digits}"

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("delivery_type") == "pickup-point" and not cleaned.get("hub_id"):
            self.add_error("hub_id", "Choose a pickup point.")
        return cleaned
