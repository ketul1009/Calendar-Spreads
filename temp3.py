from unittest import main
import pandas as pd
from utility_functions import *
import time
import urllib3

data = get_meta_data()

url = data['url']
expiry_url = data['expirys_url']
cookies = data['cookies']
headers = data['headers']
years = data['years']
symbolsDf = pd.read_csv('symbols50.csv')
symbols = symbolsDf['Symbol']

nearMonthParams = {
    'from':'25-01-2023',
    'to':'23-02-2023',
    'instrumentType':'FUTIDX',
    'symbol':'NIFTY',
    'year':'2024',
    'expiryDate':'23-Feb-2023'
}

# nearMonthResponse = requests.get(url, headers=headers, cookies=cookies,params=nearMonthParams)

def make_https_request(url):
    # Create a PoolManager instance
    http = urllib3.PoolManager()

    try:
        # Make a GET request
        response = http.request('GET', url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status == 200:
            # Print the response data
            print(response.data.decode('utf-8'))
        else:
            print(f"HTTP Error: {response.status}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
if __name__ == "__main__":
    start_time = time.time()
    make_https_request(url)
    print("--- %s seconds ---" % round(time.time() - start_time, 2))
