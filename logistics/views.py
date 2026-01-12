from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django import forms

from accounts.models import Roles
from accounts.utils import role_required
from devices.models import Device
from marketplace.models import Order

from .models import LogisticsTask, TaskStatus, TaskType, TaskStatusHistory


class TaskStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = LogisticsTask
        fields = ["status", "pickup_proof", "delivery_proof", "pickup_latitude", "pickup_longitude", 
                  "delivery_latitude", "delivery_longitude", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            "pickup_latitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "e.g., 28.6139"}),
            "pickup_longitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "e.g., 77.2090"}),
            "delivery_latitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "e.g., 28.6139"}),
            "delivery_longitude": forms.NumberInput(attrs={"step": "0.000001", "placeholder": "e.g., 77.2090"}),
        }


@login_required
@role_required([Roles.ADMIN, Roles.REPAIR_PARTNER])  # Logistics staff can be repair partners or admins
def task_list(request: HttpRequest) -> HttpResponse:
    """Display all logistics tasks assigned to current user or all tasks for admins"""
    if request.user.role == Roles.ADMIN:
        tasks = LogisticsTask.objects.select_related("device", "order", "assigned_to").all()
    else:
        tasks = LogisticsTask.objects.select_related("device", "order", "assigned_to").filter(
            assigned_to=request.user
        )
    
    # Filter by task type if provided
    task_type = request.GET.get("type")
    if task_type in [TaskType.PICKUP, TaskType.DELIVERY]:
        tasks = tasks.filter(task_type=task_type)
    
    # Filter by status if provided
    status_filter = request.GET.get("status")
    if status_filter in [s[0] for s in TaskStatus.choices]:
        tasks = tasks.filter(status=status_filter)
    
    return render(request, "logistics/task_list.html", {"tasks": tasks})


@login_required
@role_required([Roles.ADMIN, Roles.REPAIR_PARTNER])
def task_detail(request: HttpRequest, pk: int) -> HttpResponse:
    """View and update logistics task details"""
    task = get_object_or_404(
        LogisticsTask.objects.select_related("device", "order", "assigned_to").prefetch_related("history"),
        pk=pk
    )
    
    # Check access - assigned user or admin
    if request.user.role != Roles.ADMIN and task.assigned_to != request.user:
        messages.error(request, "You don't have permission to access this task.")
        return redirect("logistics:task_list")
    
    if request.method == "POST":
        form = TaskStatusUpdateForm(request.POST, request.FILES, instance=task)
        if form.is_valid():
            old_status = task.status
            task = form.save()
            
            # Handle status transitions with proof uploads
            if task.status == TaskStatus.PICKED_UP and old_status == TaskStatus.ASSIGNED:
                if task.pickup_proof:
                    task.mark_picked_up(
                        proof_image=task.pickup_proof,
                        latitude=task.pickup_latitude,
                        longitude=task.pickup_longitude,
                        notes=task.notes
                    )
                    messages.success(request, "Task marked as picked up with proof.")
                else:
                    messages.warning(request, "Status updated but proof upload recommended.")
            
            elif task.status == TaskStatus.DELIVERED and old_status == TaskStatus.PICKED_UP:
                if task.delivery_proof:
                    task.mark_delivered(
                        proof_image=task.delivery_proof,
                        latitude=task.delivery_latitude,
                        longitude=task.delivery_longitude,
                        notes=task.notes
                    )
                    messages.success(request, "Task marked as delivered with proof.")
                else:
                    messages.warning(request, "Status updated but proof upload recommended.")
            
            else:
                messages.success(request, "Task updated successfully.")
            
            return redirect("logistics:task_detail", pk=task.pk)
    else:
        form = TaskStatusUpdateForm(instance=task)
    
    return render(request, "logistics/task_detail.html", {"task": task, "form": form})


@login_required
@role_required([Roles.ADMIN])
def create_pickup_task(request: HttpRequest, device_id: int) -> HttpResponse:
    """Admin-only: Create pickup task for a device"""
    device = get_object_or_404(Device, pk=device_id)
    if request.method == "POST":
        address = request.POST.get("pickup_address", "").strip()
        assigned_to_id = request.POST.get("assigned_to")
        if not address:
            messages.error(request, "Pickup address is required.")
            return redirect("devices:detail", pk=device_id)
        
        task = LogisticsTask.objects.create(
            task_type=TaskType.PICKUP,
            device=device,
            pickup_address=address,
            assigned_to_id=assigned_to_id if assigned_to_id else None,
        )
        TaskStatusHistory.objects.create(task=task, status=TaskStatus.ASSIGNED, note="Task created")
        messages.success(request, f"Pickup task created for {device.listing_id}")
        return redirect("logistics:task_detail", pk=task.pk)
    
    return redirect("devices:detail", pk=device_id)


@login_required
@role_required([Roles.ADMIN])
def create_delivery_task(request: HttpRequest, order_id: int) -> HttpResponse:
    """Admin-only: Create delivery task for an order"""
    order = get_object_or_404(Order.objects.select_related("listing__device"), pk=order_id)
    if request.method == "POST":
        assigned_to_id = request.POST.get("assigned_to")
        task = LogisticsTask.objects.create(
            task_type=TaskType.DELIVERY,
            order=order,
            delivery_address=order.shipping_address,
            assigned_to_id=assigned_to_id if assigned_to_id else None,
        )
        TaskStatusHistory.objects.create(task=task, status=TaskStatus.ASSIGNED, note="Task created")
        messages.success(request, f"Delivery task created for Order #{order.id}")
        return redirect("logistics:task_detail", pk=task.pk)
    
    return redirect("marketplace:order_status", order_id=order_id)

