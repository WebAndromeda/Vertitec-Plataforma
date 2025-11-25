from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password

# Formulario para filtros del listado de usuarios técnicos y administradores
class UserFilterForm(forms.Form):
    nombre = forms.CharField(
        required=False,
        label='Buscar por nombre',
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Nombre del usuario',
                'class': 'inputForm',
                'autocomplete':"off"
            }
        )
    )
    rol = forms.ChoiceField(
        required=False,
        label='Rol',
        choices=[
            ('', 'Cualquiera'),
            ('Administrador', 'Administrador'),
            ('Técnico', 'Técnico')
        ],
        widget=forms.Select(attrs={'class': 'inputForm'})
    )
    estado = forms.ChoiceField(
        required=False,
        label='Estado',
        choices=[
            ('activo', 'Activos'),
            ('inactivo', 'Inactivos'),
            ('todos', 'Todos')
        ],
        initial='activo',
        widget=forms.Select(attrs={'class': 'inputForm'})
    )


# Formulario para crear / editar un usuario
class UnifiedUserForm(forms.ModelForm):
    # Campos adicionales
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

    ROLE_CHOICES = [
        ('tecnico', 'Técnico'),
        ('admin', 'Administrador'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='Rol',
        widget=forms.Select(attrs={'class': 'inputForm'}),
        required=True
    )

    class Meta:
        model = User
        # 🚨 Email eliminado del formulario
        fields = ['username', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Usuario'}),
            'first_name': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Apellido'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)

        if self.is_update:
            # Campos no obligatorios al editar
            self.fields['password1'].required = False
            self.fields['password2'].required = False

            # Ocultar el campo de rol en edición
            current_group = self.instance.groups.first()
            if current_group:
                if current_group.name == 'Administrador':
                    self.fields['role'].initial = 'admin'
                elif current_group.name == 'Técnico':
                    self.fields['role'].initial = 'tecnico'

            self.fields['role'].widget = forms.HiddenInput()
            self.fields['role'].required = False
            self.fields['password1'].help_text = "Deja este campo vacío si no deseas cambiar la contraseña."

        else:
            # En creación todos los campos del formulario son obligatorios
            for field_name in self.fields:
                self.fields[field_name].required = True

            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].help_text = "Introduce una contraseña para el nuevo usuario."

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if not self.is_update:
            # En creación las contraseñas deben existir
            if not password1 or not password2:
                raise forms.ValidationError("Debes ingresar y confirmar la contraseña para crear un usuario nuevo.")

        # Si se ingresan, deben coincidir
        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')

        if password:
            user.password = make_password(password)

        if commit:
            user.save()

            # Asignar grupo según el rol solo en creación
            role = self.cleaned_data.get('role')
            if role:
                if role == 'admin':
                    group = Group.objects.get(name='Administrador')
                elif role == 'tecnico':
                    group = Group.objects.get(name='Técnico')
                else:
                    group = None

                if group:
                    user.groups.clear()
                    user.groups.add(group)

        return user



#Formulario para iniciar sesion
class loginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Usuario',
            'class': 'inputForm'
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Contraseña',
            'class': 'inputForm'
        })
    )