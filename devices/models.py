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
        """Get Cloudinary URL - always returns Cloudinary URL"""
        cloud_name = "duo3tqnyj"  # Hardcoded to ensure it works
        
        try:
            # Get the stored value from database
            stored_value = self.image.name if self.image else None
            
            if not stored_value:
                return ""
            
            stored_value = str(stored_value)
            
            # If it's already a full Cloudinary URL, return it
            if "cloudinary.com" in stored_value or stored_value.startswith("http"):
                return stored_value
            
            # Clean up duplicate paths (fix for old uploads)
            if "nayi_umeed/device_images/nayi_umeed/device_images" in stored_value:
                stored_value = stored_value.replace("nayi_umeed/device_images/nayi_umeed/device_images/", "device_images/")
            
            # If it starts with /media/, extract the path
            if stored_value.startswith("/media/"):
                stored_value = stored_value.replace("/media/", "")
            
            # Remove file extension if present (Cloudinary public_id shouldn't have extension)
            if '.' in stored_value:
                # Keep the path structure but remove extension
                parts = stored_value.rsplit('.', 1)
                if len(parts) == 2 and parts[1] in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                    stored_value = parts[0]
            
            # Try to get actual Cloudinary URL with version
            try:
                import cloudinary
                import cloudinary.api
                from django.conf import settings
                
                cloudinary.config(
                    cloud_name=cloud_name,
                    api_key=getattr(settings, "CLOUDINARY_API_KEY", "436353534932931"),
                    api_secret=getattr(settings, "CLOUDINARY_API_SECRET", "bcuxK2hTL-UDQFyzAxnKBKbY3o8"),
                    secure=True
                )
                
                # Try to get resource info to get the actual URL
                resource = cloudinary.api.resource(stored_value)
                if resource and 'secure_url' in resource:
                    return resource['secure_url']
            except:
                # If we can't fetch from API, use versionless URL (Cloudinary supports this)
                # Versionless URLs work if the image was uploaded with overwrite or has a unique public_id
                pass
            
            # Fallback: Use versionless URL format (Cloudinary will serve the latest version)
            return f"https://res.cloudinary.com/{cloud_name}/image/upload/{stored_value}"
            
        except Exception as e:
            # Fallback: try to use image.url and convert if needed
            try:
                if self.image:
                    url = self.image.url
                    if "cloudinary.com" in url:
                        return url
                    if url.startswith("/media/"):
                        path = url.replace("/media/", "")
                        # Clean duplicate paths
                        if "nayi_umeed/device_images/nayi_umeed/device_images" in path:
                            path = path.replace("nayi_umeed/device_images/nayi_umeed/device_images/", "device_images/")
                        return f"https://res.cloudinary.com/{cloud_name}/image/upload/{path}"
            except:
                pass
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

