from functools import wraps
from typing import Iterable

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect

from .models import Roles, User


def role_required(allowed_roles: Iterable[str]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user: User = request.user
            if not user.is_authenticated:
                messages.error(request, "Login required.")
                return redirect("accounts:login")
            if user.role not in allowed_roles:
                messages.error(request, "You do not have permission to access this area.")
                return redirect("accounts:dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator

