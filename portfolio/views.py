import os 
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
import re

@csrf_exempt
def send_whatsapp_message(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        data = json.loads(request.body)

        name = data.get("name")
        email = data.get("email")
        phone_number = data.get("phone_number")
        user_message = data.get("message")

        if not all([name, email, phone_number, user_message]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Validate & format phone number to E.164 (Twilio requirement)
        phone_number = str(phone_number).strip()
        if not phone_number.startswith("+"):
            # Check if it looks like a valid 10-digit Indian number
            if re.fullmatch(r"\d{10}", phone_number):
                phone_number = f"+91{phone_number}"  # prepend Indian country code
            else:
                return JsonResponse({
                    "error": "Invalid phone number format. Please include country code (e.g., +919390795502)."
                }, status=400)

        message_body = (
            f"📩 New Portfolio Contact!\n\n"
            f"👤 Name: {name}\n"
            f"📧 Email: {email}\n"
            f"📱 Phone: {phone_number}\n"
            f"💬 Message: {user_message}"
        )

        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

        if not account_sid or not auth_token:
            return JsonResponse({
                "error": "Twilio credentials not found. Check environment variables."
            }, status=500)

        client = Client(account_sid, auth_token)

        # Send WhatsApp message
        whatsapp_message = client.messages.create(
            from_='whatsapp:+14155238886',  # Twilio sandbox WhatsApp number
            body=message_body,
            to=f'whatsapp:{phone_number}'  # recipient WhatsApp number
        )

        # Send SMS message
        sms_message = client.messages.create(
            from_='+12566998810',  # Your Twilio SMS-enabled phone number in E.164
            body=message_body,
            to=phone_number
        )

        return JsonResponse({
            "status": "success",
            "whatsapp_message_sid": whatsapp_message.sid,
            "sms_message_sid": sms_message.sid
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
