from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import replacementParts
from .forms import ReplacementPartsFilterForm, replacementPartsForm
from django.contrib.auth.models import User
from buildings.models import buildings, towers
from utils.decorators import admin_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Listar repuestos
@admin_required
def listParts(request):
    building_id = request.GET.get("id")

    building_user = None
    building_obj = None
    listado_completo = True

    # Filtrar por edificio si se pasa el ID
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

    # ------------------------------
    # FORMULARIO DE FILTROS
    # ------------------------------
    filter_form = ReplacementPartsFilterForm(request.GET or None)

    # Aplicar filtros
    if filter_form.is_valid():
        fecha_inicio = filter_form.cleaned_data.get("fecha_inicio")
        fecha_fin = filter_form.cleaned_data.get("fecha_fin")
        status_Install = filter_form.cleaned_data.get("status_Install")

        if fecha_inicio:
            repuestos = repuestos.filter(created_at__date__gte=fecha_inicio)

        if fecha_fin:
            repuestos = repuestos.filter(created_at__date__lte=fecha_fin)

        if status_Install:
            repuestos = repuestos.filter(status_Install=status_Install)

    # ------------------------------
    # PAGINACIÓN
    # ------------------------------
    paginator = Paginator(repuestos, 10)
    page_number = request.GET.get("page")
    repuestos_paginados = paginator.get_page(page_number)

    # ------------------------------
    # CREAR NUEVO REPUESTO
    # ------------------------------
    if request.method == "POST":
        form = replacementPartsForm(request.POST)

        if form.is_valid():
            nuevo_repuesto = form.save(commit=False)

            # Asociar edificio
            if building_user:
                nuevo_repuesto.building = building_user

            # Estado inicial
            if not nuevo_repuesto.approved_status:
                nuevo_repuesto.approved_status = "pendiente"

            # Calcular total
            nuevo_repuesto.precio_total = (
                nuevo_repuesto.cantidad * nuevo_repuesto.precio_unitario
            )

            # Asignar status_Payment según total
            if nuevo_repuesto.precio_total >= 1000000:
                nuevo_repuesto.status_Payment = "pendiente_anticipo"
            else:
                nuevo_repuesto.status_Payment = "no_aplica"

            nuevo_repuesto.save()

            messages.success(
                request,
                f"✅ Repuesto '{nuevo_repuesto.nameItem}' creado correctamente."
            )

            return redirect(f"{reverse('listParts')}?id={building_user.id}")

        else:
            print(form.errors)
            messages.error(
                request,
                "❌ Hubo un error al crear el repuesto. Revisa los campos."
            )

    else:
        form = replacementPartsForm()

    # Limitar torres según edificio seleccionado
    if building_obj:
        form.fields["tower"].queryset = towers.objects.filter(building=building_obj)

    # ------------------------------
    # RENDER
    # ------------------------------
    return render(request, "listParts.html", {
        "repuestos": repuestos_paginados,
        "building": building_user,
        "form": form,
        "filters": filter_form,  # Solo los 3 filtros
        "listado_completo": listado_completo,
        "paginator": paginator,
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

    from django.core.paginator import Paginator

    paginator = Paginator(repuestos, 10)  # 10 por página
    page_number = request.GET.get("page")  
    repuestos_paginados = paginator.get_page(page_number)

    es_cliente = user.groups.filter(name="Cliente").exists()

    return render(request, "listParts.html", {
        "repuestos": repuestos_paginados,   # ← enviar paginados
        "building": user,
        "listado_completo": False,
        "es_cliente": es_cliente,
        "paginator": paginator,  # opcional para más control
    })


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

    return render(request, "editPart.html", {
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