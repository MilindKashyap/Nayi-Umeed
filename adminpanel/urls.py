from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("analytics/api/", views.analytics_api, name="analytics_api"),
    path("devices/", views.device_management, name="device_management"),
    path("devices/<int:device_id>/approve/", views.device_approval_action, name="device_approval"),
    path("devices/<int:device_id>/assign-repair/", views.assign_repair_center, name="assign_repair"),
    path("users/", views.user_management, name="user_management"),
    path("users/<int:user_id>/edit/", views.user_edit, name="user_edit"),
    path("orders/", views.order_management, name="order_management"),
    path("orders/<int:order_id>/", views.order_detail, name="order_detail"),
]

