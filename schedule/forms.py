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

    # Nombre del edificio
    building = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "inputForm",
            "placeholder": "Nombre del edificio",
            "autocomplete": "off"
        })
    )

    # NUEVO STATUS usando el modelo actual
    STATUS_CHOICES = [
        ("", "Todos"),                 # Sin filtro
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
            'status': forms.Select(attrs={'class': 'inputForm'}),  # CAMBIADO
            'recurrence': forms.Select(attrs={'class': 'inputForm'}),
        }

    def __init__(self, *args, **kwargs):
        # Se recibe self.user desde las vistas
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if not self.user:
            return

        # Filtrar técnicos
        self.fields['technician'].queryset = User.objects.filter(groups__name='Técnico').order_by('first_name')

        # Torres disponibles
        self.fields['tower'].queryset = towers.objects.all()

        # Si se está editando, cargar el nombre del cliente
        if self.instance and self.instance.pk and not self.data:
            self.fields['client'].initial = self.instance.client.first_name

        # Si es técnico → ocultar campos que no debe editar
        if self.user.groups.filter(name='Técnico').exists():
            for field in ['recurrence', 'technician', 'status']:
                self.fields.pop(field)

    # Validación del cliente
    def clean_client(self):
        nombre = self.cleaned_data['client'].strip()
        try:
            return User.objects.get(first_name__iexact=nombre, groups__name="Cliente")
        except User.DoesNotExist:
            raise forms.ValidationError("Cliente no válido, selecciona uno de la lista.")

    # Validación de conflictos de horario
    def clean(self):
        cleaned_data = super().clean()

        technician = cleaned_data.get('technician') or self.user
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

        # Advertencias por citas cercanas
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