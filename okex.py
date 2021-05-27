import base64
import hmac
import json
from datetime import datetime
from hashlib import sha256
from ratelimit import limits, sleep_and_retry
from exchange.model import Candle

import requests


class Client:
    def __init__(self, config={}, headers={}):
        self.apiKey = config["apiKey"]
        self.apiSecret = config["apiSecret"]
        self.passphrase = config["passphrase"]
        self.rest = config["rest"]
        self.headers = headers

    @sleep_and_retry
    @limits(calls=10, period=1)
    def get_instruments(self, inst_type="SWAP"):
        data = self.send_request("/api/v5/public/instruments", params={"instType": inst_type})
        return data

    @sleep_and_retry
    @limits(calls=10, period=1)
    def get_ticker(self, inst_id):
        data = self.send_request("/api/v5/market/ticker", params={"instId": inst_id})
        return data[0]

    @sleep_and_retry
    @limits(calls=10, period=1)
    def get_candles(self, inst_id, before="", after="", bar="15m", limit=""):
        data = self.send_request("/api/v5/market/candles",
                                 params={"instId": inst_id, "before": before,
                                         "after": after, "bar": bar,
                                         "limit": limit})
        return list(map(lambda x: Candle(timestamp=int(x[0]), open=float(x[1]), high=float(x[2]), low=float(x[3]),
                                         close=float(x[4]), volume=float(x[5])), data))

    @sleep_and_retry
    @limits(calls=10, period=2)
    def get_account_balance(self, ccy=''):
        data = self.send_request("/api/v5/account/balance")
        return data

    @sleep_and_retry
    @limits(calls=60, period=2)
    def place_order(self, inst_id, trade_mode, side, position_side, order_type, price, volume):
        print('place order')
        # data = self.send_request("/api/v5/trade/order")
        # return data

    @sleep_and_retry
    @limits(calls=10, period=2)
    def time(self):
        data = self.send_request("/api/v5/public/time")
        return data[0]['ts']

    def send_request(self, path, params={}):
        timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
        headers = {
                      "OK-ACCESS-KEY": self.apiKey,
                      "OK-ACCESS-SIGN": self.sign(timestamp, "GET", path, params, ""),
                      "OK-ACCESS-TIMESTAMP": timestamp,
                      "OK-ACCESS-PASSPHRASE": self.passphrase
                  } | self.headers
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
