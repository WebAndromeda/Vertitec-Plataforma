from django.http import HttpResponse, JsonResponse
from django.shortcuts import  get_object_or_404, render, redirect
from utils.decorators import admin_required
from django.contrib.auth.models import Group, User
from .forms import  buildingsForm, towerForm, UserFilterForm
from .models import buildings, towers


# Autocompletado de nombre del edificio
def user_suggestions(request):
    query = request.GET.get('q', '')  # texto escrito
    suggestions = []

    if query:
        # Buscar por nombre de pila (first_name) en admins y técnicos
        usuarios = User.objects.filter(
            groups__name__in=['Cliente'],
            first_name__icontains=query
        ).distinct()[:5]  # limitar a 5 resultados

        # Devolver solo el nombre real 
        suggestions = list(
            usuarios.values_list('first_name', flat=True)
        )

    return JsonResponse(suggestions, safe=False)

# Vistas para CRUD de edificios / clientes 
# Vista para listar los edificios / clientes
@admin_required
def listBuildings(request):
    form = UserFilterForm(request.GET or None)

    # Partimos de todos los usuarios que estén en los grupos permitidos
    usuarios = User.objects.filter(groups__name__in=['Cliente']).distinct()

    if form.is_valid():
        nombre = form.cleaned_data.get('nombre')

        if nombre:
            # Buscar por first_name en lugar de username
            usuarios = usuarios.filter(first_name__icontains=nombre)

    if request.method == "GET":
        buildingsList = buildings.objects.all()
        
        """ # Ver atributos a los que se puede acceder
        for u in buildingsList:
            print("---- Datos del edificio ----")
            for field in buildings._meta.fields:
                print(f"{field.name}: {getattr(u, field.name)}")
        """
        return render(request, 'listBuildings.html', {
            "buildingList":buildingsList,
            "form": form
        })
        

# Vista para crear un edificio / cliente
@admin_required
def createBuilding(request):
    if request.method == "POST":
        form = buildingsForm(request.POST, is_update=False)
        if form.is_valid():
            building = form.save()  # building.user contiene el usuario creado

            # Crear automáticamente la torre "Torre Única"
            towers.objects.create(building=building, name="Torre Única")

            # Asignar grupo 'Cliente'
            grupo_cliente = get_object_or_404(Group, name='Cliente')
            building.user.groups.add(grupo_cliente)

            return redirect('listBuildings')
        
        print(form.errors)
        return HttpResponse("Si ves este mensaje, el formulario no fue valido")
    
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
        user.delete()

        # Despues a eliminarse, se redirecciona al listado de edificios clientes
        return redirect('listBuildings')
    


# Vistas para CRUD de Torres
# Vista para añadir una torre
@admin_required 
def addTower(request, building_id):
    building = get_object_or_404(buildings, id=building_id)

    if request.method == 'POST':
        form = towerForm(request.POST)
        if form.is_valid():
            tower = form.save(commit=False)
            tower.building = building  # Asociar torre al edificio
            tower.save()
            return redirect(f'/listTowers?id={building_id}')  # Redireccionamos incluyendo el ID
    else:
        form = towerForm()
        form.fields['building'].initial = building.id  

    return render(request, 'createTower.html', {
        'forms': form
    })

# Vista para editar una torre 
@admin_required
def editTowers(request):
    tower_id = request.GET.get("id")
    tower = get_object_or_404(towers, id=tower_id)

    if request.method == "POST":
        form = towerForm(request.POST, instance=tower)
        if form.is_valid():
            form.save()
            return redirect('listBuildings')
    else:
        building_id = tower.building_id
        form = towerForm()
        form.fields['building'].initial = building_id
        form.fields['name'].initial = tower.name

        # form = towerForm(instance=tower) Se puede reemplazar lo anterior de el else con solo esta linea 

    return render(request, 'createTower.html', {
            "forms":form,
            "is_update": True
        })   


# Vista para listar torres de un edificio en especifico (No todas las torres)
@admin_required
def listTowers(request):
    if request.method == "GET":
        client_id = request.GET.get("id")

        towerList = towers.objects.filter(building_id=client_id)
        
        return render(request, 'listTowers.html', {
            "towerList":towerList
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
        towers.objects.create(building=building, name="Torre Única")

    return redirect(f'/listTowers?id={building.id}')

# Y como harias aqui para que al momento de eliminar una torre, verifique si el listado de torres es vacio, y si es vacio que cree la torre unica