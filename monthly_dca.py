import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from dateutil.relativedelta import relativedelta
from datetime import datetime

#clean data_btc01
data_btc01 = pd.read_csv('BTC_USD01.csv')
data_btc01 = data_btc01.drop(data_btc01.columns[5:15], axis=1)


for i in data_btc01.index:
    time_str = data_btc01.iloc[i]['time']
    sliced = time_str[:10]
    data_btc01.at[i, 'time'] = sliced



#change columns mane
data_btc01 = data_btc01.rename(columns={'time': 'Date', 'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close'})
print("data_btc01\n",data_btc01,"\n")

#clean data_btc02
data_btc02 = pd.read_csv('BTC_USD02.csv')
data_btc02 = data_btc02.drop(data_btc02.columns[5:7], axis=1)
print("data_btc02\n",data_btc02,"\n")

#concatenate the dataframes vertically
data = pd.concat([data_btc01, data_btc02], axis=0)
data = data.reset_index()
data = data.drop(['index'], axis=1)
data['Date'] = pd.to_datetime(data['Date'])
data.to_csv("BTC_history.csv")
#print("break")
#exit()

cum_qty_list = []
avg_price_list = []

for date_to_cal in range(28):

    date_to_cal += 1
    #capital per trade
    capital = 30   #USD
    date = f'2017-12-{date_to_cal}' #date_start
    mask = data['Date'] >= date #date start cal
    data = data[mask]
    data = data.reset_index()
    data = data.drop(['index'], axis=1)
    print(data)


    format_str = '%Y-%m-%d'
    date = datetime.strptime(date, format_str).date()
    date_break = "2023-11-18"
    date_break_obj = datetime.strptime(date_break, format_str).date()


    #list for dca every month
    monthly_list = []
    while True:
        date = date + relativedelta(months=1)
        date_str = date.strftime(format_str)
        timestamp = pd.Timestamp(date_str)
        monthly_list.append(timestamp)
        if date > date_break_obj:
            break


    #dataFrame for buy monthly
    buy_data_monthly = pd.DataFrame([], columns=['Date', 'Price', 'qty', 'total_spend','cum_qty', 'cum_total_spent', 'usd_value', 'pnl', 'avg_price', 'pct_change'])
    count_index_monthly = 0
    def cal_cumulative_monthly(Date, Price, capi):
        global buy_data_monthly
        global count_index_monthly
        if buy_data_monthly['Date'].size == 0:
            print('in func')
            qty = capi/Price    #จำนวน bitcoin ที่ได้จากการซื้อ
            usd_value = qty*Price   #เป็นการซื้อตอนแรกจึงต้องใส่เป็นราคาที่ซื้อนะตอนนั้น
            avg_price = Price #ราคาเฉลี่ยของ bitcoin ที่ซื้อมา
            pnl = ((Price/avg_price))-1 #Profit and loss
            pct_change = (Price/Price)-1

            new_df = pd.DataFrame({'Date': [Date], 
                                    'Price': [Price], 
                                    'qty': [qty], 
                                    'total_spend': [capi], 
                                    'cum_qty': [qty], 
                                    'cum_total_spent': [capi],
                                    'usd_value': [usd_value], 
                                    'pnl': [pnl],
                                    'avg_price': [avg_price],
                                    'pct_change': [pct_change]})
            #print(new_df,"\n")
            # concatenate the new DataFrame with the original DataFrame
            buy_data_monthly = pd.concat([buy_data_monthly, new_df], ignore_index=True)

        else:
            #check month to buy dca
            if Date in monthly_list:
                capi = capi
            else:
                capi = 0

            qty = capi/Price    #จำนวน bitcoin ที่ได้จากการซื้อ
            cum_qty = qty+buy_data_monthly.iloc[count_index_monthly]['cum_qty']   #จำนวน bitcoin สะสม
            cum_total_spent = capi+buy_data_monthly.iloc[count_index_monthly]['cum_total_spent']   #จำนวนเงินที่ลงทุนไป
            usd_value = cum_qty*Price   #ราคาของจำนวนเงิน usd ณ ราคาตอนนั้น
            avg_price = cum_total_spent/cum_qty #ราคาเฉลี่ยของ bitcoin ที่ซื้อมา
            pnl = (Price/avg_price)-1 #Profit and loss
            pct_change = (Price/buy_data_monthly.iloc[0]['Price'])-1    
            new_df = pd.DataFrame({'Date': [Date], 
                                    'Price': [Price], 
                                    'qty': [qty], 
                                    'total_spend': [capi], 
                                    'cum_qty': [cum_qty], 
                                    'cum_total_spent': [cum_total_spent],
                                    'usd_value': [usd_value], 
                                    'pnl': [pnl],
                                    'avg_price': [avg_price],
                                    'pct_change': [pct_change]})
            buy_data_monthly = pd.concat([buy_data_monthly, new_df], ignore_index=True)
            count_index_monthly += 1


    #call function
    for index_num in data.index:
        date_of_buy = data.iloc[index_num]['Date']
        price_of_buy = data.iloc[index_num]['Close']
        cal_cumulative_monthly(date_of_buy, price_of_buy, capital)


    print("buy_data_monthly\n",buy_data_monthly,"\n\n")
    print("cum_qty = ",buy_data_monthly['cum_qty'].iloc[-1])
    print("\mAVG. = ",buy_data_monthly['avg_price'].iloc[-1])
    print(date_to_cal,"\n")

    cum_qty_list.append(buy_data_monthly['cum_qty'].iloc[-1])
    avg_price_list.append(buy_data_monthly['avg_price'].iloc[-1])



date_of_month = []
for i in range(28):
    i += 1
    str(i)
    date_of_month.append(i)

print("cum_qty_list = ", cum_qty_list[24])
print("avg_price_list = ", avg_price_list[24])

# creating the bar plot
plt.bar(date_of_month, cum_qty_list, color ='maroon',
        width = 0.8)

plt.yscale("log")
plt.xlabel("Date Of Month")
plt.ylabel("BTC")
plt.show()

plt.bar(date_of_month, avg_price_list, color ='green',
        width = 0.8)

plt.yscale("log")
plt.xlabel("Date Of Month")
plt.ylabel("AVG. Price")
plt.show()

