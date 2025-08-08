from django.db import models
from django.contrib.auth.models import User

# Modelo de edificios / clientes
class buildings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Cuando se elimine el usuario relacionado, elimina también automáticamente este building
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.user.first_name


# Modelo para crear torres   
class towers(models.Model):
    building = models.ForeignKey(buildings, on_delete=models.CASCADE, related_name='towers')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.building.user.username}"
    
