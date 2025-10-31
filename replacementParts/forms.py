from django import forms
from django.contrib.auth.models import User
from .models import replacementParts

# Formulario para filtros del listado de repuestos
class ReplacementPartsFilterForm(forms.Form):
    fecha_inicio = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "inputForm"
        }),
        label="Desde"
    )
    fecha_fin = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date",
            "class": "inputForm"
        }),
        label="Hasta"
    )

    status_Install = forms.ChoiceField(
        choices=[('', '---------')] + replacementParts.statusInstall,
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"}),
        label="Estado instalación"
    )

    status_Payment = forms.ChoiceField(
        choices=[('', '---------')] + replacementParts.statusPayment,
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"}),
        label="Estado pago"
    )

    tecnico = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Técnico"),
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"}),
        label="Técnico"
    )

    edificio = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Cliente"),
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"}),
        label="Edificio"
    )


# Formulario para creación de un repuesto
class replacementPartsForm(forms.ModelForm):
    class Meta:
        model = replacementParts
        fields = [
            "nameItem",
            "price",
            "status_Install",
            "status_Payment",
            "tower",
        ]
        widgets = {
            "nameItem": forms.TextInput(attrs={"class": "inputForm", "placeholder": "Nombre del repuesto"}),
            "price": forms.NumberInput(attrs={"class": "inputForm", "placeholder": "Precio"}),
            "status_Install": forms.Select(attrs={"class": "inputForm"}),
            "status_Payment": forms.Select(attrs={"class": "inputForm"}),
            "tower": forms.Select(attrs={"class": "inputForm"}),
        }

