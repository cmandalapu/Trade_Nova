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

def load_intraday_tradable_stocks():
    folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..","..","..",config["output_file_names"]["atr_base_results_folder"],
                     config["output_file_names"]["atr_list_stocks_folder"])
    )
    file_path = os.path.join(folder_path,config["output_file_names"]["atr_list_stocks_output"])
    df = pd.read_excel(file_path)
    return df

def calculate_per_chng_live_data():
    dt = date.today().strftime("%d-%m-%Y")
    df = get_bhavcopy(dt)  # DD-MM-YYYY
    df.columns = (df.columns.str.strip().str.lower())
    df = df[df["series"].str.strip()=='EQ']
    print(df.head())

def main():
    tradable_stocks = load_intraday_tradable_stocks()
    print(tradable_stocks.head())
    live_data_with_per_chng = calculate_per_chng_live_data()
    
    

if __name__ =='__main__':
    main()