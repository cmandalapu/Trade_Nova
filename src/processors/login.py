import http.client
import json
from utils.common_utils.config_loader import load_config
from utils.common_utils.services import *
import pyotp

config = load_config()
def login():

    payload = {
        "clientcode": config["angelone"]["client_code"],
        "password": config["angelone"]["client_pin"],  
        "state": config["app"]["state"]
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": config["network"]["client_local_ip"],
        "X-PrivateKey": config["angelone"]["api_key"],
    }
    payload["totp"] = pyotp.TOTP(config["angelone"]["totp_base_tocken"]).now()
    headers["X-ClientPublicIP"] = get_public_ip()
    headers["X-MACAddress"] = get_mac_address()
    conn = http.client.HTTPSConnection(config["api_urls"]["angelone_base_endpoint"])
    conn.request(
        config["api_methods"]["POST"],
        config["api_urls"]["login_url"],
        body=json.dumps(payload),
        headers=headers
    )

    res = conn.getresponse()
    store_login_response(res)
    return res

if __name__ =='__main__':
    login()