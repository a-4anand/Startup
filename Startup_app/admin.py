# app/admin.py
from django.contrib import admin
from .models import Contact,Subscription

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "phone", "subject", "created_at")
    search_fields = ("first_name", "last_name", "email", "phone", "subject")
    list_filter = ("created_at",)

@admin.register(Subscription)

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "plan","razorpay_order_id","is_paid"]

