from django.db import models
from django.contrib.auth.models import User
from buildings.models import buildings, towers

class schedule(models.Model):
    RECURRENCE_CHOICES = [
        ('single', 'Individual'),
        ('monthly', 'Mensual'),
        # ('weekly', 'Semanal'),   # <-- En caso de necesitar mas en el futuro
        # ('yearly', 'Anual'),
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
    status = models.BooleanField(default=False)

    # Recurrencia
    recurrence = models.CharField(
        max_length=20,
        choices=RECURRENCE_CHOICES,
        default='single'
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
        return self.client.buildings.address  # Gracias al OneToOne
