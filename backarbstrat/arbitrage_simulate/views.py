from django.shortcuts import render
from django.http import JsonResponse
import json
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.permissions import IsAuthenticated
from arbitrage_simulate.serializer import TradeSerializer
from arbitrage_simulate.serializer import CloseTradeSerializer
from cointegration_arbitrage.serializer import CointegratedPairsSerializer
from cointegration_arbitrage.models import Cointegrated_Pairs
from .models import CloseTrade, Trade
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated


def csrf(request):
    return JsonResponse({'csrfToken': get_token(request)})


@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simulateTrades(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Cargar los datos JSON enviados desde React
            data = json.loads(request.body)

            # Extraer los valores de los precios y las cantidades
            idPair = data.get('idPair')
            direction = data.get('direction')
            coin1 = data.get('coin1')
            coin2 = data.get('coin2')
            price1 = data.get('price1')
            price2 = data.get('price2')
            amount1 = data.get('amount1')
            amount2 = data.get('amount2')
            zscore = data.get('zscore')
            spread = data.get('spread'),
            hedgeRatio = data.get('hedgeRatio')

            cointegrated_pair = Cointegrated_Pairs.objects.get(id=idPair)
            print(cointegrated_pair)
            trade = Trade(
                user=request.user,  # Asigna el usuario autenticado al trade
                idPair=cointegrated_pair,
                coin1=coin1,
                coin2=coin2,
                direction=direction,
                price1=price1,
                price2=price2,
                amount1=amount1,
                amount2=amount2,
                zScore=zscore,
                spread=spread[0],
                hedgeRatio=hedgeRatio
            )
            try:
                trade.save()
            except Exception as e:
                response_data = {
                    'error': f'Error al guardar el trade en la base de datos: {e}'}
                return JsonResponse(response_data, status=500, safe=False)

            # Enviar una respuesta JSON de confirmación
            response_data = {
                'message': 'Trades simulados recibidos y procesados.',
                "coin1": coin1,
                "coin2": coin2,
                'direction': direction,
                'price1': price1,
                'price2': price2,
                'amount1': amount1,
                'amount2': amount2,
                'zScore': zscore,
                'spread': spread[0],
                'hedgeRatio': hedgeRatio
            }
            return JsonResponse(response_data, status=200, safe=False)
        else:
            response_data = {'error': 'User No Authenticated'}
            return JsonResponse(response_data, status=405)
    else:
        response_data = {'error': 'Método no permitido'}
        return JsonResponse(response_data, status=405)


@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getAllTrades(request):
    if request.user.is_authenticated:
        user = request.user
        querysetTrade = Trade.objects.filter(user=user)

        serializedTrades_data = TradeSerializer(querysetTrade, many=True).data
        all_pairs = []
        for trade_data in serializedTrades_data:
            querysetPair = Cointegrated_Pairs.objects.filter(
                id=trade_data['idPair'])
            pairData = CointegratedPairsSerializer(
                querysetPair, many=True).data
            for pair in pairData:
                if trade_data['direction'] == "long":
                    print("LONGS")

                    profit1 = float(trade_data['amount1']) * \
                        ((float(pair['last_price_1']) /
                         float(trade_data['price1'])) - 1)
                    profit2 = float(trade_data['amount2']) * (1 -
                                                              (float(pair['last_price_2']) / float(trade_data['price2'])))


                    # Obtener el z-score de pair
                    z_scores = pair.get('z_score')

                    # Obtener el último z-score
                    latest_z_score = z_scores[-1] if z_scores else None

                    # Actualizar el campo zScore en trade_data
                    trade_data['zScore'] = round(latest_z_score, 2)

                    # print(trade_data['coin1'])
                    # print(pair['last_price_1'])
                    # print(round(profit1, 2))
                    # print(trade_data['coin2'])
                    # print(pair['last_price_2'])
                    # print(round(profit2, 2))

                elif trade_data['direction'] == "short":
                    print("SHORTS")

                    profit1 = float(
                        trade_data['amount1']) * (1 - (float(pair['last_price_1']) / float(trade_data['price1'])))
                    profit2 = float(trade_data['amount2']) * ((float(pair['last_price_2']) /
                                                               float(trade_data['price2'])) - 1)

                    # Obtener el z-score de pair
                    z_scores = pair.get('z_score')

                    # Obtener el último z-score
                    latest_z_score = z_scores[-1] if z_scores else None

                    # Actualizar el campo zScore en trade_data
                    trade_data['zScore'] = round(latest_z_score, 2)


                    # print(trade_data['coin1'])
                    # print(pair['last_price_1'])
                    # print(round(profit1, 2))
                    # print(trade_data['coin2'])
                    # print(pair['last_price_2'])
                    # print(round(profit2, 2))

                trade_data['profit1'] = round(profit1, 2)
                trade_data['profit2'] = round(profit2, 2)

        return JsonResponse(serializedTrades_data, safe=False)
    else:
        return JsonResponse({'error': 'User not authenticated'}, status=401)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def saveCloseTrade(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            data = json.loads(request.body)

            # Aquí asumimos que recibes todos los campos necesarios para el modelo CloseTrade
            # Asegúrate de que estos nombres de campo correspondan a los que estás enviando desde el frontend
            coin1 = data.get('coin1')
            amount1 = data.get('amount1')
            price1 = data.get('price1')
            profit1 = data.get('profit1')
            coin2 = data.get('coin2')
            amount2 = data.get('amount2')
            price2 = data.get('price2')
            profit2 = data.get('profit2')

            try:
                close_trade = CloseTrade.objects.create(
                    user=request.user,
                    coin1=coin1,
                    amount1=amount1,
                    price1=price1,
                    profit1=profit1,
                    coin2=coin2,
                    amount2=amount2,
                    price2=price2,
                    profit2=profit2
                )
                close_trade.save()

                response_data = {
                    'message': f'Trade cerrado y guardado correctamente'}
                return JsonResponse(response_data, status=200)

            except Exception as e:
                response_data = {
                    'error': f'Error al guardar el trade cerrado en la base de datos: {e}'}
                return JsonResponse(response_data, status=500)
        else:
            response_data = {'error': 'Usuario no autenticado'}
            return JsonResponse(response_data, status=401)
    else:
        response_data = {'error': 'Método no permitido'}
        return JsonResponse(response_data, status=405)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def closeTrade(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            # Cargar los datos JSON enviados desde React
            data = json.loads(request.body)

            # Extraer los valores de los precios y las cantidades
            idTrade = data.get('id')

            trade = Trade.objects.get(id=idTrade)
            print(trade)
            try:
                trade.delete()
                response_data = {
                    'success': 'El trade ha sido borrado exitosamente'
                }
            except Exception as e:
                response_data = {
                    'error': f'Error al borrar el trade en la base de datos: {e}'
                }
                return JsonResponse(response_data, status=500, safe=False)

            # Enviar una respuesta JSON de confirmación
            return JsonResponse(response_data, status=200, safe=False)
        else:
            response_data = {'error': 'User No Authenticated'}
            return JsonResponse(response_data, status=405)
    else:
        response_data = {'error': 'Método no permitido'}
        return JsonResponse(response_data, status=405)
    
@csrf_exempt
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getClosedTradesByUser(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            user = request.user

            trades = CloseTrade.objects.filter(user_id=user)
            trades_data = CloseTradeSerializer(trades, many=True).data
            trades_json = json.dumps(trades_data)

            return JsonResponse(trades_data, status=200, safe=False)
        else:
            response_data = {'error': 'User not authenticated'}
            return JsonResponse(response_data, status=401)
    else:
        response_data = {'error': 'Method not allowed'}
        return JsonResponse(response_data, status=405)