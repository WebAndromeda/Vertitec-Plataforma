from django import forms
from django.contrib.auth.models import User
from .models import schedule
from buildings.models import towers
from buildings.models import buildings
from datetime import datetime, timedelta





# Formulario para filtros del listado de agendamientos por rango de fechas, tecnico, nombre del edificio y estado
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


# Formulario para crear / editar un agendamiento
class ScheduleForm(forms.ModelForm):
    client = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'inputForm',
            'placeholder': 'Nombre del edificio',
            'autocomplete': 'off',
            'id': 'buildingInput'
        })
    )

    technician = forms.ModelChoiceField(
        queryset=User.objects.none(),  # vacío por defecto, se llenará en __init__
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
        self.is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)

        # 🔹 Filtrar solo los usuarios que están en el grupo “Técnico”
        self.fields['technician'].queryset = User.objects.filter(groups__name='Técnico').order_by('first_name')

        # 🔹 Cargar todas las torres (ajusta si quieres filtrar por cliente)
        self.fields['tower'].queryset = towers.objects.all()

        # 🔹 Mostrar el nombre del cliente si es edición
        if self.instance and self.instance.pk and not self.data:
            self.fields['client'].initial = self.instance.client.first_name

    def clean_client(self):
        nombre = self.cleaned_data['client'].strip()
        try:
            return User.objects.get(first_name__iexact=nombre, groups__name="Cliente")
        except User.DoesNotExist:
            raise forms.ValidationError("Cliente no válido, selecciona uno de la lista.")

    def clean(self):
        cleaned_data = super().clean()
        technician = cleaned_data.get('technician')
        date = cleaned_data.get('date')
        hour = cleaned_data.get('hour')

        if not (technician and date and hour):
            return cleaned_data

        new_dt = datetime.combine(date, hour)

        # ❌ Conflicto exacto
        conflict_qs = schedule.objects.filter(technician=technician, date=date, hour=hour)
        if self.instance.pk:
            conflict_qs = conflict_qs.exclude(pk=self.instance.pk)
        if conflict_qs.exists():
            raise forms.ValidationError(
                f"❌ El técnico {technician.first_name} ya tiene un agendamiento a esa hora."
            )

        # ⚠️ Advertencia si hay otro a menos de una hora
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
                f"(por ejemplo a las {', '.join(advertencias)}). "
                f"Haz clic nuevamente en Crear agendamiento para agendarlo de todas formas."
            )

        return cleaned_data