from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from .models import replacementParts
from .forms import ReplacementPartsFilterForm, replacementPartsForm
from django.contrib.auth.models import User
from buildings.models import buildings, towers
from utils.decorators import admin_required, roles_required
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# Listado de respuestos si es metodo Get y creacion de repuesto si es metodo Post
@roles_required("Administrador", "Cliente")
def listParts(request):

    user = request.user
    es_admin = user.groups.filter(name__in=["Administrador", "Técnico"]).exists()
    es_cliente = user.groups.filter(name="Cliente").exists()

    building_user = None
    building_obj = None
    listado_completo = True

    # ----------------------------------
    #   FILTRO BASE SEGÚN EL ROL
    # ----------------------------------
    if es_admin:
        # Admin puede ver todos o filtrar por ?id=
        building_id = request.GET.get("id")

        if building_id:
            building_user = get_object_or_404(User, id=building_id)
            building_obj = get_object_or_404(buildings, user=building_user)

            repuestos = replacementParts.objects.filter(
                building=building_user
            ).select_related("tower", "building")

            listado_completo = False

        else:
            repuestos = replacementParts.objects.all().select_related("tower", "building")

    else:
        # Cliente: solo sus repuestos
        building_user = user
        repuestos = replacementParts.objects.filter(
            building=user
        ).select_related("tower", "building")

        listado_completo = False

    # ----------------------------------
    # FORMULARIO DE FILTROS
    # ----------------------------------
    filter_form = ReplacementPartsFilterForm(request.GET or None)

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

    # ----------------------------------
    # PAGINACIÓN
    # ----------------------------------
    paginator = Paginator(repuestos, 10)
    page_number = request.GET.get("page")
    repuestos_paginados = paginator.get_page(page_number)

    # ----------------------------------
    # CREACIÓN DE REPUESTOS (SOLO ADMIN)
    # ----------------------------------
    if es_admin and request.method == "POST":
        form = replacementPartsForm(request.POST)

        if form.is_valid():
            nuevo = form.save(commit=False)

            # asociar edificio
            if building_user:
                nuevo.building = building_user

            # estado inicial
            if not nuevo.approved_status:
                nuevo.approved_status = "pendiente"

            # total
            nuevo.precio_total = nuevo.cantidad * nuevo.precio_unitario

            # status payment
            if nuevo.precio_total >= 1_000_000:
                nuevo.status_Payment = "pendiente_anticipo"
            else:
                nuevo.status_Payment = "no_aplica"

            nuevo.save()

            messages.success(
                request, f"✅ Repuesto '{nuevo.nameItem}' creado correctamente."
            )

            return redirect(f"{reverse('listParts')}?id={building_user.id}")

        else:
            print(form.errors)
            messages.error(request, "Error al crear el repuesto.")

    else:
        form = replacementPartsForm() if es_admin else None

    # limitar torres si se seleccionó edificio
    if building_obj and form:
        form.fields["tower"].queryset = towers.objects.filter(building=building_obj)

    # ----------------------------------
    # RENDER
    # ----------------------------------
    return render(request, "listParts.html", {
        "repuestos": repuestos_paginados,
        "building": building_user,
        "listado_completo": listado_completo,
        "filters": filter_form,
        "paginator": paginator,
        "form": form,
        "es_cliente": es_cliente,
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