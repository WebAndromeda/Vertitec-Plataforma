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
            "fecha",
            "numero_cotizacion",
            "nameItem",
            "cantidad",
            "precio_unitario",
            "status_Install",
            "approved_status",
            "tower",
        ]

        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "inputForm"}),
            "numero_cotizacion": forms.NumberInput(attrs={"class": "inputForm", "placeholder": "No. Cotización"}),
            "nameItem": forms.TextInput(attrs={"class": "inputForm", "placeholder": "Nombre del repuesto"}),
            "cantidad": forms.NumberInput(attrs={"class": "inputForm", "min": "1"}),
            "precio_unitario": forms.NumberInput(attrs={"class": "inputForm", "step": "0.01", "placeholder": "Precio unitario (SIN IVA)"}),
            "status_Install": forms.Select(attrs={"class": "inputForm"}),
            "approved_status": forms.Select(attrs={"class": "inputForm"}),
            "tower": forms.Select(attrs={"class": "inputForm"}),
        }

    # Calcular precio_total automáticamente
    def clean(self):
        cleaned_data = super().clean()
        cantidad = cleaned_data.get("cantidad")
        precio_unitario = cleaned_data.get("precio_unitario")

        if cantidad is not None and precio_unitario is not None:
            cleaned_data["precio_total"] = cantidad * precio_unitario

        return cleaned_data

