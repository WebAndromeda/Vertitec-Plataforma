from django.contrib.auth.decorators import login_required
from utils.decorators import admin_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from .forms import ScheduleForm
from .models import schedule


# Vista para listar los agendamientos
@login_required
def listSchedule(request):
    if request.method == "GET":
        print("Usuario:", request.user.username)
        print("Grupos del usuario:", list(request.user.groups.values_list('name', flat=True)))

        # Si es administrador, mostrar todos
        if request.user.groups.filter(name='Administrador').exists():
            scheduleModel = schedule.objects.all()

        # Si es técnico, mostrar solo los asignados como técnico
        elif request.user.groups.filter(name='Técnico').exists():
            scheduleModel = schedule.objects.filter(technician=request.user)

        # Si es cliente, mostrar solo los agendamientos que le corresponden
        else:
            scheduleModel = schedule.objects.filter(client=request.user)

        return render(request, 'listSchedule.html', {
            "schedule": scheduleModel
        })

"""Ver por consola los atributos a los que es posible acceder
    for u in scheduleModel:
        print("---- Datos Schedule ----")
        for field in schedule._meta.fields:
            print(f"{field.name}: {getattr(u, field.name)}")
"""


# Vista para crear un agendamiento
@admin_required
def createSchedule(request):
    if request.method == "POST":
        form = ScheduleForm(request.POST)
        if form.is_valid():
            form.save()  
            return redirect('listSchedule')
    else:
        form = ScheduleForm()

    return render(request, 'createSchedule.html', {
        'forms': form,
        'update': False
    })

    
# Vista para editar un agendamiento
@admin_required        
def editSchedule(request):
    schedule_id = request.GET.get("id")
    scheduleEdit = get_object_or_404(schedule, id=schedule_id)

    if request.method == "POST":
        form = ScheduleForm(request.POST, instance=scheduleEdit, is_update=True)
        if form.is_valid():
            form.save()
            return redirect('listSchedule') 
    else:
        form = ScheduleForm(instance=scheduleEdit, is_update=True)

        return render(request, 'createSchedule.html', {
            'forms': form,
            'update': True
        })


# Vista para eliminar un agendamiento
@admin_required
def deleteSchedule(request):
    schedule_id = request.GET.get("id")

    if(schedule_id):
        # Si existe el id del usuario, se elimina
        scheduleDelete = schedule.objects.get(id=schedule_id)
        scheduleDelete.delete()

        # Despues a eliminarse, se redirecciona al listado de agendamientos
        scheduleModel = schedule.objects.all()
        return render(request, 'listSchedule.html',{
            "schedule":scheduleModel
        })
    

    """
    Tengo que mostrar una plantilla html que muestra el contenido de una tabla o modelo, sin embargo, entre la informacion que tengo que mostrar, hay un dato que esta en otra tabla, el campo se llama "address"  ¿Que es mejor?
    Opcion 1:
        Crear una llave foranea entre la tabla que ya estoy mostrando  "Agendamiento" y la tabla Clientes / Edificios que es donde esta el campo address que quiero mostrar, p
    Opcion 2:
        En la vista o views.py pasarle a la plantilla tambien la tabla Clientes / Edificios

    Adjunto una imagen de mas o menos como se ve la base de datos



    Claro, pero piensa lo siguiente, tengo el siguiente modelo, como puedes ver, tiene 3 llaves foraenas, una al cliente, otra a los tecnicos, y otra a las torres, esto tiene sentido porque en cada agendamiento tengo que selecionar uno de los clientes, uno de los tecnicos y una de las torres, sin embargo hay un dato especial, es el campo address, este campo el usuario no debe seleccionarlo, ya que al seleccionar un cliente, el modelo de clientes ya esta asociado con una clave foranea a un modelo llamado buildings, el cual tiene unicamente una direccion para cada edificio, por lo que no tiene sentido poner al usuario a seleccionar entre una sola opcion. ¿Que me recomiendas?

    from django.db import models
from django.contrib.auth.models import User
from buildings.models import buildings, towers

# Modelo para guardar el agendamiento
class schedule(models.Model):
    # Usuario que solicita el agendamiento (cliente)
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Cliente'},
        related_name='client_schedules'
    )

    tower = models.ForeignKey(towers, on_delete=models.CASCADE)
    # address = models.ForeignKey(buildings, on_delete=models.CASCADE)

    date = models.DateField()
    hour = models.TimeField()
    status = models.BooleanField(default=False)

    # Técnico asignado al agendamiento
    technician = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Técnico'},
        related_name='technician_schedules'
    )

    def __str__(self):
        return f"{self.date} - {self.hour} - {self.technician.username} - {self.tower.name}"


    Adjunto una imagen de mas o menos como se ve la base de datos
    """