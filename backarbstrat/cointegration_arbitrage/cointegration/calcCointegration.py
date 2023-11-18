from django.utils import timezone
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from cointegration_arbitrage.models import Cointegrated_Pairs
from cointegration_arbitrage.dydx.const import MAX_HALF_LIFE, WINDOW

# Half life
def calculate_half_life(spread):
    # Se crea un DataFrame de pandas llamado df_spread a partir de la serie temporal "spread", con una columna denominada "spread" para almacenar los datos.
    df_spread = pd.DataFrame(spread, columns=["spread"])
    #  Se crea una nueva serie temporal llamada spread_lag que contiene los valores de "spread" desplazados una posición hacia arriba (un período de tiempo). Esto se hace utilizando la función shift(1) de pandas.
    spread_lag = df_spread.spread.shift(1)
    # Se ajusta el primer valor de spread_lag para que sea igual al segundo valor. Esto se hace para evitar valores nulos o incorrectos debido al desplazamiento.
    spread_lag.iloc[0] = spread_lag.iloc[1]
    # Se crea una nueva serie temporal llamada spread_ret que contiene la diferencia entre los valores actuales de "spread" y los valores desplazados de spread_lag. Esto calcula el rendimiento del spread en cada período.
    spread_ret = df_spread.spread - spread_lag
    # Se ajusta el primer valor de spread_ret para que sea igual al segundo valor. Esto se hace para evitar valores nulos o incorrectos debido al desplazamiento.
    spread_ret.iloc[0] = spread_ret.iloc[1]
    # Se agrega una columna constante (constante) a la serie temporal spread_lag utilizando la función add_constant() de la biblioteca statsmodels (sm). Esto es necesario para realizar la regresión lineal.
    spread_lag2 = sm.add_constant(spread_lag)
    # Se crea un modelo de regresión lineal de mínimos cuadrados ordinarios (OLS) utilizando la función OLS() de statsmodels. La variable dependiente es spread_ret y la variable independiente es spread_lag2.
    model = sm.OLS(spread_ret, spread_lag2)
    # Se ajusta el modelo a los datos utilizando el método fit() y se obtienen los resultados de la regresión en el objeto res.
    res = model.fit()
    #  Se calcula la semivida (halflife) utilizando el coeficiente de la variable independiente en la regresión (res.params[1]). La semivida se calcula como el logaritmo natural de 2 dividido por el coeficiente, y se redondea al número entero más cercano.
    halflife = round(-np.log(2) / res.params[1], 0)
    return halflife

# ZScore
def calculate_zscore(spread):
    # spread_series = pd.Series(spread)
    # mean = spread_series.rolling(center=False, window=WINDOW).mean()
    # # Standard deviation
    # std = spread_series.rolling(center=False, window=WINDOW).std()
    # x = spread_series.rolling(center=False, window=1).mean()
    # zscore = (x - mean) / std
    # return zscore

    # Se crea un objeto de la serie temporal llamado spread_series a partir de la lista o array spread.
    spread_series = pd.Series(spread)
    #  Se calcula la media móvil de la serie spread_series utilizando la función rolling().mean(). La ventana de tamaño utilizada está especificada por la variable WINDOW.
    mean = spread_series.rolling(center=False, window=WINDOW).mean()
    # Standard deviation
    #  Se calcula la desviación estándar móvil de la serie spread_series utilizando la función rolling().std(). La ventana de tamaño utilizada está especificada por la variable WINDOW.
    std = spread_series.rolling(center=False, window=WINDOW).std()

    # Cambio: Elimina la ventana de tamaño 1
    #  Se asigna la serie spread_series a la variable x. En este caso, no se realiza un promedio móvil con ventana 1 como se indica en el código original.
    x = spread_series
    # Se calcula el z-score de la serie x utilizando la media móvil mean y la desviación estándar móvil std. El z-score indica cuántas desviaciones estándar un valor específico se encuentra por encima o por debajo de la media.
    zscore = (x - mean) / std

    # Cambio: Manejar NaN en la serie zscore (opcional)
    # Se realiza un cambio opcional para manejar los valores NaN en la serie zscore. Aquí, se reemplazan los valores NaN con ceros utilizando la función fillna().
    zscore = zscore.fillna(0)  # Reemplaza NaN con 0

    return zscore

# Cointegración de criptos


