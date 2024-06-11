from utility_functions import *
import pandas as pd

data = get_meta_data()

url = data['url']
expiry_url = data['expirys_url']
cookies = data['cookies']
headers = data['headers']
years = data['years']
symbolsDf = pd.read_csv('symbols50.csv')
symbols = symbolsDf['Symbol']

# getExpirys(expiry_url, cookies, headers, years, export='Expiry Dates.csv')

expirysDf = pd.read_csv('Expiry Dates.csv')
expirys = expirysDf['Expiry']

for symbol in symbols:
    get_futures_data(url, cookies, headers, expirys, "FUTSTK", symbol, export="Historical Futures Data Copy")
