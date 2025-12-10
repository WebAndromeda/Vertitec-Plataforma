from django.db import models
from django.contrib.auth.models import User
from buildings.models import buildings, towers

class schedule(models.Model):
    RECURRENCE_CHOICES = [
        ('single', 'Individual'),
        ('monthly', 'Mensual'),
    ]

    PROGRAMMING_OPTIONS = [
        ('programmed', 'Programado'),
        ('not_programmed', 'No programado')
    ]

    STATUS_CHOICES = [
        ('to_be_done', 'Por realizar'),
        ('in_production', 'En producción'),
        ('complete', 'Realizado'),
    ]
    # Usuario que solicita el agendamiento (cliente)
    client = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Cliente'},
        related_name='client_schedules'
    )

    tower = models.ForeignKey(towers, on_delete=models.CASCADE)

    date = models.DateField()
    hour = models.TimeField()

    # Nuevo status con opciones
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='por_realizar'
    )

    # Recurrencia
    recurrence = models.CharField(
        max_length=20,
        choices=RECURRENCE_CHOICES,
        default='single'
    )
    
    # Programado o no programado
    programmed = models.CharField(
        max_length=20,
        choices=PROGRAMMING_OPTIONS,
        default='programmed'
    )

    # Técnico asignado
    technician = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'groups__name': 'Técnico'},
        related_name='technician_schedules'
    )

    def __str__(self):
        return f"{self.date} - {self.hour} - {self.technician.username} - {self.tower.name} ({self.get_recurrence_display()})"

    @property
    def address(self):
        return self.client.buildings.address
