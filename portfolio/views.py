from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def sendmail(request):
    if request.method == 'POST':  # Fix: POST must be uppercase
        data = json.loads(request.body)
        return JsonResponse(data)  # JsonResponse for Django
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
