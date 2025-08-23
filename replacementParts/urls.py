from django.urls import path
from . import views

urlpatterns = [
    # Rutas para repuestos
    path('createPart', views.createPart, name="createPart"),
    path('listParts', views.listParts, name="listParts"),
    path("editPart/<int:part_id>/", views.editPart, name="editPart"),
    path("deletePart/<int:part_id>/", views.deletePart, name="deletePart")
]

