from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required, roles_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ScheduleForm, ScheduleFilterForm
from .models import schedule
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.contrib.auth.models import User
from buildings.models import buildings, towers
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django import forms







# Crear opciones para seleccionar la torre del edificio seleccionado
def tower_suggestions(request):
    building_id = request.GET.get("building_id")
    suggestions = []

    if building_id:
        towersList = towers.objects.filter(building_id=building_id).values("id", "name")
        suggestions = list(towersList)

    return JsonResponse(suggestions, safe=False)

# Autocompletado del edificio
def building_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        # Buscar solo usuarios en el grupo Cliente cuyo nombre coincida
        clientes = User.objects.filter(
            groups__name='Cliente',
            first_name__icontains=query
        ).distinct()[:5]

        # Ahora devolvemos el id del building, no del user
        suggestions = [
            {"id": cliente.buildings.id, "first_name": cliente.first_name}
            for cliente in clientes if hasattr(cliente, "buildings")
        ]

    return JsonResponse(suggestions, safe=False)

# Autocompletado de nombre del edificio
def building_suggestionsS(request):
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


# Vista para listar los agendamientos con filtros
@login_required
def listSchedule(request):
    scheduleModel = schedule.objects.all().order_by('-date', 'hour')
    server_time = timezone.localtime().strftime("%I:%M")

    # Aplicar filtros si el formulario es válido
    form = ScheduleFilterForm(request.GET or None)
    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        technician = form.cleaned_data.get("technician")
        building_name = form.cleaned_data.get("building")
        status = form.cleaned_data.get("status")
        programmed = form.cleaned_data.get("programmed")   # <-- NUEVO

        if start_date:
            scheduleModel = scheduleModel.filter(date__gte=start_date)
        if end_date:
            scheduleModel = scheduleModel.filter(date__lte=end_date)
        if technician:
            scheduleModel = scheduleModel.filter(technician=technician)
        if building_name:
            scheduleModel = scheduleModel.filter(
                tower__building__user__first_name__icontains=building_name
            )
            
        if status:
            scheduleModel = scheduleModel.filter(status=status)

        if programmed:  
            scheduleModel = scheduleModel.filter(programmed=programmed)

    # Filtro por rol del usuario
    if request.user.groups.filter(name='Administrador').exists():
        pass  # ve todos
    elif request.user.groups.filter(name='Técnico').exists():
        scheduleModel = scheduleModel.filter(technician=request.user)
    else:  # Cliente
        scheduleModel = scheduleModel.filter(client=request.user)

    # Paginación 
    paginator = Paginator(scheduleModel, 10)  # 10 agendamientos por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'listSchedule.html', {
        "schedule": page_obj,  # pasamos page_obj al template
        "form": form,
        "server_time": server_time,
    })



@roles_required("Administrador", "Técnico")
def createSchedule(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST, user=request.user)
        if form.is_valid():
            # ⚠️ Advertencia por horarios cercanos
            warning = form.cleaned_data.get('__warning__')
            if warning and "confirm_warning" not in request.POST:
                messages.warning(request, warning)
                return render(request, "createSchedule.html", {
                    "forms": form,
                    "confirm_warning": True,
                    "update": False
                })

            sched = form.save(commit=False)

            # Asignar campos automáticos según rol
            if request.user.groups.filter(name="Administrador").exists():
                sched.programmed = "programmed"
            else:  # Técnico
                sched.programmed = "not_programmed"
                sched.recurrence = "single"
                sched.technician = request.user
                sched.status = "to_be_done"

            sched.save()

            # Recurrente mensual solo aplica si es admin
            if sched.recurrence == "monthly":
                base_date = sched.date
                for i in range(1, 6):
                    try:
                        new_date = base_date + relativedelta(months=i)
                        schedule.objects.create(
                            client=sched.client,
                            tower=sched.tower,
                            date=new_date,
                            hour=sched.hour,
                            status="to_be_done",
                            recurrence=sched.recurrence,
                            technician=sched.technician,
                            programmed=sched.programmed
                        )
                    except ValueError:
                        new_date = base_date + relativedelta(months=i, day=31)
                        schedule.objects.create(
                            client=sched.client,
                            tower=sched.tower,
                            date=new_date,
                            hour=sched.hour,
                            status="to_be_done",
                            recurrence=sched.recurrence,
                            technician=sched.technician,
                            programmed=sched.programmed
                        )

            # ✅ Mensaje de éxito y redirección al listado
            messages.success(request, "✅ Agendamiento creado correctamente.")
            return redirect("listSchedule")

        else:
            # Formulario inválido → errores en el mismo formulario
            return render(request, "createSchedule.html", {
                "forms": form,
                "update": False
            })

    else:
        # GET → formulario vacío, siempre pasamos user
        form = ScheduleForm(user=request.user)
        return render(request, "createSchedule.html", {
            "forms": form,
            "update": False
        })


# Vista para editar un agendamiento
@roles_required("Administrador", "Técnico")
def editSchedule(request):
    schedule_id = request.GET.get("id")
    scheduleEdit = get_object_or_404(schedule, id=schedule_id)

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=scheduleEdit, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"✅ El agendamiento fue editado correctamente. ")
            return redirect('listSchedule')
    else:
        form = ScheduleForm(
            instance=scheduleEdit,
            initial={'client': scheduleEdit.client.first_name},
            user=request.user,   # ← OBLIGATORIO
        )

    return render(request, 'createSchedule.html', {
        'forms': form,
        'update': True
    })


# Vista para eliminar un agendamiento
@roles_required("Administrador", "Técnico")
def deleteSchedule(request):
    schedule_id = request.GET.get("id")

    if not schedule_id:
        messages.error(request, "❌ No se recibió el ID del agendamiento.")
        return redirect('listSchedule')

    sched = get_object_or_404(schedule, id=schedule_id)

    # ---------------------------------------
    # 🚨 Validar si el agendamiento tiene reporte
    # ---------------------------------------
    if hasattr(sched, "report"):
        messages.error(request, "❌ No puedes eliminar este agendamiento porque ya tiene un reporte asociado.")
        return redirect('listSchedule')

    # Si NO existe un reporte → se puede eliminar
    sched.delete()

    messages.success(request, "🗑️ El agendamiento fue eliminado correctamente.")
    return redirect('listSchedule')
