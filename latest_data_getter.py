from operator import index
from utility_functions import *
import pandas as pd

data = get_meta_data()

url = data['url']
expiry_url = data['expirys_url']
cookies = data['cookies']
headers = data['headers']
symbols = pd.read_csv('symbols50.csv')
expirys = ["25-Apr-2024", "30-May-2024", "27-Jun-2024", "25-Jul-2024"]

for symbol in symbols['Symbol']:

    # if(symbol in ['BAJAJ_AUTO', 'M_M', 'SUNPHARMA']):

    get_futures_data(url, cookies, headers, expirys, "FUTSTK", symbol=symbol, export="HFD")


        # try:
        #     current = pd.read_csv(f'Historical Futures Data/{symbol}_current_month.csv')
        #     next = pd.read_csv(f'Historical Futures Data/{symbol}_next_month.csv')
        #     data  = get_futures_row(
        #         url = url,
        #         cookies = cookies,
        #         headers = headers,
        #         fromDate="26-04-2024",
        #         endDate="11-06-2024",
        #         currentExpiry="25-Apr-2024",
        #         nextExpiry="30-May-2024",
        #         instrumentType="FUTSTK",
        #         symbol=symbol,
        #     )
        
        #     current = pd.concat([current, data[0]])
        #     next = pd.concat([next, data[1]])
        #     current.to_csv(f'Historical Futures Data/{symbol}_current_month.csv', index=False)
        #     next.to_csv(f'Historical Futures Data/{symbol}_next_month.csv', index=False)

        # except Exception as e:
            # print(f"Symbol: {symbol}, {e}")