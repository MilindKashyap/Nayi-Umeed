from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def root_redirect(request):
    """Redirect root URL to dashboard if authenticated, otherwise to login"""
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    return redirect("accounts:login")

urlpatterns = [
    path("", root_redirect, name="home"),
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("devices/", include("devices.urls")),
    path("marketplace/", include("marketplace.urls")),
    path("repairs/", include("repairs.urls")),
    path("logistics/", include("logistics.urls")),
    path("adminpanel/", include("adminpanel.urls")),
    path("analytics/", include("analytics.urls")),
    path("pages/", include("pages.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
