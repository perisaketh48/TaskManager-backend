from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from django.conf import settings
import os
import json

@csrf_exempt
def send_whatsapp_message(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Extract user-submitted contact details
            name = data.get("name")
            email = data.get("email")
            phone_number = data.get("phone_number")
            user_message = data.get("message")

            if not name or not email or not phone_number or not user_message:
                return JsonResponse({"error": "Missing required fields"}, status=400)

            # Construct the message to be sent to yourself
            message_body = (
                f"📩 New Portfolio Contact!\n\n"
                f"👤 Name: {name}\n"
                f"📧 Email: {email}\n"
                f"📱 Phone: {phone_number}\n"
                f"💬 Message: {user_message}"
            )

            # Send WhatsApp message to your number (registered in Twilio)
            account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
            auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                from_='whatsapp:+14155238886',  # Example: 'whatsapp:+14155238886'
                body=message_body,
                to='whatsapp:+919390795502'  # Your own number with country code
            )

            return JsonResponse({"status": "success", "message_sid": message.sid})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)
