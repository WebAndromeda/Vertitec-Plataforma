from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ScheduleForm, ScheduleFilterForm
from .models import schedule
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse
from django.contrib.auth.models import User
from buildings.models import buildings, towers
from django.core.paginator import Paginator

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

    # Aplicar filtros si el formulario es válido
    form = ScheduleFilterForm(request.GET or None)
    if form.is_valid():
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        technician = form.cleaned_data.get("technician")
        building_name = form.cleaned_data.get("building")
        status = form.cleaned_data.get("status")

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
        if status == "true":
            scheduleModel = scheduleModel.filter(status=True)
        elif status == "false":
            scheduleModel = scheduleModel.filter(status=False)

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
    })


# Vista para crear un agendamiento
@admin_required
def createSchedule(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            sched = form.save(commit=False)

            # Guardamos el agendamiento inicial
            sched.save()

            # Si es recurrente mensual, creamos futuras repeticiones
            if sched.recurrence == "monthly":
                base_date = sched.date
                for i in range(1, 6):  # crea 6 meses adicionales, ajusta según necesidad
                    try:
                        new_date = base_date + relativedelta(months=i)
                        schedule.objects.create(
                            client=sched.client,
                            tower=sched.tower,
                            date=new_date,
                            hour=sched.hour,
                            status=False,
                            recurrence=sched.recurrence,
                            technician=sched.technician
                        )
                    except ValueError:
                        # Si el día no existe (ej: 30 febrero), ajustamos al último día del mes
                        new_date = (base_date + relativedelta(months=i, day=31))
                        schedule.objects.create(
                            client=sched.client,
                            tower=sched.tower,
                            date=new_date,
                            hour=sched.hour,
                            status=False,
                            recurrence=sched.recurrence,
                            technician=sched.technician
                        )

            return redirect('listSchedule')
    else:
        form = ScheduleForm()

    return render(request, 'createSchedule.html', {
        'forms': form,
        'update': False
    })


# Vista para editar un agendamiento
@login_required
def editSchedule(request):
    schedule_id = request.GET.get("id")
    scheduleEdit = get_object_or_404(schedule, id=schedule_id)

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=scheduleEdit)
        if form.is_valid():
            form.save()
            return redirect('listSchedule')
    else:
        # Aquí asignamos manualmente initial para el campo 'client'
        form = ScheduleForm(
            instance=scheduleEdit,
            initial={'client': scheduleEdit.client.first_name}
        )

    return render(request, 'createSchedule.html', {
        'forms': form,
        'update': True
    })


# Vista para eliminar un agendamiento
@admin_required
def deleteSchedule(request):
    schedule_id = request.GET.get("id")

    if schedule_id:
        scheduleDelete = get_object_or_404(schedule, id=schedule_id)
        scheduleDelete.delete()

    return redirect('listSchedule')
