from utility_functions import *
import pandas as pd
symbols = pd.read_csv('symbols50.csv')
trades = get_consolidated_trades(symbols['Symbol'], 'Trades', export=None)

print(get_order_book(trades))