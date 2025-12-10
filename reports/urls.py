from django.urls import path
from . import views

urlpatterns = [
    path('createReport/', views.createReport, name="createReport"),
    path('listReports/', views.listReports, name="listReports"),
    path("delete/<int:report_id>/", views.deleteReport, name="deleteReport"),
]
