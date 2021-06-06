import backtrader as bt


class Context:

    def __init__(self, args, trader, listener=None):
        self.args = args
        self.trader = trader

    def get_candles(self, inst_id, bar, limit=1):
        return self.client.get_candles(inst_id=inst_id, bar=bar, limit=limit)

    def get_ticker(self, inst_id):
        return self.client.get_ticker(inst_id=inst_id)

    def buy(self):
        pass

    def sell(self):
        pass
