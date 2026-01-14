from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import ContactForm


def about_us_view(request: HttpRequest) -> HttpResponse:
    """About Us page - visible to all users"""
    return render(request, "pages/about.html")


def contact_us_view(request: HttpRequest) -> HttpResponse:
    """Contact Us page with contact form - visible to all users"""
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Here you can add email sending logic later
            # For now, just show success message
            name = form.cleaned_data["name"]
            messages.success(
                request,
                f"Thank you, {name}! Your message has been received. We'll respond within 24-48 hours."
            )
            form = ContactForm()  # Reset form after successful submission
        else:
            messages.error(request, "Please correct the errors below and try again.")
    else:
        form = ContactForm()
    
    return render(request, "pages/contact.html", {"form": form})
