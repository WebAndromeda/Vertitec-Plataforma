from django.contrib.auth import authenticate, login as auth_login, logout
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from .forms import loginForm, UnifiedUserForm 


# Index
def index(request):
    return render(request, 'index.html')

# Vistas para CRUD de usuarios
# Vista para crear un usuario  
@admin_required
def createUser(request):
    if request.method == "POST":
        form = UnifiedUserForm(request.POST)
        if form.is_valid():
            form.save()
            print("Usuario creado correctamente.")
            return redirect("userList")  # Cambia por la URL que desees
    else:
        form = UnifiedUserForm(is_update=False)

        return render(request, 'createUser.html', {
            'forms': form,
            'update': False
        })

# Vista para editar un usuario
@admin_required        
def editUser(request):
    user_id = request.GET.get("id")
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        form = UnifiedUserForm(request.POST, instance=user, is_update=True)
        if form.is_valid():
            form.save()
            return redirect('userList') 
    else:
        form = UnifiedUserForm(instance=user, is_update=True)

        return render(request, 'createUser.html', {
            'forms': form,
            'update': True
        })

# Vista para eliminar un usuario  
@admin_required
def deleteUser(request):
    user_id = request.GET.get("id")

    if(user_id):
        # Si existe el id del usuario, se elimina
        user = User.objects.get(id=user_id)
        user.delete()

        # Despues a eliminarse, se redirecciona al listado de usuarios
        usuarios = User.objects.all()
        return render(request, 'userList.html',{
            "usuarios":usuarios
        })


# Vista para listar los usuarios
@admin_required
def userList(request):
    if request.method == "GET":
        print("Usuario:", request.user.username)
        print("Grupos del usuario:", list(request.user.groups.values_list('name', flat=True)))
        # if request.user.groups.filter(name='Administrador').exists():
        
        # usuarios = User.objects.all() Mostrar todos los usuarios
        usuarios = User.objects.filter(groups__name__in=['Administrador', 'Técnico']).distinct() # Mostrar solo los de perfil Administrdor y tecnico

        return render(request, 'userList.html',{
            "usuarios":usuarios
        })


# Vistas para inicio y cierre de sesión
# Vista para iniciar sesión
def login(request):
    if request.user.is_authenticated:
        return redirect('index') 
    if request.method == "GET":
        return render(request, 'login.html', {
            "form":loginForm()
        })
    else:
        form = loginForm(request.POST)
        print("Entro a la vista correcta");

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)

            if user is not None:
                auth_login(request, user)
                #return redirect('about')  # Cambia esto por la vista a la que quieres redirigir
                return redirect('login')
            else:
                return HttpResponse("<h1>Los datos son incorrectos</h1>")    
            
        # 🔴 Aquí estás cubriendo el caso en el que el formulario no es válido
        print("Errores del formulario:", form.errors)
        return HttpResponse("<H1>No fue validado el formulario<h1>");

# Vista para cerrar sesión
@login_required    
def user_logout(request):
    logout(request)
    return redirect('login')