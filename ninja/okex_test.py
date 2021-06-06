import configparser
import unittest

from exchange import okex

cp = configparser.ConfigParser()
cp.read("config.ini")
config = cp['okex']


class TestCase(unittest.TestCase):
    def setUp(self):
        pass

    def testF(self):
        client = okex.Client(config)
        client.time()
        data = client.get_instruments()

    def testAccountBalance(self):
        client = okex.Client(config)
        client.get_account_balance()

    def testTicker(self):
        client = okex.Client(config)
        client.get_ticker("ETH-USDT-SWAP")

    def testCandles(self):
        client = okex.Client(config)
        data = client.get_candles(inst_id="ETH-USDT-SWAP", limit="100")

        import numpy as np
        a=np.empty([0,4])
        a=np.append(a,[[1,2]],axis=0)
        a=np.append(a,[[3,4]],axis=0)
        print(a)
        # print(jsonpath.jsonpath(data, '$..open'))

        # print(jsonpath.jsonpath(json.loads(json.dumps(data, default=vars)), '$..open'))

        if __name__ == '__main__':
            unittest.main()
