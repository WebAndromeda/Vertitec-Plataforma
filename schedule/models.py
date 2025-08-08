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
    
    # Se usa para poder mostrar la direccion de un edificio donde se requiera, sin necesidad de crear un campo en este modelo con un Foreign Key hacia el modelo "buildings"
    @property
    def address(self):
        return self.client.buildings.address  # Gracias al OneToOne