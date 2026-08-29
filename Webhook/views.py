from django.shortcuts import render
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import reponses
from django.views.decorators.http import require_POST
import demjson3


@require_POST
@csrf_exempt
def webhook_receiver(request):
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud y decodificarlo
        request_body = request.body.decode('utf-8')

        # Analizar el cuerpo JSON
        try:
            
            payload = json.loads(request_body)
            print(payload)
            transaction_id = payload.get("transactionId")
            if transaction_id == None:
                transaction_id = payload['metaData']['transactionId']

            # Guardar los datos en tu modelo Response
            r = reponses()
            r.data = payload
            r.transaction_id = transaction_id
            r.save()

            return HttpResponse(request_body, status=200)
        except json.JSONDecodeError as e:
            # Manejar errores de JSON si la decodificación falla
            return HttpResponse(f"Error decoding JSON: {e}", status=400)

    return HttpResponse("Invalid method", status=405)