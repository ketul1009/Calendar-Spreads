import pandas as pd

def mainAlgo(df1, df2, symbol):
    currentMonth = df1
    nextMonth = df2

    futuresDf = pd.DataFrame()

    futuresDf['Date'] = currentMonth['FH_TIMESTAMP']
    futuresDf['Current'] = currentMonth['FH_CLOSING_PRICE']
    futuresDf['Next'] = nextMonth['FH_CLOSING_PRICE']
    futuresDf['Difference'] = nextMonth['FH_CLOSING_PRICE']-currentMonth['FH_CLOSING_PRICE']
    futuresDf['Expiry'] = currentMonth['FH_EXPIRY_DT']

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
            if(diffenrece>upperRange and not openTrade):
                trade['Entry Date'] = row['Date']
                trade['Upper'] = upperRange
                trade['Lower'] = lowerRange
                trade['Entry Difference'] = row['Difference']
                trade['Type'] = "Short"
                trade['Current Month Entry'] = row['Current']
                trade['Next Month Entry'] = row['Next']
                openTrade = True
                tradeType=0

            elif(diffenrece<lowerRange and not openTrade):
                trade['Entry Date'] = row['Date']
                trade['Upper'] = upperRange
                trade['Lower'] = lowerRange
                trade['Entry Difference'] = row['Difference']
                trade['Type'] = "Long"
                trade['Current Month Entry'] = row['Current']
                trade['Next Month Entry'] = row['Next']
                openTrade = True
                tradeType=1

            i=i+1
        
        else:
            row = futuresDf.iloc[i+201]
            diffenrece = row['Difference']

            if((openTrade and tradeType==0 and diffenrece<upperRange) or (row['Date']==row['Expiry'])):
                trade['Exit Date'] = row['Date']
                trade['Exit Difference'] = row['Difference']
                trade['Current Month Exit'] = row['Current']
                trade['Next Month Exit'] = row['Next']
                trades.append(trade)
                openTrade = False
                trade={}
        
            elif((openTrade and tradeType==1 and diffenrece>lowerRange) or (row['Date']==row['Expiry'])):
                trade['Exit Date'] = row['Date']
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
            nearMonthPl = (trade['Next Month Entry'] - trade['Next Month Exit'])*50
            currentMonthPl = (trade['Current Month Exit'] - trade['Current Month Entry'])*50
            pnl.append(nearMonthPl+currentMonthPl-500)

        else:
            nearMonthPl = (trade['Next Month Exit'] - trade['Next Month Entry'])*50
            currentMonthPl = (trade['Current Month Entry'] - trade['Current Month Exit'])*50
            pnl.append(nearMonthPl+currentMonthPl-500)

    trades['PNL'] = pnl
    trades.to_csv(f'Trades/{symbol} Trades.csv', index=False)
