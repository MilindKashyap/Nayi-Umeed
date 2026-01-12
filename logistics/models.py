from django.conf import settings
from django.db import models
from django.utils import timezone

from devices.models import Device
from marketplace.models import Order


class TaskType(models.TextChoices):
    PICKUP = "pickup", "Pickup"
    DELIVERY = "delivery", "Delivery"


class TaskStatus(models.TextChoices):
    ASSIGNED = "assigned", "Assigned"
    PICKED_UP = "picked_up", "Picked Up"
    DELIVERED = "delivered", "Delivered"
    CANCELLED = "cancelled", "Cancelled"


def proof_upload_path(instance: "LogisticsTask", filename: str) -> str:
    task_type = instance.task_type
    task_id = instance.id or "temp"
    return f"logistics_proofs/{task_type}/{task_id}/{filename}"


class LogisticsTask(models.Model):
    task_type = models.CharField(max_length=10, choices=TaskType.choices)
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.ASSIGNED)
    
    # Links - either device (pickup) or order (delivery)
    device = models.ForeignKey(
        Device, on_delete=models.CASCADE, related_name="logistics_tasks", null=True, blank=True
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="logistics_tasks", null=True, blank=True
    )
    
    # Address information
    pickup_address = models.CharField(max_length=255, blank=True)
    delivery_address = models.CharField(max_length=255, blank=True)
    
    # Assigned logistics partner/staff
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="logistics_tasks",
    )
    
    # Proof of pickup/delivery
    pickup_proof = models.ImageField(upload_to=proof_upload_path, null=True, blank=True)
    delivery_proof = models.ImageField(upload_to=proof_upload_path, null=True, blank=True)
    
    # Geo-tracking placeholders (backend-ready for GPS integration)
    pickup_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    pickup_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    delivery_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Timestamps
    assigned_at = models.DateTimeField(auto_now_add=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ["-assigned_at"]
    
    def __str__(self) -> str:
        if self.device:
            return f"{self.get_task_type_display()} - {self.device.listing_id}"
        if self.order:
            return f"{self.get_task_type_display()} - Order #{self.order.id}"
        return f"{self.get_task_type_display()} - Task #{self.id}"
    
    @property
    def display_address(self) -> str:
        """Returns the relevant address based on task type"""
        if self.task_type == TaskType.PICKUP:
            return self.pickup_address or (self.device.donor.get_full_name() if self.device else "")
        return self.delivery_address or (self.order.shipping_address if self.order else "")
    
    def mark_picked_up(self, proof_image=None, latitude=None, longitude=None, notes=""):
        """Mark task as picked up with proof and optional geo-coordinates"""
        if self.status != TaskStatus.ASSIGNED:
            raise ValueError("Task must be in Assigned status to mark as picked up")
        self.status = TaskStatus.PICKED_UP
        self.picked_up_at = timezone.now()
        if proof_image:
            self.pickup_proof = proof_image
        if latitude is not None:
            self.pickup_latitude = latitude
        if longitude is not None:
            self.pickup_longitude = longitude
        if notes:
            self.notes = notes
        self.save()
        TaskStatusHistory.objects.create(
            task=self, status=TaskStatus.PICKED_UP, note=notes or "Picked up"
        )
        # Update device status if pickup task
        if self.device and self.device.status == "submitted":
            try:
                self.device.transition_to("picked_up", note="Picked up by logistics")
            except ValueError:
                pass
    
    def mark_delivered(self, proof_image=None, latitude=None, longitude=None, notes=""):
        """Mark task as delivered with proof and optional geo-coordinates"""
        if self.status != TaskStatus.PICKED_UP:
            raise ValueError("Task must be in Picked Up status to mark as delivered")
        self.status = TaskStatus.DELIVERED
        self.delivered_at = timezone.now()
        if proof_image:
            self.delivery_proof = proof_image
        if latitude is not None:
            self.delivery_latitude = latitude
        if longitude is not None:
            self.delivery_longitude = longitude
        if notes:
            self.notes = notes
        self.save()
        TaskStatusHistory.objects.create(
            task=self, status=TaskStatus.DELIVERED, note=notes or "Delivered"
        )
        # Update order status if delivery task
        if self.order:
            try:
                self.order.advance_status("delivered")
            except ValueError:
                pass


class TaskStatusHistory(models.Model):
    task = models.ForeignKey(LogisticsTask, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20, choices=TaskStatus.choices)
    note = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ["changed_at"]
    
    def __str__(self):
        return f"Task #{self.task.id}: {self.status}"

