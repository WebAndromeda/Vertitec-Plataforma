from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import replacementParts
from .forms import replacementPartsForm
from django.contrib.auth.models import User

# Crear repuesto
def createPart(request):
    building_id = request.GET.get("id")
    building = get_object_or_404(User, id=building_id)

    if request.method == "POST":
        form = replacementPartsForm(request.POST)
        if form.is_valid():
            repuesto = form.save(commit=False)
            repuesto.building = building
            repuesto.save()
            return redirect(f"{reverse('listParts')}?id={building.id}")
    else:
        form = replacementPartsForm()

    return render(request, "createPart.html", {
        "form": form,
        "building": building,
        "update": False   # 👈 señalamos que es creación
    })


# Ver repuestos
def listParts(request):
    building_id = request.GET.get("id")  # id del edificio/usuario

    if building_id:  
        # Si viene un id → filtramos solo los de ese edificio
        building = get_object_or_404(User, id=building_id)
        repuestos = replacementParts.objects.filter(
            building=building
        ).select_related("tower", "building")

    else:
        # Si NO hay id → traemos todos los repuestos
        repuestos = replacementParts.objects.all().select_related("tower", "building")
        building = None  # 👈 para que el template sepa que no está filtrado

    return render(request, "listParts.html", {
        "repuestos": repuestos,
        "building": building
    })



# Editar repuesto
def editPart(request, part_id):
    repuesto = get_object_or_404(replacementParts, id=part_id)
    building = repuesto.building

    if request.method == "POST":
        form = replacementPartsForm(request.POST, instance=repuesto)
        if form.is_valid():
            form.save()
            return redirect(f"{reverse('listParts')}?id={building.id}")
    else:
        form = replacementPartsForm(instance=repuesto)

    return render(request, "createPart.html", {   # 👈 usamos el mismo template
        "form": form,
        "building": building,
        "repuesto": repuesto,
        "update": True   # 👈 señalamos que es edición
    })

# Eliminar repuesto
def deletePart(request, part_id):
    repuesto = get_object_or_404(replacementParts, id=part_id)
    building = repuesto.building  # Guardamos el edificio al que pertenece

    if request.method == "POST":
        repuesto.delete()
        # Redirigimos a la lista de repuestos del mismo building
        return redirect(f"{reverse('listParts')}?id={building.id}")

    # Si no es POST mostramos una confirmación
    return render(request, "deletePart.html", {
        "repuesto": repuesto,
        "building": building
    })