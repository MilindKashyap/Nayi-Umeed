from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, OTPRequest


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role & Contact", {"fields": ("role", "phone_number", "otp_verified")}),
    )
    list_display = ("username", "email", "phone_number", "role", "is_staff")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "phone_number")


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at", "is_used")
    list_filter = ("is_used", "created_at")

