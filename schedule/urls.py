from django.urls import path
from . import views

urlpatterns = [
    path('listSchedule/', views.listSchedule, name="listSchedule"),
    path('createSchedule/', views.createSchedule, name="createSchedule"),
    path('editSchedule/', views.editSchedule, name="editSchedule"),
    path('deleteSchedule/', views.deleteSchedule, name="deleteSchedule"),
    path("building-suggestions/", views.building_suggestions, name="building_suggestions"),
    path("tower-suggestions/", views.tower_suggestions, name="tower_suggestions"),
    path('building_suggestionsS/', views.building_suggestionsS, name="building_suggestionsS")
]
