from django.db import models
from django.utils import timezone

from devices.models import Device


class Region(models.Model):
    """Geographic region for impact reporting (e.g., state/district/cluster)."""

    name = models.CharField(max_length=100)
    code = models.CharField(max_length=32, unique=True)
    country = models.CharField(max_length=64, default="India")
    state = models.CharField(max_length=64, blank=True)
    district = models.CharField(max_length=64, blank=True)

    class Meta:
        verbose_name = "Region"
        verbose_name_plural = "Regions"
        ordering = ["country", "state", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.state})" if self.state else self.name


class DeviceImpact(models.Model):
    """
    Per-device impact annotation.
    Can be populated gradually as field data comes in.
    """

    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="impact")
    region = models.ForeignKey(Region, on_delete=models.SET_NULL, null=True, blank=True, related_name="device_impacts")
    beneficiaries = models.PositiveIntegerField(default=0)
    estimated_co2_saved_kg = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Device Impact"
        verbose_name_plural = "Device Impacts"

    def __str__(self) -> str:
        return f"Impact for {self.device.listing_id}"


class SystemBottleneckSnapshot(models.Model):
    """
    Periodic snapshot of system bottlenecks for monitoring.
    These can be created via a cron/management command later.
    """

    captured_at = models.DateTimeField(default=timezone.now, db_index=True)
    pending_approvals = models.PositiveIntegerField(default=0)
    pending_repairs = models.PositiveIntegerField(default=0)
    pending_pickups = models.PositiveIntegerField(default=0)
    in_transit_deliveries = models.PositiveIntegerField(default=0)

    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "System Bottleneck Snapshot"
        verbose_name_plural = "System Bottleneck Snapshots"
        ordering = ["-captured_at"]

    def __str__(self) -> str:
        return f"Bottleneck snapshot at {self.captured_at:%Y-%m-%d %H:%M}"


