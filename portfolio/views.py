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
import os
import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from django.core.mail import send_mail


@csrf_exempt
def send_whatsapp_message(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)

        name = data.get("name")
        email = data.get("email")
        phone_number = data.get("phone_number")
        user_message = data.get("message")

        if not all([name, email, phone_number, user_message]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        message_body = (
            f"📩 New Portfolio Contact!\n\n"
            f"👤 Name: {name}\n"
            f"📧 Email: {email}\n"
            f"📱 Phone: {phone_number}\n"
            f"💬 Message: {user_message}"
        )

        # EMAIL ALWAYS RUNS — EVEN IF TWILIO FAILS
        email_status = "sent"
        try:
            send_mail(
                subject="📩 New Portfolio Message",
                message=message_body,
                from_email=os.getenv("EMAIL_HOST_USER"),
                recipient_list=[os.getenv("EMAIL_HOST_USER")],
                fail_silently=False,
            )
        except Exception as e:
            email_status = f"failed: {str(e)}"

        # TWILIO MAY FAIL — BUT WILL NOT BREAK API
        twilio_status = "skipped"
        try:
            client = Client(
                os.getenv("TWILIO_ACCOUNT_SID"),
                os.getenv("TWILIO_AUTH_TOKEN")
            )

            whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
            my_whatsapp = os.getenv("MY_WHATSAPP")

            twilio_message = client.messages.create(
                from_=f"whatsapp:{whatsapp}",
                to=f"whatsapp:{my_whatsapp}",
                body=message_body,
            )
            twilio_status = "sent"

        except Exception as twilio_error:
            twilio_status = f"failed: {str(twilio_error)}"

        return JsonResponse({
            "status": "success",
            "email": email_status,
            "twilio": twilio_status
        })

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
