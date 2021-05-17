import okex
import schedule
import threading
from strategy.base import Strategy
from trade import okexConfig

client = okex.Client(okexConfig)


def execute(args):
    rsi = Rsi(args)
    rsi.execute()


class Rsi(Strategy):

    def execute(self):
        self.fetch_candles()
        schedule.every(1).seconds.do(self.fetch_candles)

    def fetch_candles(self):
        return client.candles(inst_id=self.args['inst'])
