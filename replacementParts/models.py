from django.db import models
from django.contrib.auth.models import User
from buildings.models import towers 

# Repuestos
class replacementParts(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    nameItem = models.CharField(max_length=255)
    approved_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')

    statusInstall = [
        ('por_instalar', 'Pendiente por instalar'),
        ('instalado', 'Instalado'),
    ]
    status_Install = models.CharField(max_length=20, choices=statusInstall, default='por_instalar')

    statusPayment = [
        ('no_aplica', 'No aplica'),
        ('pendiente_anticipo', 'Pendiente anticipo'),
    ]
    status_Payment = models.CharField(max_length=20, choices=statusPayment, default='no_aplica')

    # Nuevos campos — (versión final, obligatorios)
    fecha = models.DateField()
    numero_cotizacion = models.PositiveIntegerField()
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    precio_total = models.DecimalField(max_digits=12, decimal_places=2)

    tower = models.ForeignKey(towers, on_delete=models.CASCADE, related_name="repuestos")
    building = models.ForeignKey(User, on_delete=models.CASCADE, related_name="repuestos")

    def __str__(self):
        return f"{self.nameItem} - Torre {self.tower.name}"
