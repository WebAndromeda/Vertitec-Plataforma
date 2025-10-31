from django.urls import path
from . import views

urlpatterns = [
    # Rutas para repuestos
    path('listParts', views.listParts, name="listParts"),
    path('listPartsClient', views.listPartsClient, name="listPartsClient"),
    path("repuesto/<int:part_id>/<str:action>/", views.toggle_approval, name="toggle_approval"),
    path("editPart/<int:part_id>/", views.editPart, name="editPart"),
    path("deletePart/<int:part_id>/", views.deletePart, name="deletePart")
]

