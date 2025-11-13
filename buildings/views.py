from django.http import HttpResponse, JsonResponse
from django.shortcuts import  get_object_or_404, render, redirect
from utils.decorators import admin_required
from django.contrib.auth.models import Group, User
from .forms import  buildingsForm, towerForm, UserFilterForm
from .models import buildings, towers
from django.core.paginator import Paginator
from django.contrib import messages


# Autocompletado de nombre del edificio
def building_suggestionsB(request):
    query = request.GET.get('q', '')  
    suggestions = []

    if query:
        usuarios = User.objects.filter(
            groups__name__in=['Cliente'],
            first_name__icontains=query
        ).distinct()[:5]

        # DEVOLVER SOLO LISTA DE STRINGS (igual que en user_suggestions)
        suggestions = list(
            usuarios.values_list('first_name', flat=True)
        )

    return JsonResponse(suggestions, safe=False)


# Vistas para CRUD de edificios / clientes 
# Vista para listar los edificios / clientes
@admin_required
def listBuildings(request):
    form = UserFilterForm(request.GET or None)

    # Filtrar solo los usuarios que sean clientes
    usuarios = User.objects.filter(groups__name='Cliente').distinct()

    # 🔹 Filtrar por activos por defecto si no hay GET
    if not request.GET.get('estado'):
        usuarios = usuarios.filter(is_active=True)

    if form.is_valid():
        nombre = form.cleaned_data.get('nombre')
        estado = form.cleaned_data.get('estado')

        if nombre:
            usuarios = usuarios.filter(first_name__icontains=nombre)

        # 🔹 Filtro según estado
        if estado == 'activo':
            usuarios = usuarios.filter(is_active=True)
        elif estado == 'inactivo':
            usuarios = usuarios.filter(is_active=False)
        # 'todos' => no filtramos

    # Filtrar los buildings asociados a esos usuarios
    buildingsList = buildings.objects.filter(user__in=usuarios)

    # Paginación
    paginator = Paginator(buildingsList, 10)  # 10 edificios por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listBuildings.html', {
        "buildingList": page_obj,
        "form": form
    })

        

# Vista para crear un edificio / cliente
@admin_required
def createBuilding(request):
    if request.method == "POST":
        form = buildingsForm(request.POST, is_update=False)
        if form.is_valid():
            building = form.save()
            nombre_edificio = building.user.first_name  

            # Asignar grupo 'Cliente'
            grupo_cliente = get_object_or_404(Group, name='Cliente')
            building.user.groups.add(grupo_cliente)

            messages.success(request, f"✅ El edificio '{nombre_edificio}' fue creado correctamente.")
            return redirect('listBuildings')
        
        print(form.errors)
        return HttpResponse("Si ves este mensaje, el formulario no fue válido.")
    
    else:
        form = buildingsForm(is_update=False)
        return render(request, 'createBuilding.html', {
            "forms": form,
            "update": False
        })

    
# Vista para editar un edificio / cliente   
@admin_required      
def editBuilding(request):
    user_id = request.GET.get("id")
    user = get_object_or_404(User, id=user_id)
    building = get_object_or_404(buildings, user=user)

    if request.method == "POST":
        form = buildingsForm(request.POST, instance=user, is_update=True, building_instance=building)
        if form.is_valid():
            form.save()
            nombre_edificio = user.first_name;

            messages.success(request, f"✅ El edificio '{nombre_edificio}' fue editado correctamente.")
            return redirect('listBuildings') 
    else:
        form = buildingsForm(instance=user, is_update=True, building_instance=building)

    return render(request, 'createBuilding.html', {
        'forms': form,
        'update': True
    })


# Vista para desactivar un edificio / cliente (NO ES BORRARLO, esto solo lo puede hacer el superusuario desde /admin)
@admin_required
def deactivateBuilding(request):
    user_id = request.GET.get("id")

    if user_id:
        # Obtenemos el usuario asociado al edificio
        user = User.objects.get(id=user_id)
        nombre_edificio = user.username

        # 🔹 Desactivar usuario en lugar de eliminar
        user.is_active = False
        user.save()

        messages.success(request, f"🗑️ El edificio '{nombre_edificio}' fue desactivado correctamente.")

        # Redirigir al listado de edificios
        return redirect('listBuildings')
    

# Vista para reactivar un usuario
@admin_required
def activateBuilding(request):
    user_id = request.GET.get("id")

    if user_id:
        # Obtenemos el usuario asociado al edificio
        user = User.objects.get(id=user_id)
        nombre_edificio = user.username

        # 🔹 Activar usuario
        user.is_active = True
        user.save()

        messages.success(request, f"✅ El edificio '{nombre_edificio}' fue activado correctamente.")

        # Redirigir al listado de edificios
        return redirect('listBuildings')
    

# Vistas para CRUD de Torres
# Vista para listar, editar y crear torres en una misma página, de un edificio en especifico (No todas las torres)
@admin_required
def listTowers(request):
    client_id = request.GET.get("id")
    building = get_object_or_404(buildings, id=client_id)

    # 🟢 Si es POST, determinamos si es edición o creación
    if request.method == "POST":
        tower_id = request.POST.get("tower_id")
        new_name = request.POST.get("name")

        if tower_id:  # 🔹 Edición de torre existente
            tower = get_object_or_404(towers, id=tower_id)
            tower.name = new_name
            tower.save()
            messages.success(request, f"✅ La torre fue editada correctamente. ")

        else:  # 🔹 Creación de nueva torre
            if new_name.strip():
                messages.success(request, f"✅ La torre fue creada correctamente. ")
                towers.objects.create(building=building, name=new_name.strip())

        # Redirigimos manteniendo el mismo edificio
        return redirect(f'/listTowers?id={building.id}')

    # 🟢 Si es GET, mostramos la lista
    towerList = towers.objects.filter(building=building)

    return render(request, 'listTowers.html', {
        "towerList": towerList,
        "building": building
    })
    
# Vista para eliminar una torre
@admin_required
def deleteTower(request):
    tower_id = request.GET.get("id")
    tower = get_object_or_404(towers, id=tower_id)

    building = tower.building  # Guardamos la instancia del edificio

    tower.delete()  # Eliminamos la torre

    # Verificamos si el edificio ya no tiene torres
    if not towers.objects.filter(building=building).exists():
        # 🔹 Crear una torre con el nombre del edificio
        nombre_torre = f"Torre {building.user.first_name}"  # o building.user.username / building.address según prefieras
        towers.objects.create(building=building, name=nombre_torre)

    messages.success(request, f"🗑️ La torre fue eliminada correctamente.")
    return redirect(f'/listTowers?id={building.id}')