from django.urls import path
from . import views

urlpatterns = [
    # Rutas para administradores y tecnicos
    path('', views.index, name="index"),
    path('createUser/', views.createUser, name="createUser"),
    path('userList/', views.userList, name="userList"),
    path('deactivateUser/', views.deactivateUser, name="deactivateUser"),
    path('activateUser/', views.activateUser, name="activateUser"),
    path('editUser/', views.editUser, name="editUser"), 
    path('login/', views.login, name="login"),
    path('logout/', views.user_logout, name="logout"),
    path('user-suggestions/', views.user_suggestions, name="user_suggestions"),
]