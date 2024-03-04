import os
from altair import List
import streamlit as st
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly
from plotly.subplots import make_subplots
import plotly.graph_objects as go

def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row], columns=row.index)]
           ).reset_index(drop=True)
    

def derrivation_checker(Series:pd.Series, Type_list: List[str], Check_list: List[str]):
    for type in Type_list:
        for check in Check_list:
            try:
                if Series[type] == check:
                    return True
            except KeyError:
                pass
    return False

def get_derrivation(Series:pd.Series, Derrivation_List: List[str]) -> str: 
    for derrivation in Derrivation_List:
        try: return Series[derrivation] 
        except KeyError: pass
    raise KeyError


derrivation_type = ["Type", "InOut"]
derrivation_deposit = ["Deposit", "In"]
derrivation_ticker = ["Symbol", "Ticker", "Currency"]
derrivation_amount = ["Amount"]
derrivation_time = ["Time", "Date", "Timestamp"]
derrivation_trade = ["Spot Market"]
derrivation_pairs = ["Market"]
derrivation_side = ["Side"]
derrivation_price = ["Price"]
derrivation_quantity = ["Quantity"]
derrivation_quantity_2 = ["TotalWithFee"]


dict_time_format = {"Xeggex": "%m/%d/%Y, %H:%M:%S %p",
                    "zephyr": " %d %b %Y %H:%M:%S %Z"}
pairs_str_sep = ["/", "_"]


st.title('My Crypto_Tracker')

deposit_dataset = pd.DataFrame(columns=["Time"])
trade_dataset = pd.DataFrame(columns=["Time"])

price_dataset = pd.DataFrame(columns=["Time"])
for file in os.listdir("Dataset/Prices/"):
    df = pd.read_csv("Dataset/Prices/" + file)
    for i in range(len(df)):
        time = df.loc[i, "Time"]
        time_converted = datetime.datetime.strptime(time, "%d/%m/%Y").replace(minute=0, second=0, hour=0)
        if "Time" not in price_dataset or time_converted not in list(price_dataset["Time"]):
            new_row = pd.Series({"Time": time_converted, f"{df.columns[1]}":df.loc[i, df.columns[1]]})
            price_dataset = append_row(price_dataset, new_row)
        elif df.columns[1] not in price_dataset.columns:
            price_dataset[df.columns[1]] = 0
            price_dataset.loc[np.argwhere(price_dataset["Time"] == time_converted)[0, 0], df.columns[1]] = df.loc[i, df.columns[1]]
        else:
            price_dataset.fillna(0, inplace=True)
            price_dataset.loc[np.argwhere(price_dataset["Time"] == time_converted)[0, 0], df.columns[1]] = df.loc[i, df.columns[1]]
            

for file in os.listdir("Dataset/2024/March/"):
    df  = pd.read_csv("Dataset/2024/March/" + file)
    for i in range(len(df)):
        if derrivation_checker(df.iloc[i], derrivation_type, derrivation_deposit):
            ticker = get_derrivation(df.iloc[i], derrivation_ticker)
            amount = get_derrivation(df.iloc[i], derrivation_amount)
            time = get_derrivation(df.iloc[i], derrivation_time)
            conversion = dict_time_format[file.split("_")[0]]
            time_converted = datetime.datetime.strptime(time, conversion).replace(minute=0, second=0, hour=0)
            if "Time" not in deposit_dataset or time_converted not in list(deposit_dataset["Time"]):
                new_row = pd.Series({"Time": time_converted, f"{ticker}":amount})
                deposit_dataset = append_row(deposit_dataset, new_row)
            elif ticker not in deposit_dataset.columns:  # date is in pd.Series but ticker not
                #dataset[ticker] = dataset.insert(2, ticker, 0)
                deposit_dataset[ticker] = 0
                deposit_dataset.loc[np.argwhere(deposit_dataset["Time"] == time_converted)[0, 0], ticker] = amount

            else:  # time and ticker are already there
                deposit_dataset.fillna(0, inplace=True)
                deposit_dataset.loc[np.argwhere(deposit_dataset["Time"] == time_converted)[0, 0], ticker] += amount
            deposit_dataset.fillna(0, inplace=True)
        elif derrivation_checker(df.iloc[i], derrivation_type, derrivation_trade):
            time = get_derrivation(df.iloc[i], derrivation_time)
            conversion = dict_time_format[file.split("_")[0]]
            time_converted = datetime.datetime.strptime(time, conversion).replace(minute=0, second=0, hour=0)
            
            pair = get_derrivation(df.iloc[i], derrivation_pairs)
            side = get_derrivation(df.iloc[i], derrivation_side)
            for sep in pairs_str_sep:
                if len(pair.split(sep)) != 1:
                    pair = pair.split(sep)
                    break
            price = get_derrivation(df.iloc[i], derrivation_price)
            price *= price_dataset.loc[np.argwhere(price_dataset["Time"] == time_converted)[0, 0], pair[1]]
            q1 = get_derrivation(df.iloc[i], derrivation_quantity)
            q2 = get_derrivation(df.iloc[i], derrivation_quantity_2)
            
            #print(time_converted, pair, side.lower(), price, q1, q2)
            if "Time" not in trade_dataset or time_converted not in list(trade_dataset["Time"]):
                new_row = pd.Series({"Time": time_converted, f"{pair[0]}":q1 if side.lower() == "buy" else -q1
                                                            , f"{pair[1]}":-q2 if side.lower() == "buy" else q2,
                                    "realized_profit": q1*price if side.lower() == "sell" else 0})
                # TODO cost of deposits or trades? FIFO uff uff uff ...  simplification mining: 0 costs of deposit trades are always in 1 year
                trade_dataset = append_row(trade_dataset, new_row)
            else:
                if pair[0] not in trade_dataset.columns:
                    trade_dataset[pair[0]] = 0
                if pair[1] not in trade_dataset.columns:
                    trade_dataset[pair[1]] = 0
                trade_dataset.fillna(0, inplace=True)
                trade_dataset.loc[np.argwhere(trade_dataset["Time"] == time_converted)[0, 0], pair[0]] += q1 if side.lower() == "buy" else -q1
                trade_dataset.loc[np.argwhere(trade_dataset["Time"] == time_converted)[0, 0], pair[1]] += -q2 if side.lower() == "buy" else q2
                
                trade_dataset.loc[np.argwhere(trade_dataset["Time"] == time_converted)[0, 0], "realized_profit"] += q1*price if side.lower() == "sell" else 0

