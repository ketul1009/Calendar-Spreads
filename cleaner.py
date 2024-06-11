import pandas as pd
from utility_functions import *

symbols = pd.read_csv('symbols50.csv')

for symbol in symbols['Symbol']:
    # df = pd.read_csv(f'Historical Futures Data Copy/{symbol}_next_month.csv')
    # df1 = pd.read_csv(f'Historical Futures Data Copy/{symbol}_current_month.csv')
    # df.drop(index=385, inplace=True)
    # df.to_csv(f'data copy/{symbol}_next_month.csv', index=False)
    # df1.to_csv(f'data copy/{symbol}_current_month.csv', index=False)
    data_cleaner(symbol, 'data copy')