import json
from datetime import datetime, timedelta
import pandas as pd
import requests
import matplotlib.pyplot as plt
import time
import pyperclip

#function to get meta data
def get_meta_data():
    try:
        with open("meta.json", "r") as file:
            data = json.load(file)
    except Exception as e:
        print(e)
        return e

    return data

# Define a function to convert string date to datetime object
def convert_to_datetime(date_str):
    return datetime.strptime(date_str, '%d-%b-%Y')

#function to get all available expirys
def get_expirys(url, cookies, headers, years, export=None):
    expirys = []
    for year in years:
        params = {
            'instrument': 'FUTIDX',
            'symbol' : 'NIFTY',
            'year': year
        }

        response = requests.get(url, headers=headers, cookies=cookies,params=params)
        expirys = expirys + response.json()['expiresDts']

    expirys = pd.DataFrame(expirys, columns=['Expiry'])
    if(export!=None):
        expirys.to_csv(f'{export}', index=False)
        return expirys
    else:
        return expirys

#function to set cookies
def set_cookies(cookieString):
    cookies = {}
    for cookie in cookieString.split('; '):
        key, value = cookie.split('=', 1)
        cookies[key] = value

    with open("meta.json", "r") as file:
        data = json.load(file)
        data['cookies'] = cookies

    new_data = json.dumps(data, indent=4)

    with open("meta.json", "w") as file:
        file.write(new_data)

#function to get Futures data of a symbol
def get_futures_data(url, cookies, headers, expirys, instrumentType, symbol, export):

    try:
        startDate = convert_to_datetime(expirys[0]).replace(day=1)
        formattedStartDate = startDate.strftime('%d-%m-%Y')
        
        formatted_expiry_days = [convert_to_datetime(expiry).strftime('%d-%m-%Y') for expiry in expirys]
        from_dates = [(convert_to_datetime(expiry) + timedelta(days=1)).strftime('%d-%m-%Y') for expiry in expirys]
        from_dates.insert(0, formattedStartDate)

        near_month = pd.DataFrame()
        next_month = pd.DataFrame()

        for i in range(len(expirys)-1):
            nearMonthParams = {
                "from": from_dates[i],
                "to": formatted_expiry_days[i],
                "instrumentType": instrumentType,
                "symbol": symbol,
                "year": 2023,
                "expiryDate": expirys[i],
            }
            nextMonthParams = {
                "from": from_dates[i],
                "to": formatted_expiry_days[i],
                "instrumentType": instrumentType,
                "symbol": symbol,
                "year": 2023,
                "expiryDate": expirys[i+1],
            }

            try:
                start_time = time.time()
                # Send GET request to the API endpoint
                nearMonthResponse = requests.get(url, headers=headers, cookies=cookies,params=nearMonthParams)
                print("--- %s seconds ---" % round(time.time() - start_time, 2))
                nextMonthResponse = requests.get(url, headers=headers, cookies=cookies,params=nextMonthParams)
                # Check if the request was successful (status code 200)
                if nearMonthResponse.status_code == 200 and nextMonthResponse.status_code==200:
                    print("SUCCESSFUL")
                    # Parse JSON data from the response
                    nearMonthData = nearMonthResponse.json()
                    nextMonthData = nextMonthResponse.json()
                    nearMonthDf = pd.DataFrame(nearMonthData['data'])
                    nextMonthDf = pd.DataFrame(nextMonthData['data'])
                    near_month = pd.concat([near_month, nearMonthDf])
                    next_month = pd.concat([next_month, nextMonthDf])
                else:
                    print("Failed to retrieve data from API:", near_month.status_code)

            except Exception as e:
                print(f"\n========ERROR for {symbol}========\n")
                print(e)
                print(f"get(expiry=${expirys[i]}, from=${from_dates[i]}, to=${formatted_expiry_days[i]})")
                print(f"get(expiry=${expirys[i+1]}, from=${from_dates[i]}, to=${formatted_expiry_days[i]})")
                print("\n")
                print(f"Near month response code = {nearMonthResponse.status_code}")
                print(f"Next month response code = {nextMonthResponse.status_code}")
                print("\n=====================\n")

        near_month.to_csv(f'{export}/{symbol}_current_month.csv', index=False)
        next_month.to_csv(f'{export}/{symbol}_next_month.csv', index=False)

        print(f"Data Fetched Succesfully for {symbol}")

    except Exception as e:
        print(f"{e}, symbol  = {symbol}")

#function to get orderbook
def get_order_book(trades, equity=100000):
    
    orderBook = []
    for index, trade in trades.iterrows():
        # orderEntry = {'Date': trade['Entry Date'], 'PnL':0, 'equity': equity}
        orderExit = {'Date': trade['Exit Current Date'], 'PnL': trade['PNL'], 'equity':equity+trade['PNL']}
        # orderBook.append(orderEntry)
        orderBook.append(orderExit)
        equity = equity + trade['PNL']

    orderBook = pd.DataFrame(orderBook)
    orderBook['Date'] = pd.to_datetime(orderBook['Date'])
    orderBook = orderBook.sort_values(by='Date')
    return orderBook

