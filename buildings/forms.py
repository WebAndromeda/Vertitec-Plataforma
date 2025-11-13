from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from .models import buildings, towers

# Formulario para filtros del listado de edificios / clientes
class UserFilterForm(forms.Form):
    nombre = forms.CharField(
        required=False,
        label='Buscar por nombre',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nombre del edificio',
                'class': 'inputForm',
                'autocomplete':"off"
            }
        )
    )
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[
            ('activo', 'Activos'),
            ('inactivo', 'Inactivos'),
            ('todos', 'Todos')
        ],
        initial='activo',  # Por defecto muestra solo activos
        widget=forms.Select(attrs={'class': 'inputForm'})
    )

# Formulario para crear o editar un edificio / cliente
class buildingsForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'inputForm'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        required=False,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirmar contraseña',
            'class': 'inputForm'
        })
    )
    address = forms.CharField(
        label='Dirección',
        required=True,
        widget=forms.TextInput(attrs={
            'placeholder': 'Dirección',
            'class': 'inputForm'
        })
    )

    # 🔹 Campos opcionales para torres
    tower1 = forms.CharField(
        label='Torre 1 (opcional)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Nombre de la torre 1'})
    )
    tower2 = forms.CharField(
        label='Torre 2 (opcional)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Nombre de la torre 2'})
    )
    tower3 = forms.CharField(
        label='Torre 3 (opcional)',
        required=False,
        widget=forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Nombre de la torre 3'})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Usuario'}),
            'email': forms.EmailInput(attrs={'class': 'inputForm', 'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Nombre'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        self.building_instance = kwargs.pop('building_instance', None)
        super().__init__(*args, **kwargs)

        if self.is_update:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
            if self.building_instance:
                self.fields['address'].initial = self.building_instance.address
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if (password1 or password2) and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        if not self.is_update and not password1:
            self.add_error('password1', 'Este campo es obligatorio.')
        if not self.is_update and not password2:
            self.add_error('password2', 'Este campo es obligatorio.')

        if not cleaned_data.get('address'):
            self.add_error('address', 'Este campo es obligatorio.')

        return cleaned_data

    def save(self, commit=True):
        # Guardar el usuario
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.password = make_password(password)
        if commit:
            user.save()

        # Guardar o actualizar building
        if self.building_instance:
            building = self.building_instance
        else:
            building = buildings()

        building.user = user
        building.address = self.cleaned_data['address']

        if commit:
            building.save()

            # 🔹 Crear torres si se especificaron
            torres_creadas = False
            for i in range(1, 4):
                tower_name = self.cleaned_data.get(f'tower{i}')
                if tower_name:
                    towers.objects.create(building=building, name=tower_name)
                    torres_creadas = True

            # 🔹 Si no se creó ninguna torre, crear una por defecto
            if not torres_creadas:
                nombre_torre = f"Torre {building.user.first_name}"
                towers.objects.create(building=building, name=nombre_torre)

        return building


# Formulario para añadir una torre a un edificio / cliente
class towerForm(forms.ModelForm):
    class Meta:
        model = towers
        fields = ['name', 'building']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'inputForm',
                'placeholder': 'Nombre de la torre'
            }),
            'building': forms.Select(attrs={
                'class': 'inputForm'
            })
        }
        labels = {
            'name': 'Nombre de la Torre',
            'building': 'Edificio'
        }