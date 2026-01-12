from django.conf import settings
from django.db import models
from django.utils import timezone

from devices.models import Device


class MarketplaceListing(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="market_listing")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.device.title} - {self.price}"

    @property
    def is_certified(self) -> bool:
        return self.device.status in ["certified", "listed", "allocated"]
    
    @property
    def is_sold(self) -> bool:
        """Check if device has been sold (has an order that's not cancelled)"""
        return self.orders.exclude(status="cancelled").exists()
    
    @property
    def latest_order(self):
        """Get the latest non-cancelled order for this listing"""
        return self.orders.exclude(status="cancelled").order_by("-created_at").first()


class Order(models.Model):
    STATUS_CHOICES = [
        ("placed", "Placed"),
        ("confirmed", "Confirmed"),
        ("in_transit", "In Transit"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]
    listing = models.ForeignKey(MarketplaceListing, on_delete=models.CASCADE, related_name="orders")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="placed")
    shipping_address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} for {self.listing.device.title}"

    def advance_status(self, new_status: str):
        valid = [choice[0] for choice in self.STATUS_CHOICES]
        if new_status not in valid:
            raise ValueError("Invalid order status")
        self.status = new_status
        self.save(update_fields=["status", "updated_at"])
        OrderStatusHistory.objects.create(order=self, status=new_status, note="Status updated")


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20, choices=Order.STATUS_CHOICES)
    note = models.CharField(max_length=255, blank=True)
    changed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["changed_at"]

    def __str__(self):
        return f"{self.order_id}: {self.status}"

