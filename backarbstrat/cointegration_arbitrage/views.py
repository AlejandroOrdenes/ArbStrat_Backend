from .models import Cointegrated_Pairs
from .serializer import CointegratedPairsSerializer
from .dydx.connectionDydx import connect_dydx
from django.http import HttpResponse, JsonResponse
from .dydx.publicConnect import construct_market, construct_market_prices, convert_df_to_chart_data
from .cointegration.calcCointegration import store_cointegration_result




# Create your views here.
def getCryptos(request):
    client = connect_dydx()
    markets = client.public.get_markets()

    if markets:
        return JsonResponse(markets.data, safe=False)
    else:
        return JsonResponse({"error": "Failed to fetch markets data."})


def cointegration_view(request):
    try:
        client = connect_dydx()
    except Exception as err:
        print(err)
        print("Error connecting to client: ", err)
        

    # Find Cointegrated Pairs
    # Construct market Prices
    try:
        print("Fetching market pricess, please allow 5 mins...")
        df_market_prices = construct_market_prices(client)
    except Exception as err:
        print("Error constructing market prices: ", err)
        

        # Store Cointegrated Pairs
    try:
        print("Storing cointegrated pairs...")
        stores_result = store_cointegration_result(df_market_prices)
        if not stores_result:
            print("Error saving cointegrated pairs")
            
    except Exception as err:
        print("Error saving cointegrated pairs: ", err)
        

    print('Cointegration se esta ejecutando!!')
    return JsonResponse(stores_result, safe=False)


def getAllCointegratedPairs(request):
    try:
        queryset = Cointegrated_Pairs.objects.all()
        print(queryset)
        
        serialized_data = CointegratedPairsSerializer(queryset, many=True).data
        return JsonResponse(serialized_data, safe=False)
    except Exception as er:
        print(er)
        print("Error to get DB: ", er)
        

def getCointegratedPairById(request, idPair):
    try:
        queryset = Cointegrated_Pairs.objects.filter(id=idPair)
        print(queryset)
        
        serialized_data = CointegratedPairsSerializer(queryset, many=True).data
        return JsonResponse(serialized_data, safe=False)
    except Exception as er:
        print(er)
        print("Error to get DB: ", er)
        


def getCryptoPrices(request):
    try:
        client = connect_dydx()
    except Exception as err:
        print(err)
        print("Error connecting to client: ", err)
        

    data = convert_df_to_chart_data(construct_market_prices(client))
    return JsonResponse(data, safe=False)

def getPrice(request, market):
    try:
        client = connect_dydx()
    except Exception as err:
        print(err)
        print("Error connecting to client: ", err)
    
    try:
        data = convert_df_to_chart_data(construct_market(client, market))
        return JsonResponse([data], safe=False)
    except Exception as e:
        # Aquí puedes manejar el error, por ejemplo devolviendo un error HTTP
        return HttpResponse(status=400, content=str(e))
        

def getCurrentPrices(request, idPair):
    if idPair:
        queryset = Cointegrated_Pairs.objects.filter(id=idPair)
        serialized_data = CointegratedPairsSerializer(queryset, many=True).data
        
        if serialized_data:  # Verifica si la lista no está vacía
            obj = serialized_data[0]  # Accede al primer objeto en la lista
            price1 = obj['last_price_1']
            price2 = obj['last_price_2']
            return JsonResponse({"price1": price1, "price2": price2}, safe=False)
        else:
            return JsonResponse({'error': 'No data found for the given idPair'}, status=404)

    else:
        return JsonResponse({'error': 'Error to get Prices'}, status=401)


    