#main function which runs algo
def main_algo(df1, df2, symbol):
    currentMonth = df1
    nextMonth = df2

    futuresDf = pd.DataFrame()

    futuresDf['Current Date'] = currentMonth['FH_TIMESTAMP']
    futuresDf['Next Date'] = nextMonth['FH_TIMESTAMP']
    futuresDf['Current'] = currentMonth['FH_CLOSING_PRICE']
    futuresDf['Next'] = nextMonth['FH_CLOSING_PRICE']
    futuresDf['Difference'] = nextMonth['FH_CLOSING_PRICE']-currentMonth['FH_CLOSING_PRICE']
    futuresDf['Expiry'] = currentMonth['FH_EXPIRY_DT']
    futuresDf['Lot'] = currentMonth['FH_MARKET_LOT']

    i=0
    trades = []
    openTrade = False
    trade = {}
    tradeType = None

    while(i<len(futuresDf)-201):
        if(not openTrade):
            tempDf = futuresDf[i:i+200]
            mean = round(tempDf['Difference'].mean(), 2)
            stdDev = round(tempDf['Difference'].std(), 2)
            upperRange = mean + (3*stdDev)
            lowerRange = mean - (3*stdDev)
            row = futuresDf.iloc[i+201]
            diffenrece = row['Difference']
            if(diffenrece>upperRange and not openTrade and row['Current Date']!=row['Expiry']):
                trade['Symbol'] = symbol
                trade['Current Entry Date'] = row['Current Date']
                trade['Next Entry Date'] = row['Next Date']
                trade['Upper'] = upperRange
                trade['Lower'] = lowerRange
                trade['Entry Difference'] = row['Difference']
                trade['Type'] = "Short"
                trade['Current Month Entry'] = row['Current']
                trade['Next Month Entry'] = row['Next']
                trade['Lot'] = row['Lot']
                openTrade = True
                tradeType=0

            elif(diffenrece<lowerRange and not openTrade and row['Current Date']!=row['Expiry']):
                trade['Symbol'] = symbol
                trade['Current Entry Date'] = row['Current Date']
                trade['Next Entry Date'] = row['Next Date']
                trade['Upper'] = upperRange
                trade['Lower'] = lowerRange
                trade['Entry Difference'] = row['Difference']
                trade['Type'] = "Long"
                trade['Current Month Entry'] = row['Current']
                trade['Next Month Entry'] = row['Next']
                trade['Lot'] = row['Lot']
                openTrade = True
                tradeType=1

            i=i+1
        
        else:
            row = futuresDf.iloc[i+201]
            diffenrece = row['Difference']

            if((openTrade and tradeType==0 and diffenrece<upperRange) or (row['Current Date']==row['Expiry'])):
                trade['Exit Current Date'] = row['Current Date']
                trade['Exit Next Date'] = row['Next Date']
                trade['Exit Difference'] = row['Difference']
                trade['Current Month Exit'] = row['Current']
                trade['Next Month Exit'] = row['Next']
                trades.append(trade)
                openTrade = False
                trade={}
        
            elif((openTrade and tradeType==1 and diffenrece>lowerRange) or (row['Current Date']==row['Expiry'])):
                trade['Exit Current Date'] = row['Current Date']
                trade['Exit Next Date'] = row['Next Date']
                trade['Exit Difference'] = row['Difference']
                trade['Current Month Exit'] = row['Current']
                trade['Next Month Exit'] = row['Next']
                trades.append(trade)
                openTrade = False
                trade={}
            
            i=i+1

    trades = pd.DataFrame(trades)

    pnl = []

    for index, trade in trades.iterrows():
        if(trade['Type']=='Short'):
            nearMonthPl = (trade['Next Month Entry'] - trade['Next Month Exit'])*(trade['Lot'])
            currentMonthPl = (trade['Current Month Exit'] - trade['Current Month Entry'])*(trade['Lot'])
            pnl.append(nearMonthPl+currentMonthPl-500)

        else:
            nearMonthPl = (trade['Next Month Exit'] - trade['Next Month Entry'])*(trade['Lot'])
            currentMonthPl = (trade['Current Month Entry'] - trade['Current Month Exit'])*(trade['Lot'])
            pnl.append(nearMonthPl+currentMonthPl-500)

    trades['PNL'] = pnl
    trades.to_csv(f'Trades/{symbol} Trades.csv', index=False)

#function to get margin required
def get_margin(trades):

    orderBook = []
    for index, trade in trades.iterrows():
        orderEntry = {'Date': trade['Entry Date'], 'Margin':trade['Margin']}
        orderExit = {'Date': trade['Exit Date'], 'Margin': -1*trade['Margin']}
        orderBook.append(orderEntry)
        orderBook.append(orderExit)

    orderBook = pd.DataFrame(orderBook)
    orderBook['Date'] = pd.to_datetime(orderBook['Date'])
    orderBook = orderBook.sort_values(by='Date')
    return orderBook

