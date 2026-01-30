import requests
import uuid
from utils.common_utils.config_loader import load_config
import json
import os
from nsepython import *

config = load_config()

def get_public_ip():
    return requests.get(config["api_urls"]["public_ip_url"]).text

def get_mac_address():
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -1, -8))

def store_login_response(response):
    response_body = response.read().decode("utf-8")
    response_body = json.loads(response_body)
    folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..","..","..","..",'API_Response')
    )
    os.makedirs(folder_path, exist_ok=True)
    file_path = os.path.join(folder_path,config["output_file_names"]["login_response"])
    with open(file_path, "w") as f:
        json.dump(response_body, f, indent=4)

def load_login_response():
    folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..","..","..","..",'API_Response')
    )
    file_path = os.path.join(folder_path,config["output_file_names"]["login_response"])
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def cash_market_holiday_list():
    holidays = nse_holidays("trading")
    holidays = holidays["CM"]
    cm_holiday_dates = {
    pd.to_datetime(h["tradingDate"], format="%d-%b-%Y").date()
    for h in holidays
    }
    return cm_holiday_dates


def get_common_header(access_token):
    header ={
        'X-PrivateKey': config["angelone"]["api_key"],
        'X-ClientLocalIP': config["network"]["client_local_ip"],
        'X-ClientPublicIP': get_public_ip(),
        'X-MACAddress': get_mac_address(),
        'X-UserType': 'USER',
        'Authorization': 'Bearer {access_token}',
        'Accept': 'application/json',
        'X-SourceID': 'WEB',
        'Content-Type': 'application/json' 
    }

    return header

