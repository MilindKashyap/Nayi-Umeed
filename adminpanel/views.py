from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from django import forms

from accounts.models import Roles, User
from accounts.utils import role_required
from devices.models import Device, DeviceStatusFlow
from repairs.models import RepairAssignment
from marketplace.models import MarketplaceListing, Order
from logistics.models import LogisticsTask


@login_required
@role_required([Roles.ADMIN])
def dashboard(request: HttpRequest) -> HttpResponse:
    """Main admin dashboard with overview stats and charts"""
    # Overview stats
    total_devices = Device.objects.count()
    repaired_devices = Device.objects.filter(status__in=["certified", "listed", "allocated"]).count()
    redistributed_devices = Device.objects.filter(status="allocated").count()
    pending_approval = Device.objects.filter(admin_approval_status="pending").count()
    
    # Recent activity
    recent_devices = Device.objects.select_related("donor").order_by("-created_at")[:10]
    recent_orders = Order.objects.select_related("buyer", "listing__device").order_by("-created_at")[:5]
    
    context = {
        "total_devices": total_devices,
        "repaired_devices": repaired_devices,
        "redistributed_devices": redistributed_devices,
        "pending_approval": pending_approval,
        "recent_devices": recent_devices,
        "recent_orders": recent_orders,
    }
    return render(request, "adminpanel/dashboard.html", context)


@login_required
@role_required([Roles.ADMIN])
def analytics_api(request: HttpRequest) -> JsonResponse:
    """API endpoint for Chart.js data"""
    chart_type = request.GET.get("type", "device_status")
    
    if chart_type == "device_status":
        # Device status distribution
        status_counts = Device.objects.values("status").annotate(count=Count("id"))
        data = {
            "labels": [s[1] for s in Device.STATUS_CHOICES],
            "data": [next((item["count"] for item in status_counts if item["status"] == s[0]), 0) 
                    for s in Device.STATUS_CHOICES],
        }
    
    elif chart_type == "device_category":
        # Device category distribution
        category_counts = Device.objects.values("category").annotate(count=Count("id"))
        data = {
            "labels": [dict(Device.CATEGORY_CHOICES).get(cat["category"], cat["category"]) 
                      for cat in category_counts],
            "data": [cat["count"] for cat in category_counts],
        }
    
    elif chart_type == "monthly_trends":
        # Monthly device submissions (last 6 months)
        months = []
        counts = []
        for i in range(5, -1, -1):
            month_start = timezone.now() - timedelta(days=30 * i)
            month_end = month_start + timedelta(days=30)
            count = Device.objects.filter(
                created_at__gte=month_start, created_at__lt=month_end
            ).count()
            months.append(month_start.strftime("%b %Y"))
            counts.append(count)
        data = {"labels": months, "data": counts}
    
    elif chart_type == "approval_status":
        # Admin approval status distribution
        approval_counts = Device.objects.values("admin_approval_status").annotate(count=Count("id"))
        data = {
            "labels": [dict(Device.ADMIN_APPROVAL_CHOICES).get(stat["admin_approval_status"], stat["admin_approval_status"])
                      for stat in approval_counts],
            "data": [stat["count"] for stat in approval_counts],
        }
    
    else:
        data = {"labels": [], "data": []}
    
    return JsonResponse(data)


def _ensure_marketplace_listings():
    """Helper function to create MarketplaceListing for all approved devices that don't have one"""
    from marketplace.models import MarketplaceListing
    
    approved_devices = Device.objects.filter(
        admin_approval_status="approved"
    )
    
    created_count = 0
    for device in approved_devices:
        # Check if device already has a marketplace listing
        if not hasattr(device, 'market_listing'):
            listing_price = device.price if device.price else 0
            MarketplaceListing.objects.create(
                device=device,
                price=listing_price,
                is_active=True
            )
            created_count += 1
    
    return created_count


@login_required
@role_required([Roles.ADMIN])
def device_management(request: HttpRequest) -> HttpResponse:
    """Device management with approve/reject/hold actions"""
    # Ensure all approved devices have marketplace listings
    _ensure_marketplace_listings()
    
    approval_filter = request.GET.get("approval_status", "")
    status_filter = request.GET.get("status", "")
    
    devices = Device.objects.select_related("donor").order_by("-created_at")
    
    if approval_filter:
        devices = devices.filter(admin_approval_status=approval_filter)
    if status_filter:
        devices = devices.filter(status=status_filter)
    
    context = {
        "devices": devices,
        "approval_statuses": Device.ADMIN_APPROVAL_CHOICES,
        "statuses": Device.STATUS_CHOICES,
        "current_approval_filter": approval_filter,
        "current_status_filter": status_filter,
    }
    return render(request, "adminpanel/device_management.html", context)


class DeviceApprovalForm(forms.Form):
    approval_status = forms.ChoiceField(choices=Device.ADMIN_APPROVAL_CHOICES)
    admin_notes = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), required=False)
    status_override = forms.ChoiceField(
        choices=[("", "No Override")] + list(Device.STATUS_CHOICES),
        required=False
    )


