from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.hashers import make_password

class UnifiedUserForm(forms.ModelForm):
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
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Usuario'}),
            'email': forms.EmailInput(attrs={'class': 'inputForm', 'placeholder': 'Correo electrónico'}),
            'first_name': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'class': 'inputForm', 'placeholder': 'Apellido'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_update = kwargs.pop('is_update', False)
        super().__init__(*args, **kwargs)

        if self.is_update:
            self.fields['password1'].required = False
            self.fields['password2'].required = False
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 or password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')

        if password:
            user.password = make_password(password)

        if commit:
            user.save()

            # Asignar grupo basado en el campo role
            selected_role = self.cleaned_data.get('role')

            if selected_role == 'admin':
                group = Group.objects.get(name='Administrador')
            elif selected_role == 'tecnico':
                group = Group.objects.get(name='Técnico')
            else:
                group = None

            if group:
                user.groups.clear()  # Elimina cualquier grupo previo
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




