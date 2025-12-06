# import os 
# import json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from twilio.rest import Client
# import re


# @csrf_exempt
# def send_whatsapp_message(request):
#     if request.method != 'POST':
#         return JsonResponse({"error": "Invalid request method"}, status=400)

#     try:
#         data = json.loads(request.body)

#         name = data.get("name")
#         email = data.get("email")
#         phone_number = data.get("phone_number")
#         user_message = data.get("message")

#         if not all([name, email, phone_number, user_message]):
#             return JsonResponse({"error": "Missing required fields"}, status=400)

#         # Validate & format phone number for Twilio
#         phone_number = str(phone_number).strip()
#         if not phone_number.startswith("+"):
#             if re.fullmatch(r"\d{10}", phone_number):
#                 phone_number = f"+91{phone_number}"
#             else:
#                 return JsonResponse({
#                     "error": "Invalid phone number format. Please include country code (e.g., +919390795502)."
#                 }, status=400)

#         message_body = (
#             f"📩 New Portfolio Contact!\n\n"
#             f"👤 Name: {name}\n"
#             f"📧 Email: {email}\n"
#             f"📱 Phone: {phone_number}\n"
#             f"💬 Message: {user_message}"
#         )

#         # --------------------------
#         # SEND EMAIL (FREE via Gmail)
#         # --------------------------
#         email_subject = "📩 New Contact Form Submission from Portfolio"
#         email_message = (
#             f"New message from your portfolio:\n\n"
#             f"Name: {name}\n"
#             f"Email: {email}\n"
#             f"Phone: {phone_number}\n"
#             f"Message:\n{user_message}\n\n"
#         )

#         try:
#             send_mail(
#                 subject=email_subject,
#                 message=email_message,
#                 from_email=os.environ.get("EMAIL_HOST_USER"),
#                 recipient_list=["perisaketh545@gmail.com"],
#                 fail_silently=False,
#             )
#             email_status = "Email sent"
#         except Exception as e:
#             email_status = f"Email error: {str(e)}"

#         # --------------------------
#         # SEND WHATSAPP + SMS (TWILIO)
#         # --------------------------
#         account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
#         auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

#         if not account_sid or not auth_token:
#             return JsonResponse({
#                 "error": "Twilio credentials not found. Check environment variables."
#             }, status=500)

#         client = Client(account_sid, auth_token)

#         whatsapp_message = client.messages.create(
#             from_='whatsapp:+14155238886',
#             body=message_body,
#             to=f'whatsapp:{phone_number}'
#         )

#         sms_message = client.messages.create(
#             from_='+12566998810',
#             body=message_body,
#             to=phone_number
#         )

#         return JsonResponse({
#             "status": "success",
#             "whatsapp_message_sid": whatsapp_message.sid,
#             "sms_message_sid": sms_message.sid,
#             "email_status": email_status
#         })

#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON format"}, status=400)

#     except Exception as e:
#         return JsonResponse({
#             "status": "error",
#             "message": str(e)
#         }, status=500)

# import os, json
# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt

# # -------- EMAIL (SendGrid API) -------- #
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail


# def send_email(subject, body):
#     try:
#         message = Mail(
#             from_email=os.getenv("EMAIL_FROM"),
#             to_emails=os.getenv("EMAIL_FROM"),
#             subject=subject,
#             plain_text_content=body,
#         )

#         sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
#         sg.send(message)

#         print("✅ Email sent successfully")
#     except Exception as e:
#         print("❌ SendGrid Email Error:", e)


# # -------- WHATSAPP (Twilio API) -------- #
# from twilio.rest import Client


# def send_whatsapp(body):
#     try:
#         client = Client(
#             os.getenv("TWILIO_ACCOUNT_SID"),
#             os.getenv("TWILIO_AUTH_TOKEN")
#         )

#         msg = client.messages.create(
#             from_=f"whatsapp:{os.getenv('TWILIO_WHATSAPP_NUMBER')}",
#             to=f"whatsapp:{os.getenv('MY_WHATSAPP')}",
#             body=body,
#         )

#         print("✅ WhatsApp message queued:", msg.sid)
#     except Exception as e:
#         print("❌ Twilio WhatsApp Error:", e)


# # -------- MAIN VIEW -------- #
# @csrf_exempt
# def send_whatsapp_message(request):
#     if request.method != "POST":
#         return JsonResponse({"error": "Invalid request method"}, status=400)

#     try:
#         data = json.loads(request.body)

#         name = data.get("name")
#         email = data.get("email")
#         phone_number = data.get("phone_number")
#         user_message = data.get("message")

#         if not all([name, email, phone_number, user_message]):
#             return JsonResponse({"error": "Missing required fields"}, status=400)

#         message_body = (
#             f"📩 New Portfolio Contact!\n\n"
#             f"👤 Name: {name}\n"
#             f"📧 Email: {email}\n"
#             f"📱 Phone: {phone_number}\n"
#             f"💬 Message: {user_message}"
#         )

