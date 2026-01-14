from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def about_us_view(request: HttpRequest) -> HttpResponse:
    """About Us page - visible to all users"""
    return render(request, "pages/about.html")
