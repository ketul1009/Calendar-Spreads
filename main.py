from unittest import main
import pandas as pd
from utility_functions import *
import time

symbols = pd.read_csv('symbols50.csv')

for symbol in symbols['Symbol']:
    currentMonth = pd.read_csv(f'data copy/{symbol}_current_month.csv')
    nextMonth = pd.read_csv(f'data copy/{symbol}_next_month.csv')
    main_algo(currentMonth, nextMonth, symbol)