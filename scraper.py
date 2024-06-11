from utility_functions import *
import requests
import pandas as pd
from datetime import datetime, timedelta

#metaData
data = get_meta_data()
url = data['url']
cookies = data['cookies']
headers = data['headers']


expirysDf = pd.read_csv('Expiry Dates.csv')
expirys = expirysDf['Expiry']

# Extract the first day of the month for each expiry
first_days = [convert_to_datetime(expiry).replace(day=1) for expiry in expirys]

# Format the first days as strings in the same format
formatted_first_days = [day.strftime('%d-%m-%Y') for day in first_days]
formatted_expiry_days = [convert_to_datetime(expiry).strftime('%d-%m-%Y') for expiry in expirys]
from_dates = [(convert_to_datetime(expiry) + timedelta(days=1)).strftime('%d-%m-%Y') for expiry in expirys]
from_dates.insert(0, '01-01-2023')

near_month = pd.DataFrame()
next_month = pd.DataFrame()

for i in range(len(expirys)-1):
    nearMonthParams = {
        "from": from_dates[i],
        "to": formatted_expiry_days[i],
        "instrumentType": "FUTIDX",
        "symbol": "NIFTY",
        "year": 2023,
        "expiryDate": expirys[i],
    }
    nextMonthParams = {
        "from": from_dates[i],
        "to": formatted_expiry_days[i],
        "instrumentType": "FUTIDX",
        "symbol": "NIFTY",
        "year": 2023,
        "expiryDate": expirys[i+1],
    }

    try:
        # Send GET request to the API endpoint
        nearMonthResponse = requests.get(url, headers=headers, cookies=cookies,params=nearMonthParams)
        nextMonthResponse = requests.get(url, headers=headers, cookies=cookies,params=nextMonthParams)
                
        # Check if the request was successful (status code 200)
        if nearMonthResponse.status_code == 200 and nextMonthResponse.status_code==200:
            # Parse JSON data from the response
            print("SUCCESSFUL")
            nearMonthData = nearMonthResponse.json()
            nextMonthData = nextMonthResponse.json()
            nearMonthDf = pd.DataFrame(nearMonthData['data'])
            nextMonthDf = pd.DataFrame(nextMonthData['data'])
            near_month = pd.concat([near_month, nearMonthDf])
            next_month = pd.concat([next_month, nextMonthDf])
        else:
            print("Failed to retrieve data from API:", near_month.status_code)

    except Exception as e:
        print("\n========ERROR========\n")
        print(e)
        print(f"get(expiry=${expirys[i]}, from=${from_dates[i]}, to=${formatted_expiry_days[i]})")
        print(f"get(expiry=${expirys[i+1]}, from=${from_dates[i]}, to=${formatted_expiry_days[i]})")
        print("\n")
        print(f"Near month response code = {nearMonthResponse.status_code}")
        print(f"Next month response code = {nextMonthResponse.status_code}")
        print("\n=====================\n")

# near_month.to_csv('Near Month.csv', index=False)
# next_month.to_csv('Next Month.csv', index=False)