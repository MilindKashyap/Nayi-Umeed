from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Roles
from accounts.utils import role_required

from .forms import DeviceForm, DeviceStatusUpdateForm
from .models import Device, DeviceImage, DeviceStatusFlow, DeviceStatusHistory


@login_required
@role_required([Roles.DONOR, Roles.BOTH, Roles.ADMIN])
def device_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = DeviceForm(request.POST)
        if form.is_valid():
            device = form.save(commit=False)
            device.donor = request.user
            device.status = DeviceStatusFlow[0]
            device.save()
            DeviceStatusHistory.objects.create(
                device=device, from_status=device.status, to_status=device.status, note="Submitted"
            )
            for file in request.FILES.getlist("images"):
                DeviceImage.objects.create(device=device, image=file)
            messages.success(request, "Device submitted successfully.")
            return redirect("devices:detail", pk=device.pk)
    else:
        form = DeviceForm()
    return render(request, "devices/device_form.html", {"form": form})


@login_required
@role_required([Roles.DONOR, Roles.BOTH, Roles.ADMIN])
def my_devices(request: HttpRequest) -> HttpResponse:
    devices = Device.objects.filter(donor=request.user)
    return render(request, "devices/device_list.html", {"devices": devices})


@login_required
def device_detail(request: HttpRequest, pk: int) -> HttpResponse:
    device = get_object_or_404(Device, pk=pk)
    if request.user.role not in [Roles.ADMIN, Roles.BOTH] and device.donor != request.user:
        messages.error(request, "You cannot access this device.")
        return redirect("accounts:dashboard")
    return render(request, "devices/device_detail.html", {"device": device})


@login_required
@role_required([Roles.ADMIN])
def update_status(request: HttpRequest, pk: int) -> HttpResponse:
    device = get_object_or_404(Device, pk=pk)
    if request.method == "POST":
        form = DeviceStatusUpdateForm(request.POST, instance=device)
        if form.is_valid():
            try:
                device.transition_to(form.cleaned_data["status"])
                messages.success(request, "Status updated.")
            except ValueError as exc:
                messages.error(request, str(exc))
        return redirect("devices:detail", pk=pk)
    else:
        form = DeviceStatusUpdateForm(instance=device)
    return render(request, "devices/device_status_form.html", {"form": form, "device": device})

