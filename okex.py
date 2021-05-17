import base64
import hmac
import json
from datetime import datetime
from hashlib import sha256

import requests


class Client:
    def __init__(self, config={}):
        self.apiKey = config["apiKey"]
        self.apiSecret = config["apiSecret"]
        self.passphrase = config["passphrase"]
        self.rest = config["rest"]
        self.env = config["env"]

    def instruments(self, inst_type="SWAP"):
        data = self.send_request("/api/v5/public/instruments", params={"instType": inst_type})
        return data

    def ticker(self, inst_id):
        data = self.send_request("/api/v5/market/ticker", params={"instId": inst_id})
        return data[0]

    def candles(self, inst_id, before="", after="", bar="15m", limit=""):
        data = self.send_request("/api/v5/market/candles",
                                 params={"instId": inst_id, "before": before,
                                         "after": after, "bar": bar,
                                         "limit": limit})
        return data

    def account_balance(self, ccy=''):
        data = self.send_request("/api/v5/account/balance")
        return data

    def time(self):
        data = self.send_request("/api/v5/public/time")
        return data[0]['ts']

    def send_request(self, path, params={}):
        timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
        headers = {
            "x-simulated-trading": "1" if self.env == "sim" else "0",
            "OK-ACCESS-KEY": self.apiKey,
            "OK-ACCESS-SIGN": self.sign(timestamp, "GET", path, params, ""),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase
        }
        r = requests.get(self.rest + path, headers=headers, params=params)
        body = json.loads(r.text)
        return body['data']

    def sign(self, timestamp, method, path, params={}, body=''):
        if len(params) > 0:
            path += "?"
            for k, v in params.items():
                path += k + "=" + str(v) + "&"
            path = path[:-1]

        return base64.b64encode(
            hmac.new(key=bytes(self.apiSecret, encoding='utf-8'),
                     msg=bytes(timestamp + method + path + body, encoding='utf-8'),
                     digestmod=sha256).digest())
