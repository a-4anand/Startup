# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone_e164 = models.CharField(max_length=20, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    whatsapp_opt_in = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} ({self.phone_e164})"

class Subscription(models.Model):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELED = "canceled"
    STATUS_CHOICES = [(ACTIVE,"Active"),(EXPIRED,"Expired"),(CANCELED,"Canceled")]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=EXPIRED)
    plan = models.CharField(max_length=50, default="starter")
    provider = models.CharField(max_length=50, blank=True)  # stripe/razorpay/etc
    external_id = models.CharField(max_length=100, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def has_active(self):
        from django.utils import timezone
        return self.status == self.ACTIVE and (self.expires_at and self.expires_at > timezone.now())
