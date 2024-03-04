import os
from altair import List
import streamlit as st
import datetime
import pandas as pd
import numpy as np


def append_row(df, row):
    return pd.concat([
                df, 
                pd.DataFrame([row], columns=row.index)]
           ).reset_index(drop=True)
    

def derrivation_checker(Series:pd.Series, Type_list: List[str], Check_list: List[str]):
    for type in Type_list:
        for check in Check_list:
            if Series[type] == check:
                return True
    return False

def get_derrivation(Series:pd.Series, Derrivation_List: List[str]) -> str: 
    for derrivation in Derrivation_List:
        try: return Series[derrivation] 
        except KeyError: pass
    raise KeyError


derrivation_type = ["Type"]
derrivation_deposit = ["Deposit"]
derrivation_ticker = ["Symbol", "Ticker"]
derrivation_amount = ["Amount"]
derrivation_time = ["Time"]
derrivation_trade = ["Spot Market"]
derrivation_pairs = ["Market"]
derrivation_side = ["Side"]
derrivation_price = ["Price"]
derrivation_quantity = ["Quantity"]
derrivation_quantity_2 = ["TotalWithFee"]


dict_time_format = {"Xeggex": "%m/%d/%Y, %H:%M:%S %p"}
pairs_str_sep = ["/", "_"]


st.title('My Crypto_Tracker')

deposit_dataset = pd.Series({})
trade_dataset = pd.Series({})
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
                deposit_dataset[ticker][(deposit_dataset["Time"] == time_converted)] = amount
            else:  # time and ticker are already there
                deposit_dataset[ticker][(deposit_dataset["Time"] == time_converted)] += amount
        elif derrivation_checker(df.iloc[i], derrivation_type, derrivation_trade):
            time = get_derrivation(df.iloc[i], derrivation_time)
            pair = get_derrivation(df.iloc[i], derrivation_pairs)
            side = get_derrivation(df.iloc[i], derrivation_side)
            for sep in pairs_str_sep:
                if len(pair.split(sep)) != 1:
                    pair = pair.split(sep)
            price = get_derrivation(df.iloc[i], derrivation_price)
            q1 = get_derrivation(df.iloc[i], derrivation_quantity)
            q2 = get_derrivation(df.iloc[i], derrivation_quantity_2)
            if "Time" not in deposit_dataset or time_converted not in list(deposit_dataset["Time"]):
                new_row = pd.Series({"Time": time_converted, f"{pair[0]}":q1 if side.lower == "buy" else -q1
                                                            , f"{pair[1]}":-q2 if side.lower == "buy" else q2},
                                    "")
                # TODO cost of deposits or trades? FIFO uff uff uff ...
                deposit_dataset = append_row(deposit_dataset, new_row)
            elif ticker not in deposit_dataset.columns:  # date is in pd.Series but ticker not
                #dataset[ticker] = dataset.insert(2, ticker, 0)
                deposit_dataset[ticker] = 0
                deposit_dataset[ticker][(deposit_dataset["Time"] == time_converted)] = amount
            else:  # time and ticker are already there
                deposit_dataset[ticker][(deposit_dataset["Time"] == time_converted)] += amount
            
            
                
'''deposit_dataset.drop(columns=[0], inplace=True)
deposit_dataset.sort_values(by="Time", inplace=True)
cum_sum_columns = list(deposit_dataset.columns)
cum_sum_columns.remove("Time")
print(cum_sum_columns)
deposit_dataset[cum_sum_columns] = deposit_dataset[cum_sum_columns].cumsum()
print(deposit_dataset)'''

    
'''
date_now = datetime.datetime.now().strftime("%d/%m/%Y")
if date_now not in list(df["Time"]):
    new_row = pd.Series({"Time":date_now,"kWh":0})
    df = append_row(df, new_row)
else:
    df[f"kWh"][(df["Time"] == date_now)] += 0
    df[f"Product_Day"][(df["Time"] == date_now)] += 0
df.to_csv(f"dataset/{0}/{0}.txt", sep=",", index=False)'''

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
start_date = st.date_input('Start date', today)
end_date = st.date_input('End date', tomorrow)

if start_date < end_date:
    st.success('Start date: `%s`\n\nEnd date:`%s`' % (start_date, end_date))
else:
    st.error('Error: End date must fall after start date.')