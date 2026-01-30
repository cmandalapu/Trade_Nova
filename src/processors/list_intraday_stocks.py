import requests
import json
from utils.common_utils.config_loader import load_config
from utils.common_utils.services import *
import pandas as pd
from pathlib import Path
import os,io
from SmartApi import SmartConnect
from datetime import date,datetime, timedelta
import zipfile
from nsepython import *
import numpy as np 


config = load_config()

def download_master_json():
    response = requests.get(config["api_urls"]["master_json"], timeout=30)
    response.raise_for_status()
    return response.json()

def get_last_trading_day(cm_holiday_dates):    
    today = date.today()
    d = today - timedelta(days=1)  
    while d.weekday() >= 5 or d in cm_holiday_dates:
        d -= timedelta(days=1)
    return d.strftime("%d-%m-%Y")

def last_n_trading_days(n,cm_holiday_dates):    
    curr_date = datetime.datetime.today().date()
    holidays = cm_holiday_dates
    trading_days = []

    while len(trading_days) < n:
        curr_date -= timedelta(days=1)

        # skip weekends
        if curr_date.weekday() >= 5:
            continue

        # skip NSE holidays
        if curr_date in holidays:
            continue

        trading_days.append(curr_date)
    trading_days = [i.strftime("%d-%m-%Y") for i in trading_days]
    return trading_days

def load_nse_bhavcopy():
    cm_holiday_dates = cash_market_holiday_list()
    # dt = get_last_trading_day(cm_holiday_dates) #additional functionality
    last_n_dates = last_n_trading_days(config["atr_strategy_params"]["atr_%check_days"],cm_holiday_dates)
    dfs = []
    for i in last_n_dates:
        df = get_bhavcopy(i)  # DD-MM-YYYY
        df.columns = (df.columns.str.strip().str.lower())
        df = df[df["series"].str.strip()=='EQ']
        dfs.append(df)
    final_df = pd.concat(dfs, ignore_index=True)
    final_df_ordered = final_df.sort_values(by=["date1"],ascending=[True])

    return final_df_ordered 


def filter_nse_stocks(data):
    filtered = [
        {
            "symbol": item.get("symbol"),
            "name": item.get("name"),
            "token": item.get("token"),
            "exchange": item.get("exch_seg"),
            "instrument_type": item.get("instrumenttype"),
            "lot_size": item.get("lotsize"),
            "strike_price" : float(item.get("strike", 0)) #this return value as -1 for EQ and Futures, it returns values for options
        }
        for item in data
        if item.get("exch_seg") == "NSE"
        and item.get("symbol").endswith("-EQ")
    ]
    
    return filtered 

def filter_stocks_based_on_price(nse_equity_stocks,nse_stocks_close_price):
    lower_limit = config["atr_strategy_params"]["stock_min_price"]
    upper_limit = config["atr_strategy_params"]["stock_max_price"]
    df_nse_stocks = pd.DataFrame(nse_equity_stocks)
    df_nse_closed_price = nse_stocks_close_price[(nse_stocks_close_price["close_price"]>=lower_limit) & (nse_stocks_close_price["close_price"]<=upper_limit)]
    df_nse_stocks['name'] = df_nse_stocks['name'].str.strip().str.upper()
    #df_nse_closed_price['symbol'] 
    df_nse_closed_price.loc[:, 'symbol']= df_nse_closed_price['symbol'].str.strip().str.upper()
    final_df = pd.merge(df_nse_stocks,df_nse_closed_price,how='inner',left_on='name',right_on='symbol')[["date1","name","token","close_price"]]
    return final_df
        


def save_to_excel(df):
    folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..","..","..",config["output_file_names"]["atr_base_results_folder"],
                     config["output_file_names"]["atr_list_stocks_folder"])
    )
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path,config["output_file_names"]["atr_list_stocks_output"])
    df.sort_values(by="name", inplace=True)
    df.to_excel(file_path, index=False)

def perform_anomoly_detection(lst_stocks_with_price_range):
    distinct_stocks = lst_stocks_with_price_range["name"].unique().tolist()
    output_dfs = []
    
    for i in distinct_stocks:
        data = lst_stocks_with_price_range[lst_stocks_with_price_range["name"]==i]
        ordered_data = data.sort_values(by=["date1"],ascending=[True])
        #Calculate percentage change
        ordered_data['pct_change'] = ordered_data['close_price'].pct_change() * 100
        ordered_data = ordered_data[ordered_data["pct_change"].notna()]
        # Create flag column: 1 if abs(%change) > 1.5%, else 0
        ordered_data['flag'] = np.where(ordered_data['pct_change'].abs() > 1.5, 1, 0)
        if ordered_data["flag"].sum()==0:
            latest_df = ordered_data.tail(1)
            output_dfs.append(latest_df)
    
    final_df = pd.concat(output_dfs, ignore_index=True)
    final_df.rename(columns={'date1': 'recent_traded_date'}, inplace=True) 
    return final_df


def main():
    master_data = download_master_json()
    nse_equity_stocks = filter_nse_stocks(master_data)
    nse_stocks_close_price = load_nse_bhavcopy()
    lst_stocks_with_price_range = filter_stocks_based_on_price(nse_equity_stocks,nse_stocks_close_price)
    final_df = perform_anomoly_detection(lst_stocks_with_price_range)
    save_to_excel(final_df)
    

if __name__ =='__main__':
    main()
