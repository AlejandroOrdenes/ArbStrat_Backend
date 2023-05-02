from django.utils import timezone
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.stattools import coint
from cointegration_arbitrage.models import Cointegrated_Pairs
from cointegration_arbitrage.dydx.const import MAX_HALF_LIFE, WINDOW

# Half life


def calculate_half_life(spread):
    df_spread = pd.DataFrame(spread, columns=["spread"])
    spread_lag = df_spread.spread.shift(1)
    spread_lag.iloc[0] = spread_lag.iloc[1]
    spread_ret = df_spread.spread - spread_lag
    spread_ret.iloc[0] = spread_ret.iloc[1]
    spread_lag2 = sm.add_constant(spread_lag)
    model = sm.OLS(spread_ret, spread_lag2)
    res = model.fit()
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
    spread_series = pd.Series(spread)
    mean = spread_series.rolling(center=False, window=WINDOW).mean()
    # Standard deviation
    std = spread_series.rolling(center=False, window=WINDOW).std()

    # Cambio: Elimina la ventana de tamaño 1
    x = spread_series

    zscore = (x - mean) / std

    # Cambio: Manejar NaN en la serie zscore (opcional)
    zscore = zscore.fillna(0)  # Reemplaza NaN con 0

    return zscore

# Cointegración de criptos


def calculate_cointegration(series_1, series_2):
    series_1 = np.array(series_1).astype(float)
    series_2 = np.array(series_2).astype(float)
    coint_flag = 0
    coint_res = coint(series_1, series_2)
    coint_t = coint_res[0]
    p_value = coint_res[1]
    critical_value = coint_res[2][1]
    model = sm.OLS(series_1, series_2).fit()
    hedge_ratio = model.params[0]
    spread = series_1 - (hedge_ratio * series_2)
    half_life = calculate_half_life(spread)
    t_check = coint_t < critical_value
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
            coint_flag, hedge_ratio, half_life, spread = calculate_cointegration(
                series_1, series_2)

            # zscore
            z_score = calculate_zscore(spread).values.tolist()

            if not isinstance(spread, pd.DataFrame):
                spread = pd.DataFrame(spread)
                spreadNum = spread.values.tolist()

            # Log Pair
            if coint_flag == 1 and half_life <= MAX_HALF_LIFE and half_life > 0:
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
            existing_pair = Cointegrated_Pairs.objects.get(Crypto1_ID=base_market, Crypto2_ID=quote_market)

            # Update the fields
            existing_pair.Date_detection = timezone.now()
            existing_pair.Spread = spread_flat_list
            existing_pair.z_score = z_score
            existing_pair.hedge_ratio = hedge_ratio
            existing_pair.half_life = half_life,
            last_price_1=last_price_1,
            last_price_2=last_price_2

            # Save the updated instance to the database
            existing_pair.save()

            print(f"Pair {base_market}-{quote_market} updated in the database")


def allZscore():
    calculate_zscore()
