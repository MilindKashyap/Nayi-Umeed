from django.urls import path

from . import views

app_name = "marketplace"

urlpatterns = [
    path("", views.public_listings, name="public_listings"),
    path("api/listings/", views.listings_api, name="listings_api"),
    path("<int:pk>/", views.listing_detail, name="detail"),
    path("<int:pk>/order/", views.place_order, name="place_order"),
    path("orders/<int:order_id>/", views.order_status, name="order_status"),
    path("api/orders/<int:order_id>/", views.order_status_api, name="order_status_api"),
]