def data_cleaner(symbol, dataLocation):
    nearMonth = pd.read_csv(f'{dataLocation}/{symbol}_current_month.csv')
    nextMonth = pd.read_csv(f'{dataLocation}/{symbol}_next_month.csv')

    for index, row in nearMonth.iterrows():
        if(nearMonth.iloc[index]['FH_TIMESTAMP']!=nextMonth.iloc[index]['FH_TIMESTAMP']):
            print(f"============{symbol}============")
            print(f"{index} = {nearMonth.iloc[index]['FH_TIMESTAMP']} {nextMonth.iloc[index]['FH_TIMESTAMP']}")
            break

def extract_from_json(jsonObj):
    csv_string = ','.join(f'{value}' if isinstance(value, (int, float)) else value for value in jsonObj.values())
    print(csv_string)
    pyperclip.copy(csv_string)

def get_futures_row(url, cookies, headers, fromDate, endDate, currentExpiry, nextExpiry, instrumentType, symbol):

    nearMonthParams = {
        "from": fromDate,
        "to": endDate,
        "instrumentType": instrumentType,
        "symbol": symbol,
        "year": 2023,
        "expiryDate": currentExpiry,
    }
    nextMonthParams = {
        "from": fromDate,
        "to": endDate,
        "instrumentType": instrumentType,
        "symbol": symbol,
        "year": 2023,
        "expiryDate": nextExpiry,
    }

    try:
        start_time = time.time()
        # Send GET request to the API endpoint
        nearMonthResponse = requests.get(url, headers=headers, cookies=cookies,params=nearMonthParams)
        print("--- %s seconds ---" % round(time.time() - start_time, 2))
        nextMonthResponse = requests.get(url, headers=headers, cookies=cookies,params=nextMonthParams)
        # Check if the request was successful (status code 200)
        if nearMonthResponse.status_code == 200 and nextMonthResponse.status_code==200:
            print("SUCCESSFUL")
            # Parse JSON data from the response
            nearMonthData = nearMonthResponse.json()
            nextMonthData = nextMonthResponse.json()
            nearMonthDf = pd.DataFrame(nearMonthData['data'])
            nextMonthDf = pd.DataFrame(nextMonthData['data'])
            return [nearMonthDf, nextMonthDf]
        else:
            print("Failed to retrieve data from API:", nearMonthResponse.status_code)

    except Exception as e:
        print(f"\n========ERROR for {symbol}========\n")
        print(e)
        print(f"get(expiry=${currentExpiry}, from=${fromDate}, to=${endDate})")
        print(f"get(expiry=${nextExpiry}, from=${fromDate}, to=${endDate})")
        print("\n")
        print(f"Near month response code = {nearMonthResponse.status_code}")
        print(f"Next month response code = {nextMonthResponse.status_code}")
        print("\n=====================\n")

    print(f"Data Fetched Succesfully for {symbol}")

def get_tracker(symbols, dataLocation, lookback):
    tracker = []
    for symbol in symbols:
        df1 = pd.read_csv(f'{dataLocation}/{symbol}_current_month.csv')
        df2 = pd.read_csv(f'{dataLocation}/{symbol}_next_month.csv')
        currentMonth = df1
        nextMonth = df2

        futuresDf = pd.DataFrame()

        futuresDf['Current Date'] = currentMonth['FH_TIMESTAMP']
        futuresDf['Next Date'] = nextMonth['FH_TIMESTAMP']
        futuresDf['Current'] = currentMonth['FH_CLOSING_PRICE']
        futuresDf['Next'] = nextMonth['FH_CLOSING_PRICE']
        futuresDf['Difference'] = nextMonth['FH_CLOSING_PRICE']-currentMonth['FH_CLOSING_PRICE']
        futuresDf['Expiry'] = currentMonth['FH_EXPIRY_DT']
        futuresDf['Lot'] = currentMonth['FH_MARKET_LOT']
        tempDf = futuresDf[len(futuresDf)-lookback-1:len(futuresDf)-1]
        mean = round(tempDf['Difference'].mean(), 2)
        stdDev = round(tempDf['Difference'].std(), 2)
        upperRange = mean + (3*stdDev)
        lowerRange = mean - (3*stdDev)
        tracker.append({
            'symbol': symbol,
            'upperRange': upperRange,
            'lowerRange': lowerRange,
            'difference': futuresDf.iloc[len(futuresDf)-1]['Difference']
        })
        # print(futuresDf.iloc[len(futuresDf)-1])

    trackerDf = pd.DataFrame(tracker)
    print(trackerDf)

def get_consolidated_trades(symbols, trades_folder, export):
    consolidated_trades = pd.DataFrame()
    for symbol in symbols:
        trades = pd.read_csv(f'{trades_folder}/{symbol} Trades.csv')
        consolidated_trades = pd.concat([consolidated_trades, trades])

    if(export!=None):
        consolidated_trades.to_csv(export, index=False)

    return consolidated_trades