price_dataset.sort_values(by="Time", inplace=True)
price_dataset = price_dataset.set_index("Time") 
#print(price_dataset)       
   
deposit_dataset.sort_values(by="Time", inplace=True)
deposit_dataset = deposit_dataset.set_index("Time")

deposit_euro = deposit_dataset.mul(price_dataset)
deposit_euro.dropna(how='all',axis=0, inplace=True)
deposit_euro["sum"] = deposit_euro.sum(axis=1)


trade_dataset.sort_values(by="Time", inplace=True)
trade_dataset = trade_dataset.set_index("Time")
#print(trade_dataset)

together = deposit_dataset.add(trade_dataset, fill_value=0.0)
together.fillna(0, inplace=True)
#print(together)

cum_sum_columns = list(together.columns)
#print(cum_sum_columns)
together[cum_sum_columns] = together[cum_sum_columns].cumsum()
cum_sum_euro = together.mul(price_dataset)
cum_sum_euro.dropna(how='all',axis=0, inplace=True)
cum_sum_euro["sum"] = cum_sum_euro.sum(axis=1)


#print(deposit_euro["sum"])
deposit_euro["cum_sum"] = deposit_euro["sum"].cumsum()
#print(deposit_euro["cum_sum"])
#print(together["realized_profit"])
#print(cum_sum_euro["sum"])

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
start_date = st.date_input('Start date', today)
end_date = st.date_input('End date', tomorrow)

if start_date < end_date:
    st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.error('Error: End date must fall after start date.')
    
fig = make_subplots(rows=1, cols=1)
fig.add_trace(go.Bar(x=deposit_euro["sum"].index, y=deposit_euro["sum"], name="Deposit"), row=1, col=1)
fig.add_trace(go.Scatter(x=deposit_euro["cum_sum"].index, y=deposit_euro["cum_sum"], mode="lines", name="Cummulated Deposits"), row=1, col=1)
fig.add_trace(go.Scatter(x=together["realized_profit"].index, y=together["realized_profit"], mode="lines", name="realized Gains"), row=1, col=1)
fig.add_trace(go.Scatter(x=cum_sum_euro["sum"].index, y=cum_sum_euro["sum"], mode="lines", name="Portfolio"), row=1, col=1)
st.plotly_chart(fig)


'''
date_now = datetime.datetime.now().strftime("%d/%m/%Y")
if date_now not in list(df["Time"]):
    new_row = pd.Series({"Time":date_now,"kWh":0})
    df = append_row(df, new_row)
else:
    df[f"kWh"][(df["Time"] == date_now)] += 0
    df[f"Product_Day"][(df["Time"] == date_now)] += 0
df.to_csv(f"dataset/{0}/{0}.txt", sep=",", index=False)'''

