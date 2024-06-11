from utility_functions import *
import pandas as pd

symbols = pd.read_csv('symbols50.csv')
get_tracker(symbols['Symbol'], 'data copy copy', 200)