import uuid
from typing import List

from django.conf import settings
from django.db import models
from django.utils import timezone

DeviceStatusFlow: List[str] = [
    "submitted",
    "picked_up",
    "under_inspection",
    "under_repair",
    "certified",
    "listed",
    "allocated",
]


class Device(models.Model):
    CATEGORY_CHOICES = [
        ("oxygen_concentrator", "Oxygen Concentrator"),
        ("ventilator", "Ventilator"),
        ("monitor", "Patient Monitor"),
        ("wheelchair", "Wheelchair"),
        ("other", "Other"),
    ]
    CONDITION_CHOICES = [
        ("new", "New"),
        ("good", "Good"),
        ("needs_repair", "Needs Repair"),
    ]
    STATUS_CHOICES = [(s, s.replace("_", " ").title()) for s in DeviceStatusFlow]
    
    ADMIN_APPROVAL_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("on_hold", "On Hold"),
    ]

    title = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="submitted")
    admin_approval_status = models.CharField(
        max_length=20, choices=ADMIN_APPROVAL_CHOICES, default="pending"
    )
    admin_notes = models.TextField(blank=True, help_text="Admin notes for approval/rejection")
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="devices"
    )
    listing_id = models.CharField(max_length=20, unique=True, editable=False)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.listing_id})"

    def save(self, *args, **kwargs):
        if not self.listing_id:
            self.listing_id = f"DEV-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def transition_to(self, new_status: str, note: str = ""):
        if new_status not in DeviceStatusFlow:
            raise ValueError("Invalid status")
        current_index = DeviceStatusFlow.index(self.status)
        target_index = DeviceStatusFlow.index(new_status)
        if target_index != current_index + 1 and new_status != self.status:
            raise ValueError("Status transition must follow defined order")
        previous_status = self.status
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])
        DeviceStatusHistory.objects.create(
            device=self, from_status=previous_status, to_status=new_status, note=note
        )
        send_status_notification(self, previous_status, new_status)


def device_image_upload(instance: "DeviceImage", filename: str) -> str:
    return f"device_images/{instance.device.listing_id}/{filename}"


class DeviceImage(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=device_image_upload)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.device.listing_id}"
    
    @property
    def get_image_url(self):
        """Get Cloudinary URL - constructs URL directly without API calls"""
        cloud_name = "duo3tqnyj"
        
        try:
            # Get stored value
            stored_value = self.image.name if self.image else None
            if not stored_value:
                return ""
            
            stored_value = str(stored_value)
            
            # If already a full URL, return it
            if "cloudinary.com" in stored_value or stored_value.startswith("http"):
                return stored_value
            
            # Clean duplicate paths
            if "nayi_umeed/device_images/nayi_umeed/device_images" in stored_value:
                stored_value = stored_value.replace("nayi_umeed/device_images/nayi_umeed/device_images/", "device_images/")
            
            # Remove /media/ prefix
            if stored_value.startswith("/media/"):
                stored_value = stored_value.replace("/media/", "")
            
            # Construct Cloudinary URL directly
            # Based on verified uploads, images have these public_ids:
            public_id = stored_value
            
            # Map of known working public_ids to their versions (from verification)
            # Format: public_id -> version number
            known_versions = {
                "device_images/DEV-383B0B02/blood_pressure_monitor": "v1768303887",
                "device_images/DEV-1D28C43D/oxygen_concentrator": "v1768303887",
                "device_images/DEV-6BD3B519/patient_monitor": "v1768303888",
                "device_images/DEV-8C93FAA3/pulse_oximeter": "v1768303889",
                "device_images/DEV-3BD4155A/stethoscope": "v1768303889",
                "device_images/DEV-AC24891B/thermometer": "v1768303890",
                "device_images/DEV-B694C352/ventilator 1": "v1768303891",
                "device_images/DEV-B326E3D2/ventilator2": "v1768303892",
                "device_images/DEV-3C25EA4B/wheelchair": "v1768303892",
            }
            
            # Check if we have a known version
            version = known_versions.get(public_id, "v1")  # Default to v1 if unknown
            
            # Add extension if missing
            if '.' not in public_id.split('/')[-1]:
                public_id = f"{public_id}.jpg"
            
            # Construct versioned URL
            return f"https://res.cloudinary.com/{cloud_name}/image/upload/{version}/{public_id}"
            
        except:
            return ""


class DeviceStatusHistory(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="history")
    from_status = models.CharField(max_length=20, choices=Device.STATUS_CHOICES)
    to_status = models.CharField(max_length=20, choices=Device.STATUS_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["changed_at"]

    def __str__(self):
        return f"{self.device.listing_id}: {self.from_status} -> {self.to_status}"


def send_status_notification(device: Device, old: str, new: str) -> None:
    # Placeholder for email/SMS/Push integration
    print(f"[Notification] {device.listing_id} status changed {old} -> {new}")

