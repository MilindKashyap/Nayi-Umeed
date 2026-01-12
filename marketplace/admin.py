from django.contrib import admin

from .models import MarketplaceListing, Order, OrderStatusHistory


@admin.register(MarketplaceListing)
class MarketplaceListingAdmin(admin.ModelAdmin):
    list_display = ("device", "price", "is_active", "created_at")
    list_filter = ("is_active",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "buyer", "status", "created_at")
    list_filter = ("status",)


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("order", "status", "changed_at")

