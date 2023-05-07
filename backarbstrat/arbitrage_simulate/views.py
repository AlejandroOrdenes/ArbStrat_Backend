from django.shortcuts import render
from django.http import JsonResponse
import json
from django.http import JsonResponse
from django.middleware.csrf import get_token


def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})

def simulateTrades(request):
    if request.method == 'POST':
        # Cargar los datos JSON enviados desde React
        data = json.loads(request.body)

        # Extraer los valores de los precios y las cantidades
        direction = data.get('direction')
        price1 = data.get('price1')
        price2 = data.get('price2')
        amount1 = data.get('amount1')
        amount2 = data.get('amount2')
        zscore = data.get('zscore')
        spread = data.get('spread'),
        hedgeRatio = data.get('hedgeRatio')
        # Realizar operaciones con los datos recibidos, por ejemplo, guardar en la base de datos
        # ...
        print()

        # Enviar una respuesta JSON de confirmación
        response_data = {
            'message': 'Trades simulados recibidos y procesados.',
            'direction': direction,
            'price1': price1,
            'price2': price2,
            'amount1': amount1,
            'amount2': amount2,
            'zScore': zscore,
            'spread': spread[0],
            'hedgeRatio': hedgeRatio
        }
        return JsonResponse(response_data, status=200)

    else:
        response_data = {'error': 'Método no permitido'}
        return JsonResponse(response_data, status=405)

def procesingTrades():
    pass