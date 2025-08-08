from django import forms
from django.contrib.auth.models import User
from .models import schedule
from buildings.models import buildings, towers

class ScheduleForm(forms.ModelForm):
    class Meta:
        model = schedule
        fields = ['client', 'tower', 'date', 'hour', 'technician', 'status']
        widgets = {
            'client': forms.Select(attrs={'class': 'inputForm'}),
            'tower': forms.Select(attrs={'class': 'inputForm'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'inputForm', 'placeholder': 'Fecha'}),
            'hour': forms.TimeInput(attrs={'type': 'time', 'class': 'inputForm', 'placeholder': 'Hora'}),
            'technician': forms.Select(attrs={'class': 'inputForm', 'placeholder': 'Técnico'}),
            'status': forms.CheckboxInput(attrs={'class': 'inputForm', 'placeholder': 'Estado'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super(ScheduleForm, self).__init__(*args, **kwargs)

        # Mostrar solo técnicos
        self.fields['technician'].queryset = User.objects.filter(groups__name='Técnico')

        # Mostrar todos los edificios
        self.fields['client'].queryset = User.objects.filter(groups__name='Cliente')
        self.fields['client'].label_from_instance = lambda obj: obj.first_name

        # TEMPORAL: Mostrar todas las torres sin importar el edificio
        self.fields['tower'].queryset = towers.objects.all()




"""
# Este codigo se puede utilizar para mostrar unicamente las torres que pertenecen al edificio seleccionado
class ScheduleForm(forms.ModelForm):
    class Meta:
        model = schedule
        fields = ['building', 'tower', 'date', 'hour', 'technician', 'status']
        widgets = {
            'building': forms.Select(attrs={'class': 'inputForm'}),
            'tower': forms.Select(attrs={'class': 'inputForm'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'inputForm', 'placeholder': 'Fecha'}),
            'hour': forms.TimeInput(attrs={'type': 'time', 'class': 'inputForm', 'placeholder': 'Hora'}),
            'technician': forms.Select(attrs={'class': 'inputForm', 'placeholder': 'Técnico'}),
            'status': forms.CheckboxInput(attrs={'class': 'inputForm', 'placeholder': 'Estado'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super(ScheduleForm, self).__init__(*args, **kwargs)

        self.fields['technician'].queryset = User.objects.filter(groups__name='Técnico')
        self.fields['building'].queryset = buildings.objects.all()

        # Si hay datos POST (intento de envío)
        if 'building' in self.data:
            try:
                building_id = int(self.data.get('building'))
                self.fields['tower'].queryset = towers.objects.filter(building_id=building_id)
            except (ValueError, TypeError):
                self.fields['tower'].queryset = towers.objects.none()
        # Si se está editando un objeto (update)
        elif self.instance.pk:
            self.fields['tower'].queryset = towers.objects.filter(building=self.instance.building)
        # Si no hay datos, dejamos el queryset vacío
        else:
            self.fields['tower'].queryset = towers.objects.none()

        ¿Como puedo hacer para que aqui?
        # Mostrar todos los edificios
        self.fields['building'].queryset = User.objects.filter(groups__name='Cliente')
        En lugar de mostrarme el username me muestre el firstname?

        Creo que hay un error conceptual aqui, en la tabla o modelo buildings, solo estan las direcciones de los edificios, conectados por una clave foranea al modelo prederminado de Django parar users, y no necesito ese dato en el formulario o en el modelo schdule, lo que necesito guardar en el modelo schedule es un usuario perteneciente al grupo de Cliente
"""
