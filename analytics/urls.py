from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path("", views.impact_dashboard, name="impact_dashboard"),
    path("api/impact/", views.impact_api, name="impact_api"),
]


