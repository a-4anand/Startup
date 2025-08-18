# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .utils import to_e164, create_otp, verify_otp, send_whatsapp_template_otp
from .models import Profile, Subscription
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

VERIFY_TOKEN = "supersecretverifytoken"

def send_otp_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone")
        try:
            phone_e164 = to_e164(phone, default_region="IN")   # change default if needed
            code = create_otp(phone_e164)
            send_whatsapp_template_otp(phone_e164, code, settings.OTP_EXP_MINUTES)
            messages.success(request, "OTP sent on WhatsApp.")
            request.session["otp_phone"] = phone_e164
            return redirect("verify_otp")
        except Exception as e:
            messages.error(request, str(e))
    return render(request, "accounts/send_otp.html")

def verify_otp_view(request):
    phone_e164 = request.session.get("otp_phone")
    if not phone_e164:
        return redirect("send_otp")
    if request.method == "POST":
        code = request.POST.get("code", "").strip()
        if verify_otp(phone_e164, code):
            # login or create
            user = User.objects.filter(profile__phone_e164=phone_e164).first()
            if not user:
                base_username = phone_e164.replace("+", "")
                username = base_username
                i = 1
                while User.objects.filter(username=username).exists():
                    i += 1
                    username = f"{base_username}_{i}"
                user = User.objects.create_user(username=username, password=User.objects.make_random_password())
                user.profile.phone_e164 = phone_e164
                user.profile.is_phone_verified = True
                user.profile.save()
            login(request, user)
            messages.success(request, "You are now logged in.")
            return redirect(request.GET.get("next") or "index")
        else:
            messages.error(request, "Invalid or expired OTP.")
    return render(request, "accounts/verify_otp.html", {"phone": phone_e164})

# Webhook for verification + events
@csrf_exempt
def whatsapp_webhook(request):
    if request.method == "GET":
        mode = request.GET.get("hub.mode")
        token = request.GET.get("hub.verify_token")
        challenge = request.GET.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return HttpResponse(challenge)  # ✅ Meta will succeed here
        else:
            return HttpResponse("Error: Invalid token", status=403)

    elif request.method == "POST":
        # Handle incoming messages from WhatsApp/Facebook
        print(request.body)
        return HttpResponse("EVENT_RECEIVED", status=200)
