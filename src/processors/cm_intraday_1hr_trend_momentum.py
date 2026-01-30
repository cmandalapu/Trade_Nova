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
import pytz
import time
import sys
import http.client

config = load_config()
api_key_val = config["angelone"]["api_key"]
output_fldr = config["output_file_names"]["atr_base_results_folder"]
atr_list_stocks_fldr = config["output_file_names"]["atr_list_stocks_folder"]
atr_list_stocks_output = config["output_file_names"]["atr_list_stocks_output"]
en_hr = config["atr_strategy_params"] ["entry_hr"]
en_min = config["atr_strategy_params"]["entry_min"]
ex_hr = config["atr_strategy_params"]["exit_hr"]
ex_min = config["atr_strategy_params"]["exit_min"]
mode = config["atr_strategy_params"]["mode"]


def get_smart_api():
    smart = SmartConnect(api_key=api_key_val)
    data = load_login_response()
    smart.setAccessToken(data["data"]["jwtToken"])
    smart.setRefreshToken(data["data"]["refreshToken"])
    return smart

def load_intraday_tradable_stocks():
    folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..","..","..",output_fldr,atr_list_stocks_fldr)
    )
    file_path = os.path.join(folder_path,atr_list_stocks_output)
    df = pd.read_excel(file_path)
    list_tokens = df["token"].to_list()
    return df,list_tokens

def check_window_period(en_hr,en_min,ex_hr,ex_min):
    IST = pytz.timezone("Asia/Kolkata")
    now = datetime.datetime.now(IST)
    target = now.replace(hour=en_hr, minute=en_min, second=0, microsecond=0)
    exit_time = now.replace(hour=ex_hr, minute=ex_min, second=0, microsecond=0)
    status = None
    print(now)
    print(exit_time)

    
    if now >=target and now < exit_time:
        status = "TRUE"

    if now >= exit_time:
        print("❌ Missed execution window. Exiting.")
        status = "FALSE"
    
    if now < target:
        time.sleep((target - now).total_seconds())
        status="TRUE"

    return status
        

def get_payload(list_tokens):
    payLoad = json.dumps({
       
        "exchangeTokens":{
            "NSE":[str(i) for i in list_tokens]
        }
    })

    return payLoad


def get_market_api_data_10_15_am(list_tokens,smart):
    status = check_window_period(en_hr,en_min,ex_hr,ex_min)
    response = None
    if status == "TRUE":
        response = smart.getMarketData(mode=mode,exchangeTokens={"NSE":[str(i) for i in list_tokens]})
    else:
        print("No data has been found ")
    return response
        
def convert_api_data_df(market_api_data):
    if not market_api_data:
        df = pd.DataFrame(market_api_data)
        print(df.head())
def main():
    tradable_stocks,list_tokens = load_intraday_tradable_stocks()
    print(tradable_stocks.head())
    print(list_tokens)
    smart = get_smart_api()
    market_api_data = get_market_api_data_10_15_am(list_tokens,smart)
    market_data_df = convert_api_data_df(market_api_data)
    
if __name__ =='__main__':
    main()