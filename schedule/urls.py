from django.urls import path
from . import views

urlpatterns = [
    path('listSchedule/', views.listSchedule, name="listSchedule"),
    path('createSchedule/', views.createSchedule, name="createSchedule"),
    path('editSchedule/', views.editSchedule, name="editSchedule"),
    path('deleteSchedule/', views.deleteSchedule, name="deleteSchedule")
]
