from django import forms
from django.contrib.auth.models import User
from .models import schedule
from buildings.models import towers
from buildings.models import buildings
from datetime import datetime, timedelta


# Formulario para filtros del listado de agendamientos por rango de fechas, técnico, nombre del edificio, estado y programación
class ScheduleFilterForm(forms.Form):
    # Filtro por rango de fechas
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date", "class": "inputForm"
        })
    )
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            "type": "date", "class": "inputForm"
        })
    )

    # Técnico asignado
    technician = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name="Técnico"),
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"})
    )

    # Nombre del edificio (texto libre)
    building = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "inputForm",
            "placeholder": "Nombre del edificio",
            "autocomplete": "off"
        })
    )

    # Estado (status: BooleanField)
    STATUS_CHOICES = [
        ("", "Todos"),         # No aplica filtro
        ("true", "Realizado"),
        ("false", "Por realizar"),
    ]
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"})
    )

    # Programado o no programado
    PROGRAMMED_CHOICES = [
        ("", "Todos"),                # Sin filtro
        ("programmed", "Programado"),
        ("not_programmed", "No programado"),
    ]
    programmed = forms.ChoiceField(
        choices=PROGRAMMED_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "inputForm"})
    )



# Formulario para crear / editar un agendamiento
class ScheduleForm(forms.ModelForm):
    client = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'inputForm',
            'placeholder': 'Nombre del cliente',
            'autocomplete': 'off',
            'id': 'buildingInput'
        })
    )

    technician = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.Select(attrs={'class': 'inputForm'}),
        label="Técnico"
    )

    class Meta:
        model = schedule
        fields = ['client', 'tower', 'date', 'hour', 'technician', 'status', 'recurrence']
        widgets = {
            'tower': forms.Select(attrs={'class': 'inputForm'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'inputForm'}),
            'hour': forms.TimeInput(attrs={'type': 'time', 'class': 'inputForm'}),
            'status': forms.CheckboxInput(attrs={'class': 'inputForm'}),
            'recurrence': forms.Select(attrs={'class': 'inputForm'}),
        }

    def __init__(self, *args, **kwargs):
        # FIX PARA EL KEYERROR
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Si por alguna razón no viene user, no ejecutar nada más
        if not self.user:
            return

        # Filtrar técnicos y torres
        self.fields['technician'].queryset = User.objects.filter(groups__name='Técnico').order_by('first_name')
        self.fields['tower'].queryset = towers.objects.all()

        # Si se está editando, colocar el nombre del cliente
        if self.instance and self.instance.pk and not self.data:
            self.fields['client'].initial = self.instance.client.first_name

        # Si es técnico, ocultar campos que no debe ver
        if self.user.groups.filter(name='Técnico').exists():
            for field in ['recurrence', 'technician', 'status']:
                self.fields.pop(field)

    def clean_client(self):
        nombre = self.cleaned_data['client'].strip()
        try:
            return User.objects.get(first_name__iexact=nombre, groups__name="Cliente")
        except User.DoesNotExist:
            raise forms.ValidationError("Cliente no válido, selecciona uno de la lista.")

    def clean(self):
        cleaned_data = super().clean()
        technician = cleaned_data.get('technician') or self.user  # si es técnico, se asigna self.user
        date = cleaned_data.get('date')
        hour = cleaned_data.get('hour')

        if not (technician and date and hour):
            return cleaned_data

        new_dt = datetime.combine(date, hour)

        # Conflicto exacto
        conflict_qs = schedule.objects.filter(technician=technician, date=date, hour=hour)
        if self.instance.pk:
            conflict_qs = conflict_qs.exclude(pk=self.instance.pk)
        if conflict_qs.exists():
            raise forms.ValidationError(
                f"❌ El técnico {technician.first_name} ya tiene un agendamiento a esa hora."
            )

        # Advertencia si hay otro a menos de una hora
        nearby = schedule.objects.filter(technician=technician, date=date).exclude(hour=hour)
        advertencias = []
        for other in nearby:
            other_dt = datetime.combine(other.date, other.hour)
            diff_seconds = abs((other_dt - new_dt).total_seconds())
            if diff_seconds < 3600:
                advertencias.append(other.hour.strftime('%H:%M'))

        if advertencias:
            cleaned_data['__warning__'] = (
                f"⚠️ El técnico tiene otro agendamiento a menos de una hora "
                f"(Exactamente a las {', '.join(advertencias)})."
            )

        return cleaned_data
