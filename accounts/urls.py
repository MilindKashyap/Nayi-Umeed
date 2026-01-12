from django.urls import path

from .views import RoleAwareLoginView, admin_only_view, dashboard_view, logout_view, otp_verify_view, register_view

app_name = "accounts"

urlpatterns = [
    path("register/", register_view, name="register"),
    path("login/", RoleAwareLoginView.as_view(), name="login"),
    path("logout/", logout_view, name="logout"),
    path("otp-verify/", otp_verify_view, name="otp_verify"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("admin-only/", admin_only_view, name="admin_only"),
]

