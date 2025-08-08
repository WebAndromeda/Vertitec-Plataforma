from django.urls import path
from . import views

urlpatterns = [
    # Rutas para administradores y tecnicos
    path('', views.index, name="index"),
    path('createUser/', views.createUser, name="createUser"),
    path('userList/', views.userList, name="userList"),
    path('deleteUser/', views.deleteUser, name="deleteUser"),
    path('editUser/', views.editUser, name="editUser"), 
    path('login/', views.login, name="login"),
    path('logout/', views.user_logout, name="logout"),
]
