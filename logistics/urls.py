from django.urls import path
from . import views

app_name = "logistics"

urlpatterns = [
    path("tasks/", views.task_list, name="task_list"),
    path("tasks/<int:pk>/", views.task_detail, name="task_detail"),
    path("pickup/create/<int:device_id>/", views.create_pickup_task, name="create_pickup_task"),
    path("delivery/create/<int:order_id>/", views.create_delivery_task, name="create_delivery_task"),
]

