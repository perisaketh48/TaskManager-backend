import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from twilio.rest import Client

@csrf_exempt
def send_whatsapp_message(request):
    if request.method != 'POST':
        return JsonResponse({"error": "Invalid request method"}, status=400)

    try:
        # Parse the request body
        data = json.loads(request.body)

        name = data.get("name")
        email = data.get("email")
        phone_number = data.get("phone_number")
        user_message = data.get("message")

        # Check if all required fields are present
        if not all([name, email, phone_number, user_message]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Format the WhatsApp message
        message_body = (
            f"📩 New Portfolio Contact!\n\n"
            f"👤 Name: {name}\n"
            f"📧 Email: {email}\n"
            f"📱 Phone: {phone_number}\n"
            f"💬 Message: {user_message}"
        )

        # Fetch Twilio credentials from environment
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

        if not account_sid or not auth_token:
            return JsonResponse({
                "error": "Twilio credentials not found. Check environment variables."
            }, status=500)

        # Create Twilio client and send the message
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            from_='whatsapp:+14155238886',  # Twilio sandbox sender number
            body=message_body,
            to='whatsapp:+919390795502'     # Your verified WhatsApp number
        )

        # Return success response
        return JsonResponse({
            "status": "success",
            "message_sid": message.sid
        })

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)

    except Exception as e:
        # Catch-all error handler with logging
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)
