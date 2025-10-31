from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import replacementParts
from .forms import replacementPartsForm
from django.contrib.auth.models import User
from buildings.models import buildings, towers
from utils.decorators import admin_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# Crear repuestos y ver repuestos
@admin_required
def listParts(request):
    building_id = request.GET.get("id")

    building_user = None
    building_obj = None
    listado_completo = True

    # 🔹 Filtrar por edificio si se pasa ID
    if building_id:
        building_user = get_object_or_404(User, id=building_id)
        building_obj = get_object_or_404(buildings, user=building_user)
        repuestos = (
            replacementParts.objects
            .filter(building=building_user)
            .select_related("tower", "building")
        )
        listado_completo = False
    else:
        repuestos = replacementParts.objects.all().select_related("tower", "building")

    # 🔹 Crear nuevo repuesto
    if request.method == "POST":
        form = replacementPartsForm(request.POST)
        if form.is_valid():
            nuevo_repuesto = form.save(commit=False)

            # Asociar edificio correspondiente
            if building_user:
                nuevo_repuesto.building = building_user

            # Asegurar estado inicial
            if not nuevo_repuesto.approved_status:
                nuevo_repuesto.approved_status = "pendiente"

            nuevo_repuesto.save()
            messages.success(request, f"✅ Repuesto '{nuevo_repuesto.nameItem}' creado correctamente.")
            return redirect(f"{reverse('listParts')}?id={building_user.id}")
        else:
            print(form.errors)  # 🔍 Para depurar si ocurre un error
            messages.error(request, "❌ Hubo un error al crear el repuesto. Revisa los campos.")
    else:
        form = replacementPartsForm()

    # 🔹 Limitar torres según el edificio seleccionado
    if building_obj:
        form.fields["tower"].queryset = towers.objects.filter(building=building_obj)

    return render(request, "listParts.html", {
        "repuestos": repuestos,
        "building": building_user,
        "form": form,
        "listado_completo": listado_completo,
    })


# Vista para listar repuestos del cliente
@login_required
def listPartsClient(request):
    user = request.user
    repuestos = (
        replacementParts.objects
        .filter(building=user)
        .select_related("tower", "building")
    )

    es_cliente = user.groups.filter(name="Cliente").exists()

    return render(request, "listParts.html", {
        "repuestos": repuestos,
        "building": user,
        "listado_completo": False,
        "es_cliente": es_cliente,  # 👈 esta variable la usas en el template
    })

# Vista para que el cliente pueda cambiar el estado, aprobar o rechazar un repuesto
@login_required
def toggle_approval(request, part_id, action):
    # Buscar el repuesto que pertenece al cliente logueado
    repuesto = get_object_or_404(replacementParts, id=part_id, building=request.user)

    # Diccionario de acciones válidas
    VALID_ACTIONS = {
        "aprobar": ("aprobado", f"✅ Has aprobado el repuesto '{repuesto.nameItem}'."),
        "rechazar": ("rechazado", f"❌ Has rechazado el repuesto '{repuesto.nameItem}'."),
    }

    # Verificamos si la acción enviada es válida
    if action in VALID_ACTIONS:
        nuevo_estado, mensaje = VALID_ACTIONS[action]
        repuesto.approved_status = nuevo_estado
        repuesto.save()
        # Usamos el tipo de mensaje adecuado
        if action == "aprobar":
            messages.success(request, mensaje)
        else:
            messages.warning(request, mensaje)
    else:
        # Acción no reconocida
        messages.error(request, "⚠️ Acción no válida. Intenta nuevamente.")

    # Redirige a la lista de repuestos del cliente
    return redirect("listPartsClient")


# Editar repuesto
@admin_required
def editPart(request, part_id):
    repuesto = get_object_or_404(replacementParts, id=part_id)
    building = repuesto.building
    building_obj = get_object_or_404(buildings, user=building)

    if request.method == "POST":
        form = replacementPartsForm(request.POST, instance=repuesto)
        if form.is_valid():
            # 🔹 Guardamos el form pero sin commit, para poder editar campos no incluidos en el form
            updated_part = form.save(commit=False)
            # 🔹 Tomamos el valor del select manual y lo asignamos
            updated_part.approved_status = request.POST.get("approved_status", repuesto.approved_status)
            updated_part.save()

            messages.success(request, f"✏️ El repuesto '{repuesto.nameItem}' fue actualizado correctamente.")
            return redirect(f"{reverse('listParts')}?id={building.id}")
    else:
        form = replacementPartsForm(instance=repuesto)
        form.fields["tower"].queryset = towers.objects.filter(building=building_obj)

    return render(request, "createPart.html", {
        "form": form,
        "building": building,
        "repuesto": repuesto,
        "update": True
    })



# Eliminar repuesto
@admin_required
def deletePart(request, part_id):
    repuesto = get_object_or_404(replacementParts, id=part_id)
    building = repuesto.building  # Guardamos el edificio al que pertenece

    if request.method == "POST":
        repuesto.delete()
        messages.success(request, f"🗑️ El repuesto '{repuesto.nameItem}' fue eliminado correctamente.")
        # Redirigimos a la lista de repuestos del mismo building
        return redirect(f"{reverse('listParts')}?id={building.id}")

    # Si no es POST mostramos una confirmación
    return render(request, "deletePart.html", {
        "repuesto": repuesto,
        "building": building
    })