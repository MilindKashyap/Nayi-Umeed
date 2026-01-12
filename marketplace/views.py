from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Roles
from accounts.utils import role_required
from devices.models import Device

from .models import MarketplaceListing, Order, OrderStatusHistory


def public_listings(request: HttpRequest) -> HttpResponse:
    listings = _filter_listings(request)
    # Ensure QuerySet is evaluated to a list for template rendering
    listings_list = list(listings)
    return render(request, "marketplace/listings.html", {"listings": listings_list})


def listings_api(request: HttpRequest) -> JsonResponse:
    listings = _filter_listings(request)
    data = [
        {
            "id": l.id,
            "title": l.device.title,
            "price": float(l.price),
            "category": l.device.category,
            "condition": l.device.condition,
            "certified": l.is_certified,
            "status": l.device.status,
        }
        for l in listings
    ]
    return JsonResponse({"results": data})


def _filter_listings(request: HttpRequest):
    # Only show listings for devices that are approved by admin
    qs = MarketplaceListing.objects.select_related("device").filter(
        is_active=True,
        device__admin_approval_status="approved"
    )
    category = request.GET.get("category")
    condition = request.GET.get("condition")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")
    if category:
        qs = qs.filter(device__category=category)
    if condition:
        qs = qs.filter(device__condition=condition)
    if price_min:
        qs = qs.filter(price__gte=price_min)
    if price_max:
        qs = qs.filter(price__lte=price_max)
    return qs


def listing_detail(request: HttpRequest, pk: int) -> HttpResponse:
    listing = get_object_or_404(
        MarketplaceListing.objects.select_related("device").prefetch_related("device__history"), pk=pk
    )
    device = listing.device
    return render(
        request,
        "marketplace/detail.html",
        {"listing": listing, "device": device},
    )


@login_required
@role_required([Roles.BUYER, Roles.BOTH, Roles.ADMIN])
def place_order(request: HttpRequest, pk: int) -> HttpResponse:
    listing = get_object_or_404(MarketplaceListing, pk=pk, is_active=True)
    
    # Check if device is already sold
    if listing.is_sold:
        messages.error(request, "This device has already been sold.")
        return redirect("marketplace:detail", pk=pk)
    
    if request.method == "POST":
        address = request.POST.get("shipping_address", "").strip()
        if not address:
            messages.error(request, "Shipping address required.")
            return redirect("marketplace:detail", pk=pk)
        order = Order.objects.create(listing=listing, buyer=request.user, shipping_address=address)
        OrderStatusHistory.objects.create(order=order, status=order.status, note="Order placed")
        messages.success(request, "Order placed successfully.")
        return redirect("marketplace:order_status", order_id=order.id)
    return redirect("marketplace:detail", pk=pk)


@login_required
def order_status(request: HttpRequest, order_id: int) -> HttpResponse:
    order = get_object_or_404(Order.objects.select_related("listing__device"), id=order_id, buyer=request.user)
    return render(request, "marketplace/order_status.html", {"order": order})


@login_required
def order_status_api(request: HttpRequest, order_id: int) -> JsonResponse:
    order = get_object_or_404(Order, id=order_id, buyer=request.user)
    history = [{"status": h.status, "note": h.note, "changed_at": h.changed_at} for h in order.history.all()]
    return JsonResponse({"status": order.status, "history": history})

