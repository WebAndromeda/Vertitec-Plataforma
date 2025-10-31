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
    usuarios = User.objects.filter(groups__name__in=['Cliente']).distinct()

    if form.is_valid():
        nombre = form.cleaned_data.get('nombre')

        if nombre:
            usuarios = usuarios.filter(first_name__icontains=nombre)

    # Filtrar los buildings asociados a esos usuarios
    buildingsList = buildings.objects.filter(user__in=usuarios)

    # Paginación 
    paginator = Paginator(buildingsList, 10)  # 2 edificios por página
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
            building = form.save()  # building.user contiene el usuario creado
            nombre_edificio = building.user.first_name  # Puedes cambiar a building.address si prefieres

            # 🔹 Crear automáticamente una torre con el nombre del edificio
            nombre_torre = f"Torre {nombre_edificio}"
            towers.objects.create(building=building, name=nombre_torre)

            # Asignar grupo 'Cliente'
            grupo_cliente = get_object_or_404(Group, name='Cliente')
            building.user.groups.add(grupo_cliente)

            messages.success(request, f"✅ El edificio '{nombre_edificio}' fue creado correctamente con su {nombre_torre}.")
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


# Vista para eliminar un edificio / cliente
@admin_required
def deleteBuilding(request):
    user_id = request.GET.get("id")

    if(user_id):
        # Si existe el id del usuario, se elimina
        user = User.objects.get(id=user_id)
        nombre_edificio = user.username
        user.delete()

        # Agregamos mensaje de éxito
        messages.success(request, f"🗑️ El edificio '{nombre_edificio}' fue eliminado correctamente.")

        # Despues a eliminarse, se redirecciona al listado de edificios clientes
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