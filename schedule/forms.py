from django import forms
from django.contrib.auth.models import User
from .models import schedule
from buildings.models import towers
from buildings.models import buildings

# Formulario para filtros del listado de agendamientos por rango de fechas, tecnico, estado, nombre del edificio
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
    # Sobreescribimos el campo "client" para que sea un input de texto en lugar de un select
    client = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'inputForm',
                'placeholder': 'Nombre del edificio',
                'autocomplete': 'off',
                'id': 'buildingInput'  # este id sirve para enlazar el JS de autocompletado
            }
        )
    )

    class Meta:
        model = schedule
        fields = ['client', 'tower', 'date', 'hour', 'technician', 'status', 'recurrence']
        widgets = {
            'tower': forms.Select(attrs={'class': 'inputForm'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'inputForm', 'placeholder': 'Fecha'}),
            'hour': forms.TimeInput(attrs={'type': 'time', 'class': 'inputForm', 'placeholder': 'Hora'}),
            'technician': forms.Select(attrs={'class': 'inputForm', 'placeholder': 'Técnico'}),
            'status': forms.CheckboxInput(attrs={'class': 'inputForm', 'placeholder': 'Estado'}),
            'recurrence': forms.Select(attrs={'class': 'inputForm'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)

        # Filtramos los técnicos (se mantiene como select)
        self.fields['technician'].queryset = User.objects.filter(groups__name='Técnico')

        # Torres: de momento mostramos todas
        self.fields['tower'].queryset = towers.objects.all()

        # Inicializar campo 'client' con el nombre del cliente solo si no hay datos de POST
        if self.instance and self.instance.pk and not self.data:
            self.fields['client'].initial = self.instance.client.first_name

    def clean_client(self):
        """Validar que el texto ingresado corresponda a un cliente real"""
        nombre = self.cleaned_data['client'].strip()
        try:
            return User.objects.get(first_name__iexact=nombre, groups__name="Cliente")
        except User.DoesNotExist:
            raise forms.ValidationError("Cliente no válido, selecciona uno de la lista.")