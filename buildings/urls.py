from django.urls import path
from . import views

urlpatterns = [
    # Rutas para edificios / cliente
    path('listBuildings', views.listBuildings, name="listBuildings"),
    path('createBuilding', views.createBuilding, name="createBuilding"),
    path('editBuilding', views.editBuilding, name="editBuilding"),
    path('deactivateBuilding', views.deactivateBuilding, name="deactivateBuilding"),
    path('activateBuilding', views.activateBuilding, name="activateBuilding"),
    path('listTowers', views.listTowers, name="listTowers"),
    path('deleteTower', views.deleteTower, name="deleteTower"),
    path('building_suggestionsB/', views.building_suggestionsB, name="building_suggestionsB")
]
