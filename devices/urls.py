from django.urls import path

from . import views

app_name = "devices"

urlpatterns = [
    path("create/", views.device_create, name="create"),
    path("mine/", views.my_devices, name="my_devices"),
    path("<int:pk>/", views.device_detail, name="detail"),
    path("<int:pk>/status/", views.update_status, name="update_status"),
]

