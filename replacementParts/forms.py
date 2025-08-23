from django import forms
from .models import replacementParts

class replacementPartsForm(forms.ModelForm):
    class Meta:
        model = replacementParts
        fields = [
            "nameItem",
            "price",
            "approved",
            "status_Install",
            "status_Payment",
            "tower",
        ]  # 👈 quitamos "building"
        widgets = {
            "nameItem": forms.TextInput(attrs={"class": "inputForm", "placeholder": "Nombre del repuesto"}),
            "price": forms.NumberInput(attrs={"class": "inputForm", "placeholder": "Precio"}),
            "approved": forms.CheckboxInput(attrs={"class": "inputForm"}),
            "status_Install": forms.Select(attrs={"class": "inputForm"}),
            "status_Payment": forms.Select(attrs={"class": "inputForm"}),
            "tower": forms.Select(attrs={"class": "inputForm"}),
        }  # 👈 quitamos también el widget de "building"