def calculate_cointegration(series_1, series_2):
    #  Se convierte la serie "series_1" en un array numpy de tipo float.
    series_1 = np.array(series_1).astype(float)
    # Se convierte la serie "series_2" en un array numpy de tipo float.
    series_2 = np.array(series_2).astype(float)
    #  Se inicializa la variable "coint_flag" con el valor 0. Esta variable se utilizará para indicar si hay cointegración o no.
    coint_flag = 0
    #  Se calcula la prueba de cointegración entre las dos series utilizando la función coint() de la biblioteca statsmodels. El resultado se almacena en la variable "coint_res".
    coint_res = coint(series_1, series_2)
    #  Se extrae el valor de la estadística de prueba (t-valor) de la prueba de cointegración y se guarda en la variable "coint_t".
    coint_t = coint_res[0]
    #  Se extrae el valor de p (p-value) de la prueba de cointegración y se guarda en la variable "p_value".
    p_value = coint_res[1]
    #  Se extrae el valor crítico correspondiente al nivel de significancia del 1% de la prueba de cointegración y se guarda en la variable "critical_value".
    critical_value = coint_res[2][1]
    # Se ajusta un modelo de regresión lineal utilizando la función OLS() de statsmodels. La variable dependiente es "series_1" y la variable independiente es "series_2"
    model = sm.OLS(series_1, series_2).fit()
    # Se obtiene el coeficiente de la variable independiente (pendiente de la regresión) del modelo ajustado y se guarda en la variable "hedge_ratio".
    hedge_ratio = model.params[0]
    # Se calcula la serie "spread" restando el producto del coeficiente de cobertura ("hedge_ratio") multiplicado por "series_2" de "series_1". Esta serie representa la diferencia entre las dos series teniendo en cuenta la relación cointegrada.
    spread = series_1 - (hedge_ratio * series_2)
    # Se calcula la semivida ("half_life") de la serie "spread" utilizando una función llamada "calculate_half_life()". Esta función no se muestra en el código proporcionado, pero se asume que calcula la semivida de acuerdo a alguna lógica específica.
    half_life = calculate_half_life(spread)
    # Se verifica si el valor de "coint_t" es menor que el valor crítico "critical_value". Esto se hace para determinar si la estadística de prueba está por debajo del nivel crítico, lo que indicaría la presencia de cointegración.
    t_check = coint_t < critical_value
    #  Se actualiza el valor de "coint_flag" a 1 si el valor de "p_value" es menor que 0.05 y si "t_check" es verdadero, lo que indica que hay cointegración. De lo contrario, se mantiene en 0.
    coint_flag = 1 if p_value < 0.05 and t_check else 0
    
    return coint_flag, hedge_ratio, half_life, spread

# Store Cointegration


def store_cointegration_result(df_market_prices):

    # Initialize
    markets = df_market_prices.columns.to_list()
    criteria_met_pairs = []

    # Find cointegrated pairs
    # Start with our base pair
    for index, base_market in enumerate(markets[:-1]):
        series_1 = df_market_prices[base_market].values.astype(float).tolist()
        last_price_1 = df_market_prices[base_market].iloc[-1]

        # Get Quote Pair
        for quote_market in markets[index + 1:]:
            series_2 = df_market_prices[quote_market].values.astype(
                float).tolist()
            last_price_2 = df_market_prices[quote_market].iloc[-1]

            # Check cointegration
            coint_flag, hedge_ratio, half_life_tuple, spread = calculate_cointegration(
                series_1, series_2)
            half_life = float(half_life_tuple[0]) if isinstance(half_life_tuple, tuple) else float(half_life_tuple)


            # zscore
            z_score = calculate_zscore(spread).values.tolist()

            if not isinstance(spread, pd.DataFrame):
                spread = pd.DataFrame(spread)
                spreadNum = spread.values.tolist()

            # Log Pair
            # if coint_flag == 1 and half_life <= MAX_HALF_LIFE and half_life > 0:
            # if coint_flag == 1:
                criteria_met_pairs.append({
                    "base_market": base_market,
                    "quote_market": quote_market,
                    "hedge_ratio": hedge_ratio,
                    "half_life": half_life,
                    "spread": spreadNum,
                    "z-score": z_score,
                    "last_price_1": last_price_1,
                    "last_price_2": last_price_2
                })

    # Create and save DataFrame
    df_criteria_met = pd.DataFrame(criteria_met_pairs)
    df_criteria_met.to_csv("cointegrated_pairs.csv")
    del df_criteria_met

    # Save in DB
    for pair in criteria_met_pairs:
        # Extract values from the pair dictionary
        base_market = pair["base_market"]
        quote_market = pair["quote_market"]
        hedge_ratio = pair["hedge_ratio"]
        half_life = pair["half_life"]
        spread = pair["spread"]
        z_score = pair["z-score"]
        last_price_1 = pair["last_price_1"]
        last_price_2 = pair["last_price_2"]

        spread_flat_list = [item for sublist in spread for item in sublist]

        # Check if the pair already exists in the database
        pair_exists = Cointegrated_Pairs.objects.filter(
            Crypto1_ID=base_market,
            Crypto2_ID=quote_market
        ).exists()

        if not pair_exists:
            # Create a new instance of the Cointegrated_Pairs model
            new_pair = Cointegrated_Pairs(
                Crypto1_ID=base_market,
                Crypto2_ID=quote_market,
                Date_detection=timezone.now(),
                Spread=spread_flat_list,
                z_score=z_score,
                hedge_ratio=hedge_ratio,
                half_life=half_life,
                last_price_1=last_price_1,
                last_price_2=last_price_2
            )

            print(f"Pair {base_market}-{quote_market} saved in the database")
            # Save the new instance to the database
            new_pair.save()
        else:
            # Get the existing instance of the Cointegrated_Pairs model
            existing_pair = Cointegrated_Pairs.objects.get(
                Crypto1_ID=base_market, Crypto2_ID=quote_market)

            # Update the fields
            existing_pair.Date_detection = timezone.now()
            existing_pair.Spread = spread_flat_list
            existing_pair.z_score = z_score
            existing_pair.hedge_ratio = hedge_ratio
            existing_pair.half_life = half_life
            existing_pair.last_price_1 = last_price_1
            existing_pair.last_price_2 = last_price_2

            # Save the updated instance to the database
            existing_pair.save()

            print(f"Pair {base_market}-{quote_market} updated in the database")


def allZscore():
    calculate_zscore()
