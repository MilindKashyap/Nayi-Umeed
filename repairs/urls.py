from django.urls import path

from . import views

app_name = "repairs"

urlpatterns = [
    path("assigned/", views.assigned_list, name="assigned_list"),
    path("assigned/<int:pk>/", views.assignment_detail, name="assignment_detail"),
]


