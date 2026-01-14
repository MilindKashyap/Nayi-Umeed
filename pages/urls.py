from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("about/", views.about_us_view, name="about"),
    path("contact/", views.contact_us_view, name="contact"),
]
