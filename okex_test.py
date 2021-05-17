import unittest
import okex
import configparser

cp = configparser.ConfigParser()
cp.read("config.ini")
config = cp['okex']


class TestCase(unittest.TestCase):
    def setUp(self):
        print("1")

    def testF(self):
        client = okex.Client(config)
        client.time()
        client.instruments()

    def testAccountBalance(self):
        client = okex.Client(config)
        client.account_balance()

    def testTicker(self):
        client = okex.Client(config)
        client.ticker("ETH-USDT-SWAP")

    def testCandles(self):
        client = okex.Client(config)
        client.candles(inst_id="ETH-USDT-SWAP", limit="1")


if __name__ == '__main__':
    unittest.main()
