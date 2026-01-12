from django.contrib import admin

from .models import Device, DeviceImage, DeviceStatusHistory


class DeviceImageInline(admin.TabularInline):
    model = DeviceImage
    extra = 0


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("title", "listing_id", "category", "status", "donor", "created_at")
    list_filter = ("status", "category", "condition")
    search_fields = ("title", "listing_id", "donor__username")
    inlines = [DeviceImageInline]


@admin.register(DeviceStatusHistory)
class DeviceStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("device", "from_status", "to_status", "changed_at")
    list_filter = ("to_status",)

