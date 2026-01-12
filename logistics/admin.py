from django.contrib import admin
from .models import LogisticsTask, TaskStatusHistory


@admin.register(LogisticsTask)
class LogisticsTaskAdmin(admin.ModelAdmin):
    list_display = ["id", "task_type", "status", "device", "order", "assigned_to", "assigned_at"]
    list_filter = ["task_type", "status", "assigned_at"]
    search_fields = ["device__listing_id", "order__id", "pickup_address", "delivery_address"]
    readonly_fields = ["assigned_at", "picked_up_at", "delivered_at", "updated_at"]
    
    fieldsets = (
        ("Task Info", {
            "fields": ("task_type", "status", "device", "order", "assigned_to")
        }),
        ("Addresses", {
            "fields": ("pickup_address", "delivery_address")
        }),
        ("Proof & Geo-tracking", {
            "fields": ("pickup_proof", "delivery_proof", 
                      "pickup_latitude", "pickup_longitude",
                      "delivery_latitude", "delivery_longitude")
        }),
        ("Timestamps", {
            "fields": ("assigned_at", "picked_up_at", "delivered_at", "updated_at")
        }),
        ("Notes", {
            "fields": ("notes",)
        }),
    )


@admin.register(TaskStatusHistory)
class TaskStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ["task", "status", "note", "changed_at"]
    list_filter = ["status", "changed_at"]
    readonly_fields = ["task", "status", "note", "changed_at"]

