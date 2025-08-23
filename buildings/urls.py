from django.urls import path
from . import views

urlpatterns = [
    # Rutas para edificios / cliente
    path('listBuildings', views.listBuildings, name="listBuildings"),
    path('createBuilding', views.createBuilding, name="createBuilding"),
    path('editBuilding', views.editBuilding, name="editBuilding"),
    path('deleteBuilding', views.deleteBuilding, name="deleteBuilding"),
    path('listTowers', views.listTowers, name="listTowers"),
    path('addTower/<int:building_id>/', views.addTower, name='addTower'),
    path('editTowers', views.editTowers, name="editTowers"),
    path('deleteTower', views.deleteTower, name="deleteTower"),
    path('user-suggestions/', views.user_suggestions, name="user_suggestions")
]