#         # 🔥 Execute synchronously — SAFE on Render
#         send_email("📩 New Portfolio Message", message_body)
#         send_whatsapp(message_body)

#         return JsonResponse({
#             "status": "success",
#             "message": "Message sent successfully.",
#         })

#     except Exception as e:
#         print("❌ Error in main handler:", e)
#         return JsonResponse({"status": "error", "message": str(e)}, status=500)





import os
import json
import csv
from datetime import timedelta

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from .models import ContactMessage


# -----------------------------
# Helper: Admin Protection
# -----------------------------
def admin_required(view_func):
    return user_passes_test(lambda u: u.is_staff)(view_func)


# -----------------------------
# EMAIL: Send notification to YOU
# -----------------------------
def send_email(subject, body):
    try:
        message = Mail(
            from_email=os.getenv("EMAIL_FROM"),
            to_emails=os.getenv("EMAIL_FROM"),
            subject=subject,
            plain_text_content=body,
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)

        print("✅ Email sent to admin")
    except Exception as e:
        print("❌ SendGrid Email Error:", e)


# -----------------------------
# EMAIL: Auto-reply to user
# -----------------------------
def send_auto_reply(user_email, user_name):
    try:
        message = Mail(
            from_email=os.getenv("EMAIL_FROM"),
            to_emails=user_email,
            subject="Thank you for contacting me!",
            plain_text_content=(
                f"Hi {user_name},\n\n"
                "Thank you for reaching out! I have received your message and "
                "will get back to you shortly.\n\n"
                "Regards,\nSaketh"
            ),
        )

        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        sg.send(message)

        print("📩 Auto-reply sent to user")
    except Exception as e:
        print("❌ Auto-reply error:", e)


# -----------------------------
# Spam Protection (Rate Limiting)
# -----------------------------
def is_spamming(email):
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    return ContactMessage.objects.filter(email=email, created_at__gte=one_minute_ago).exists()


# -----------------------------
# MAIN CONTACT FORM API
# -----------------------------
@csrf_exempt
def send_contact_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)

        name = data.get("name")
        email = data.get("email")
        phone = data.get("phone_number")
        message_text = data.get("message")

        # Required fields check
        if not all([name, email, phone, message_text]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Rate limiting
        if is_spamming(email):
            return JsonResponse({"error": "You are sending messages too fast."}, status=429)

        # Basic validation
        if len(name) < 2:
            return JsonResponse({"error": "Name too short"}, status=400)

        if "@" not in email:
            return JsonResponse({"error": "Invalid email address"}, status=400)

        if not phone.isdigit() or len(phone) < 10:
            return JsonResponse({"error": "Invalid phone number"}, status=400)

        if len(message_text.strip()) < 5:
            return JsonResponse({"error": "Message too short"}, status=400)

        # Save in database
        msg = ContactMessage.objects.create(
            name=name,
            email=email,
            phone_number=phone,
            message=message_text,
        )

        print("💾 Message saved with ID:", msg.id)

        # Email to Admin
        email_body = (
            f"New contact message:\n\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n"
            f"Message:\n{message_text}\n\n"
            f"Stored in DB with ID: {msg.id}"
        )
        send_email("📩 New Portfolio Message", email_body)

        # Auto reply to user
        send_auto_reply(email, name)

        return JsonResponse({"status": "success", "id": msg.id})

    except Exception as e:
        print("❌ Error:", e)
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


# -----------------------------
# ADMIN: Get All Messages
# -----------------------------
@admin_required
def get_all_messages(request):
    messages = ContactMessage.objects.all().order_by("-created_at")
    data = [
        {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "phone_number": m.phone_number,
            "message": m.message,
            "created_at": m.created_at,
        }
        for m in messages
    ]
    return JsonResponse({"messages": data})


# -----------------------------
# ADMIN: Get Single Message
# -----------------------------
@admin_required
def get_message(request, msg_id):
    try:
        m = ContactMessage.objects.get(id=msg_id)
        data = {
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "phone_number": m.phone_number,
            "message": m.message,
            "created_at": m.created_at,
        }
        return JsonResponse(data)
    except ContactMessage.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)


# -----------------------------
# ADMIN: Delete Message
# -----------------------------
@admin_required
def delete_message(request, msg_id):
    try:
        ContactMessage.objects.get(id=msg_id).delete()
        return JsonResponse({"status": "deleted"})
    except ContactMessage.DoesNotExist:
        return JsonResponse({"error": "Message not found"}, status=404)


# -----------------------------
# ADMIN: Export All Messages to CSV
# -----------------------------
@admin_required
def export_messages_csv(request):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=contact_messages.csv"

    writer = csv.writer(response)
    writer.writerow(["ID", "Name", "Email", "Phone", "Message", "Created At"])

    for m in ContactMessage.objects.all().order_by("-created_at"):
        writer.writerow([m.id, m.name, m.email, m.phone_number, m.message, m.created_at])

    return response
