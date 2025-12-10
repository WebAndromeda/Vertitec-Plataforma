from django.db import models
from schedule.models import schedule


class Report(models.Model):
    # Relación 1 a 1 → un agendamiento solo puede tener un reporte
    schedule = models.OneToOneField(
        schedule,
        on_delete=models.CASCADE,
        related_name="report"
    )

    # Hora de llegada del técnico
    check_in_time = models.TimeField(null=True, blank=True)

    # Hora de salida del técnico
    check_out_time = models.TimeField(null=True, blank=True)

    # Tiempo total que tomó la visita
    time_spent = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Tiempo total"
    )

    # Observaciones generales
    general_observations = models.TextField(
        blank=True,
        verbose_name="Observaciones generales"
    )

    # Recomendaciones especiales
    special_recommendations = models.TextField(
        blank=True,
        verbose_name="Recomendaciones especiales"
    )

    def __str__(self):
        return f"Reporte del agendamiento #{self.schedule.id} - {self.schedule.date}"