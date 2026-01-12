from django.conf import settings
from django.db import models
from django.utils import timezone

from devices.models import Device


class RepairStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    IN_PROGRESS = "in_progress", "In Progress"
    AWAITING_PARTS = "awaiting_parts", "Awaiting Parts"
    COMPLETED = "completed", "Completed"
    CERTIFIED = "certified", "Certified"
    REJECTED = "rejected", "Rejected"


class RepairAssignment(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="repair_assignments")
    repair_partner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="repair_assignments",
        help_text="User with RepairPartner role",
    )
    status = models.CharField(max_length=20, choices=RepairStatus.choices, default=RepairStatus.PENDING)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    report_file = models.FileField(upload_to="repair_reports/", null=True, blank=True)
    report_notes = models.TextField(blank=True)
    is_certified = models.BooleanField(default=False)
    certified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Repair for {self.device.listing_id} by {self.repair_partner}"

    def mark_certified(self):
        from devices.models import DeviceStatusFlow  # local import to avoid circulars

        self.is_certified = True
        self.certified_at = timezone.now()
        self.status = RepairStatus.CERTIFIED
        self.save(update_fields=["is_certified", "certified_at", "status", "updated_at"])

        # Attempt to move device to certified in its lifecycle if possible
        try:
            if self.device.status in {"under_repair", "under_inspection"} and "certified" in DeviceStatusFlow:
                self.device.transition_to("certified", note="Certified by repair partner")
        except ValueError:
            # If transition is invalid, we just keep repair certification
            pass

