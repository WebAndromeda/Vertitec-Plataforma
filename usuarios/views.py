from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from .forms import loginForm, UnifiedUserForm, UserFilterForm
from django.core.paginator import Paginator
from django.contrib import messages


# Autocompletado de nombre real
@admin_required
def user_suggestions(request):
    query = request.GET.get('q', '')  # texto escrito
    suggestions = []

    if query:
        # Buscar por nombre de pila (first_name) en admins y técnicos
        usuarios = User.objects.filter(
            groups__name__in=['Administrador', 'Técnico'],
            first_name__icontains=query
        ).distinct()[:5]  # limitar a 5 resultados

        # Devolver solo el nombre real (Se podria concatenar con apellido en el futuro)
        suggestions = list(
            usuarios.values_list('first_name', flat=True)
        )

    return JsonResponse(suggestions, safe=False)


# Index
def index(request):
    return render(request, 'index.html')


# Vistas para CRUD de usuarios
# Vista para crear un usuario  
@admin_required
def createUser(request):
    if request.method == "POST":
        form = UnifiedUserForm(request.POST, is_update=False)
        if form.is_valid():
            user = form.save()  # Guardamos el usuario y lo almacenamos en una variable
            nombre = user.first_name or user.username  # Usamos el nombre si existe, o el username como respaldo

            # Mensaje de éxito
            messages.success(request, f"✅ El usuario '{nombre}' fue creado correctamente.")
            return redirect("userList")
        else:
            return render(request, 'createUser.html', {
                'form': form,
                'update': False,
                'error_message': "❌ Por favor corrige los errores marcados antes de continuar."
            })
    else:
        form = UnifiedUserForm(is_update=False)
        return render(request, 'createUser.html', {
            'form': form,
            'update': False
        })


# Vista para editar un usuario  
@admin_required
def editUser(request):
    user_id = request.GET.get("id")
    user = get_object_or_404(User, id=user_id)
    nombre = user.username

    if request.method == "POST":
        # Guardamos el grupo actual para mantenerlo si no se envía en POST
        grupo_actual = user.groups.first()
        form = UnifiedUserForm(request.POST, instance=user, is_update=True)

        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()

            # Si no se envió role en el POST, mantenemos el grupo actual
            if not form.cleaned_data.get('role') and grupo_actual:
                user.groups.clear()
                user.groups.add(grupo_actual)
            else:
                form.save(commit=True)

            messages.success(request, f"✅ El usuario '{nombre}' fue editado correctamente. ")
            return redirect('userList') 
    else:
        form = UnifiedUserForm(instance=user, is_update=True)

    return render(request, 'createUser.html', {
        'form': form,
        'update': True
    })

# Vista para eliminar un usuario  
@admin_required
def deleteUser(request):
    user_id = request.GET.get("id")

    if user_id:
        user = User.objects.get(id=user_id)
        nombre = user.username
        user.delete()

        # Agregamos mensaje de éxito
        messages.success(request, f"🗑️ Usuario '{nombre}' eliminado correctamente.")

        # Redirigimos al listado
        return redirect('userList')


# Vista para listar los usuarios
@admin_required
def userList(request):
    form = UserFilterForm(request.GET or None)

    # Partimos de todos los usuarios que estén en los grupos permitidos
    usuarios = User.objects.filter(groups__name__in=['Administrador', 'Técnico']).distinct()

    if form.is_valid():
        nombre = form.cleaned_data.get('nombre')
        rol = form.cleaned_data.get('rol')  # Nuevo campo en el formulario

        if nombre:
            # Buscar por first_name en lugar de username
            usuarios = usuarios.filter(first_name__icontains=nombre)

        # Filtrar por rol solo si no es "Cualquiera"
        if rol and rol != 'cualquiera':
            usuarios = usuarios.filter(groups__name=rol)

    # Paginación (2 usuarios por página)
    paginator = Paginator(usuarios, 10) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)            

    return render(request, 'userList.html', {
        "usuarios": page_obj,
        "form": form
    })



# Vistas para inicio y cierre de sesión
def login(request):
    if request.user.is_authenticated:
        return redirect('index') 

    if request.method == "GET":
        return render(request, 'login.html', {
            "form": loginForm()
        })
    else:
        form = loginForm(request.POST)
        print("Entro a la vista correcta")

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                return redirect('index') 
            else:
                return render(request, 'login.html', {
                    "form": form,
                    "error": "Nombre de usuario o contraseña incorrectos."
                })

        print("Errores del formulario:", form.errors)
        return render(request, 'login.html', {
            "form": form,
            "error": "Por favor completa todos los campos correctamente."
        })

# Vista para cerrar sesión
@login_required    
def user_logout(request):
    logout(request)
    return redirect('login')