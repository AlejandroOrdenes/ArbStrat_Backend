from cointegration_arbitrage.dydx.connectionDydx import connect_dydx
from django.http import JsonResponse
from cointegration_arbitrage.dydx.publicConnect import construct_market_prices
from cointegration_arbitrage.cointegration.calcCointegration import store_cointegration_result
from apscheduler.schedulers.background import BackgroundScheduler


def getCointegrationJob():
    print("Ejecutando getCointegrationJob()")
    try:
        client = connect_dydx()
    except Exception as err:
        print(err)
        print("Error connecting to client: ", err)
        exit(1)

    # Find Cointegrated Pairs
    # Construct market Prices
    try:
        print("Fetching market pricess, please allow 5 mins...")
        df_market_prices = construct_market_prices(client)
    except Exception as err:
        print("Error constructing market prices: ", err)
        exit(1)

        # Store Cointegrated Pairs
    try:
        print("Storing cointegrated pairs...")
        stores_result = store_cointegration_result(df_market_prices)
        
    except Exception as err:
        print("Error saving cointegrated pairs: ", err)
        exit(1)

    print('Cointegration se esta ejecutando!!')
    return JsonResponse(stores_result, safe=False)


def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(getCointegrationJob, 'interval', minutes=6)
    scheduler.start()