from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q, Sum
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.models import Roles
from accounts.utils import role_required
from devices.models import Device
from logistics.models import LogisticsTask, TaskStatus, TaskType
from marketplace.models import Order
from repairs.models import RepairAssignment, RepairStatus

from .models import DeviceImpact, Region, SystemBottleneckSnapshot


@login_required
@role_required([Roles.ADMIN])
def impact_dashboard(request: HttpRequest) -> HttpResponse:
    """High-level impact dashboard with charts."""

    devices_collected = Device.objects.count()
    devices_repaired = Device.objects.filter(status__in=["certified", "listed", "allocated"]).count()
    devices_redistributed = Device.objects.filter(status="allocated").count()

    impact_agg = DeviceImpact.objects.aggregate(
        total_co2=Sum("estimated_co2_saved_kg"), total_beneficiaries=Sum("beneficiaries")
    )
    estimated_co2_saved = impact_agg["total_co2"] or 0
    beneficiaries_served = impact_agg["total_beneficiaries"] or 0

    # Region-wise stats (only regions with data)
    region_stats = (
        Region.objects.annotate(
            devices_collected=Count("device_impacts__id"),
            devices_redistributed=Count(
                "device_impacts__device",
                filter=Q(device_impacts__device__status="allocated"),
            ),
            beneficiaries=Sum("device_impacts__beneficiaries"),
            co2_saved=Sum("device_impacts__estimated_co2_saved_kg"),
        )
        .filter(devices_collected__gt=0)
        .order_by("-devices_collected")
    )

    # Bottlenecks (live)
    pending_approvals = Device.objects.filter(admin_approval_status="pending").count()
    pending_repairs = RepairAssignment.objects.exclude(
        status__in=[RepairStatus.COMPLETED, RepairStatus.CERTIFIED, RepairStatus.REJECTED]
    ).count()
    pending_pickups = LogisticsTask.objects.filter(task_type=TaskType.PICKUP, status=TaskStatus.ASSIGNED).count()
    in_transit_deliveries = LogisticsTask.objects.filter(
        task_type=TaskType.DELIVERY, status=TaskStatus.PICKED_UP
    ).count()

    bottlenecks = {
        "pending_approvals": pending_approvals,
        "pending_repairs": pending_repairs,
        "pending_pickups": pending_pickups,
        "in_transit_deliveries": in_transit_deliveries,
    }

    context = {
        "devices_collected": devices_collected,
        "devices_repaired": devices_repaired,
        "devices_redistributed": devices_redistributed,
        "estimated_co2_saved": estimated_co2_saved,
        "beneficiaries_served": beneficiaries_served,
        "region_stats": region_stats,
        "bottlenecks": bottlenecks,
    }
    return render(request, "analytics/impact_dashboard.html", context)


@login_required
@role_required([Roles.ADMIN])
def impact_api(request: HttpRequest) -> JsonResponse:
    """JSON endpoints feeding Chart.js visualisations."""

    metric_type = request.GET.get("type", "global")

    if metric_type == "global":
        devices_collected = Device.objects.count()
        devices_repaired = Device.objects.filter(status__in=["certified", "listed", "allocated"]).count()
        devices_redistributed = Device.objects.filter(status="allocated").count()
        impact_agg = DeviceImpact.objects.aggregate(
            total_co2=Sum("estimated_co2_saved_kg"), total_beneficiaries=Sum("beneficiaries")
        )
        return JsonResponse(
            {
                "labels": [
                    "Devices Collected",
                    "Devices Repaired",
                    "Devices Redistributed",
                    "Estimated CO₂ Saved (kg)",
                    "Beneficiaries Served",
                ],
                "data": [
                    devices_collected,
                    devices_repaired,
                    devices_redistributed,
                    float(impact_agg["total_co2"] or 0),
                    impact_agg["total_beneficiaries"] or 0,
                ],
            }
        )

    if metric_type == "regions":
        region_data = (
            DeviceImpact.objects.values("region__name")
            .annotate(
                devices=Count("device_id"),
                beneficiaries=Sum("beneficiaries"),
                co2=Sum("estimated_co2_saved_kg"),
            )
            .order_by("-devices")
        )
        return JsonResponse(
            {
                "labels": [r["region__name"] or "Unknown" for r in region_data],
                "devices": [r["devices"] for r in region_data],
                "beneficiaries": [r["beneficiaries"] or 0 for r in region_data],
                "co2": [float(r["co2"] or 0) for r in region_data],
            }
        )

    if metric_type == "bottlenecks":
        pending_approvals = Device.objects.filter(admin_approval_status="pending").count()
        pending_repairs = RepairAssignment.objects.exclude(
            status__in=[RepairStatus.COMPLETED, RepairStatus.CERTIFIED, RepairStatus.REJECTED]
        ).count()
        pending_pickups = LogisticsTask.objects.filter(task_type=TaskType.PICKUP, status=TaskStatus.ASSIGNED).count()
        in_transit_deliveries = LogisticsTask.objects.filter(
            task_type=TaskType.DELIVERY, status=TaskStatus.PICKED_UP
        ).count()
        return JsonResponse(
            {
                "labels": [
                    "Pending Approvals",
                    "Pending Repairs",
                    "Pending Pickups",
                    "In-transit Deliveries",
                ],
                "data": [
                    pending_approvals,
                    pending_repairs,
                    pending_pickups,
                    in_transit_deliveries,
                ],
            }
        )

    # Fallback
    return JsonResponse({"labels": [], "data": []})


