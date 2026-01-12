from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models


class Roles(models.TextChoices):
    DONOR = "donor", "Donor"
    BUYER = "buyer", "Buyer"
    BOTH = "both", "Both"
    REPAIR_PARTNER = "repair_partner", "Repair Partner"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    phone_number = models.CharField(
        max_length=15,
        unique=True,
        validators=[RegexValidator(r"^[0-9+ -]{8,15}$", "Enter a valid phone number.")],
    )
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.DONOR,
    )
    otp_verified = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_donor(self) -> bool:
        return self.role in {Roles.DONOR, Roles.BOTH}

    @property
    def is_buyer(self) -> bool:
        return self.role in {Roles.BUYER, Roles.BOTH}

    @property
    def is_admin(self) -> bool:
        return self.role == Roles.ADMIN or self.is_staff


class OTPRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otp_requests")
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"OTP for {self.user} at {self.created_at:%Y-%m-%d %H:%M}"

