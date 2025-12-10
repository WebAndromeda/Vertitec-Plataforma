from django import forms
from .models import Report
from django.contrib.auth.models import User

# Formulario para crear un reporte
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = [
            "general_observations",
            "special_recommendations",
        ]

        widgets = {
            "general_observations": forms.Textarea(attrs={
                "class": "inputForm"
            }),
            "special_recommendations": forms.Textarea(attrs={
                "class": "inputForm"
            }),
        }


# Formulario para usar filtros en la vista de reportes
class ReportFilterForm(forms.Form):
    # Fecha o rango de fechas
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "inputForm"})
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "inputForm"})
    )

    # Técnico asignado
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Técnico"),
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"})
    )

    # Nombre del edificio
    building = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "inputForm",
            "placeholder": "Nombre del edificio",
            "autocomplete": "off"
        })
    )

    # Estado del agendamiento
    STATUS_CHOICES = [
        ("", "Todos"),
        ("to_be_done", "Por realizar"),
        ("in_production", "En producción"),
        ("complete", "Realizado"),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"})
    )

    # Programado / No programado
    PROGRAMMED_CHOICES = [
        ("", "Todos"),
        ("programmed", "Programado"),
        ("not_programmed", "No programado"),
    ]
    programmed = forms.ChoiceField(
        choices=PROGRAMMED_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"})
    )
