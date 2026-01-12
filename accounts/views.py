import random

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy

from .forms import LoginForm, OTPForm, RegistrationForm
from .models import OTPRequest, Roles, User
from .utils import role_required


def _generate_mock_otp() -> str:
    return f"{random.randint(100000, 999999)}"


def _create_otp(user: User, request: HttpRequest) -> str:
    code = _generate_mock_otp()
    OTPRequest.objects.create(user=user, code=code)
    request.session["otp_user_id"] = user.id
    request.session["otp_code"] = code
    return code


def register_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user: User = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.role = form.cleaned_data["role"]
            user.phone_number = form.cleaned_data["phone_number"]
            user.save()
            otp_code = _create_otp(user, request)
            messages.success(request, f"Mock OTP generated: {otp_code}")
            return redirect("accounts:otp_verify")
    else:
        form = RegistrationForm()
    return render(request, "accounts/register.html", {"form": form})


class RoleAwareLoginView(LoginView):
    authentication_form = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        user: User = self.request.user
        if not user.otp_verified:
            otp_code = _create_otp(user, self.request)
            messages.info(self.request, f"Mock OTP generated: {otp_code}")
            logout(self.request)
            return redirect("accounts:otp_verify")
        return response


def otp_verify_view(request: HttpRequest) -> HttpResponse:
    user_id = request.session.get("otp_user_id")
    session_code = request.session.get("otp_code")
    if not user_id or not session_code:
        messages.error(request, "No OTP pending.")
        return redirect("accounts:login")

    user = User.objects.filter(id=user_id).first()
    if not user:
        messages.error(request, "User not found for OTP.")
        return redirect("accounts:login")

    if request.method == "POST":
        form = OTPForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["code"] == session_code:
                user.otp_verified = True
                user.save(update_fields=["otp_verified"])
                OTPRequest.objects.filter(user=user, code=session_code).update(is_used=True)
                login(request, user)
                for key in ("otp_user_id", "otp_code"):
                    request.session.pop(key, None)
                messages.success(request, "Phone verified.")
                return redirect("accounts:dashboard")
            messages.error(request, "Invalid OTP. Use the mock code shown above.")
    else:
        form = OTPForm()

    return render(request, "accounts/otp_verify.html", {"form": form, "code": session_code})


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    user: User = request.user
    if user.role == Roles.DONOR:
        return redirect("devices:my_devices")
    if user.role == Roles.BUYER:
        return redirect("marketplace:public_listings")
    if user.role == Roles.BOTH:
        return render(request, "accounts/dashboard.html", {"user": user})
    if user.role == Roles.ADMIN:
        return redirect("adminpanel:dashboard")
    if user.role == Roles.REPAIR_PARTNER:
        return redirect("repairs:assigned_list")
    return redirect("accounts:login")


@login_required
def logout_view(request: HttpRequest) -> HttpResponse:
    """Custom logout view that handles GET requests"""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("accounts:login")


@login_required
@role_required([Roles.ADMIN])
def admin_only_view(request: HttpRequest) -> HttpResponse:
    return HttpResponse("Admin area placeholder")

