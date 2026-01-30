import http.client
import json
from utils.common_utils.config_loader import load_config
from utils.common_utils.services import *


config = load_config()
def logout():

    payload = {
    "clientcode": config["angelone"]["client_code"],
    
    }

    headers = {
        "Authorization": "Bearer",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-UserType": "USER",
        "X-SourceID": "WEB",
        "X-ClientLocalIP": config["network"]["client_local_ip"],
        "X-PrivateKey": config["angelone"]["api_key"],
    }

    headers["X-ClientPublicIP"] = get_public_ip()
    headers["X-MACAddress"] = get_mac_address()
    jwt_token = load_login_response()["data"]["jwtToken"]
    headers["Authorization"]=str(headers["Authorization"])+' '+str(jwt_token)
    conn = http.client.HTTPSConnection(config["api_urls"]["angelone_base_endpoint"])
    conn.request(
        config["api_methods"]["POST"],
        config["api_urls"]["logout_url"],
        body=json.dumps(payload),
        headers=headers
    )

    res = conn.getresponse()
    return res