@login_required
@role_required([Roles.ADMIN])
def device_approval_action(request: HttpRequest, device_id: int) -> HttpResponse:
    """Handle device approval/rejection/hold actions"""
    device = get_object_or_404(Device, pk=device_id)
    
    if request.method == "POST":
        form = DeviceApprovalForm(request.POST)
        if form.is_valid():
            old_approval = device.admin_approval_status
            device.admin_approval_status = form.cleaned_data["approval_status"]
            device.admin_notes = form.cleaned_data["admin_notes"]
            
            # Manual status override if provided
            status_override = form.cleaned_data["status_override"]
            if status_override:
                try:
                    device.transition_to(status_override, note=f"Admin override: {form.cleaned_data['admin_notes']}")
                except ValueError:
                    # If transition fails, just update status directly (admin override)
                    device.status = status_override
                    device.save(update_fields=["status", "updated_at"])
            
            device.save(update_fields=["admin_approval_status", "admin_notes", "status", "updated_at"])
            
            # Auto-create MarketplaceListing for all approved devices
            if device.admin_approval_status == "approved":
                from marketplace.models import MarketplaceListing
                if not hasattr(device, 'market_listing'):
                    # Use device price if available, otherwise set a default price of 0
                    listing_price = device.price if device.price else 0
                    MarketplaceListing.objects.create(
                        device=device,
                        price=listing_price,
                        is_active=True
                    )
            
            if old_approval != device.admin_approval_status:
                messages.success(
                    request,
                    f"Device {device.listing_id} {device.get_admin_approval_status_display().lower()}."
                )
            return redirect("adminpanel:device_management")
    else:
        form = DeviceApprovalForm(initial={
            "approval_status": device.admin_approval_status,
            "admin_notes": device.admin_notes,
        })
    
    return render(request, "adminpanel/device_approval.html", {"device": device, "form": form})


@login_required
@role_required([Roles.ADMIN])
def assign_repair_center(request: HttpRequest, device_id: int) -> HttpResponse:
    """Assign device to repair partner"""
    device = get_object_or_404(Device, pk=device_id)
    repair_partners = User.objects.filter(role=Roles.REPAIR_PARTNER)
    
    if request.method == "POST":
        partner_id = request.POST.get("repair_partner")
        if partner_id:
            partner = get_object_or_404(User, pk=partner_id, role=Roles.REPAIR_PARTNER)
            # Create or update repair assignment
            assignment, created = RepairAssignment.objects.get_or_create(
                device=device,
                defaults={"repair_partner": partner, "status": "pending"}
            )
            if not created:
                assignment.repair_partner = partner
                assignment.save(update_fields=["repair_partner", "updated_at"])
            
            # Update device status if needed
            if device.status == "submitted" or device.status == "picked_up":
                try:
                    device.transition_to("under_inspection", note=f"Assigned to {partner.get_full_name()}")
                except ValueError:
                    pass
            
            messages.success(request, f"Device assigned to {partner.get_full_name()}")
            return redirect("adminpanel:device_management")
        else:
            messages.error(request, "Please select a repair partner")
    
    context = {
        "device": device,
        "repair_partners": repair_partners,
        "existing_assignment": RepairAssignment.objects.filter(device=device).first(),
    }
    return render(request, "adminpanel/assign_repair.html", context)


@login_required
@role_required([Roles.ADMIN])
def user_management(request: HttpRequest) -> HttpResponse:
    """User and partner management"""
    role_filter = request.GET.get("role", "")
    users = User.objects.all().order_by("-date_joined")
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    # Stats - convert to dict with role keys
    user_stats = {}
    for role_value, role_label in Roles.choices:
        user_stats[role_value] = User.objects.filter(role=role_value).count()
    
    context = {
        "users": users,
        "roles": Roles.choices,
        "current_role_filter": role_filter,
        "user_stats": user_stats,
    }
    return render(request, "adminpanel/user_management.html", context)


@login_required
@role_required([Roles.ADMIN])
def order_management(request: HttpRequest) -> HttpResponse:
    """Order management - view all orders with buyer and shipping details"""
    status_filter = request.GET.get("status", "")
    
    orders = Order.objects.select_related("buyer", "listing__device").order_by("-created_at")
    
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # Stats
    total_orders = Order.objects.count()
    pending_orders = Order.objects.filter(status__in=["placed", "confirmed"]).count()
    delivered_orders = Order.objects.filter(status="delivered").count()
    cancelled_orders = Order.objects.filter(status="cancelled").count()
    
    context = {
        "orders": orders,
        "status_choices": Order.STATUS_CHOICES,
        "current_status_filter": status_filter,
        "total_orders": total_orders,
        "pending_orders": pending_orders,
        "delivered_orders": delivered_orders,
        "cancelled_orders": cancelled_orders,
    }
    return render(request, "adminpanel/order_management.html", context)


@login_required
@role_required([Roles.ADMIN])
def order_detail(request: HttpRequest, order_id: int) -> HttpResponse:
    """View detailed order information"""
    order = get_object_or_404(
        Order.objects.select_related("buyer", "listing__device").prefetch_related("history"),
        pk=order_id
    )
    
    return render(request, "adminpanel/order_detail.html", {"order": order})


@login_required
@role_required([Roles.ADMIN])
def user_edit(request: HttpRequest, user_id: int) -> HttpResponse:
    """Edit user role and details"""
    user = get_object_or_404(User, pk=user_id)
    
    if request.method == "POST":
        new_role = request.POST.get("role")
        is_active = request.POST.get("is_active") == "on"
        if new_role in [r[0] for r in Roles.choices]:
            user.role = new_role
            user.is_active = is_active
            user.save(update_fields=["role", "is_active"])
            messages.success(request, f"User {user.username} updated successfully")
            return redirect("adminpanel:user_management")
    
    context = {
        "user": user,
        "roles": Roles.choices,
    }
    return render(request, "adminpanel/user_edit.html", context)

