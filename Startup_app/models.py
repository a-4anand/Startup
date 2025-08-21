from django.db import models
from django.contrib.auth.models import User
class Contact(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"


class Subscription(models.Model):
    PLAN_CHOICES = (
        ('Free','free'),
        ('Purchase','purchase')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES,default='Free')
    razorpay_order_id = models.CharField(max_length=255,unique=True,null=True,blank=True)
    razorpay_payment_id = models.CharField(max_length=255,unique=True,null=True,blank=True)
    razorpay_signature= models.CharField(max_length=255,null=True,blank=True)
    intended_plan = models.CharField(max_length=10,choices=PLAN_CHOICES,blank=True,null=True)
    intended_razorpay_order_id = models.CharField(max_length=100,unique=True,null=True,blank=True)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    download_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.plan}"



