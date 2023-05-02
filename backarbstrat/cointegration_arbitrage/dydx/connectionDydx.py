from dydx3 import Client


# COnnect to dydx
def connect_dydx():

    client = Client(
    host='https://api.dydx.exchange',
    )

    print("Connection Successful")
    return client