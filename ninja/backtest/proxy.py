import backtrader as bt
from exchange.model import Candle


class Proxy(bt.Strategy):

    def __init__(self, args):
        super().__init__()
        self.strategy = args['strategy']
        self.open = self.datas[0].open
        self.close = self.datas[0].close
        self.high = self.datas[0].high
        self.low = self.datas[0].low

    def next(self):
        candle = Candle(open=self.open[0], close=self.close[0], high=self.high[0], low=self.low[0],
                        volume=0, timestamp=self.data.num2date())
        self.strategy.next(candle)
