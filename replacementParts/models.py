from django.db import models
from django.contrib.auth.models import User
from buildings.models import towers 

class replacementParts(models.Model):
    STATUS_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
    ]

    nameItem = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    approved_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendiente')

    statusInstall = [
        ('por_instalar', 'Por instalar'),
        ('instalado', 'Instalado'),
    ]
    status_Install = models.CharField(max_length=20, choices=statusInstall, default='por_instalar')

    statusPayment = [
        ('pagado', 'Pagado'),
        ('falta_pago', 'Falta de pago'),
    ]
    status_Payment = models.CharField(max_length=20, choices=statusPayment, default='falta_pago')

    tower = models.ForeignKey(towers, on_delete=models.CASCADE, related_name="repuestos")
    building = models.ForeignKey(User, on_delete=models.CASCADE, related_name="repuestos")  # 🔹 Relación con el usuario

    def __str__(self):
        return f"{self.nameItem} - Torre {self.tower.name}"