import okex
from strategy.base import Strategy
from trade import okexConfig
from trade import feishuConfig
import feishu
import utils

okexClient = okex.Client(okexConfig)
feishuClient = feishu.Client(feishuConfig)


def execute(args):
    rsi = Trend(args)
    rsi.execute()


class Trend(Strategy):

    def __init__(self, args):
        self.instId = args['inst']
        self.growth = float(args['growth'])
        self.status = self.init_status()

    def execute(self):
        self.init_status()
        while True:
            try:
                candles = self.fetch_candles()
                self.update(candles)
            except Exception as e:
                print(e)
                continue

    def init_status(self):
        return self.wait

    def fetch_candles(self):
        return okexClient.candles(inst_id=self.instId, limit=1)

    def update(self, candles):
        self.status(candles)

    def set_status(self, status):
        self.status = status

    def wait(self, candles):
        if len(candles) == 0:
            return

        candle = candles[0]
        print(candle)
        open = float(candle[1])
        close = float(candle[4])
        growth = abs((open - close)) / open * 100
        if growth > self.growth:
            if close < open:
                self.set_status(self.buy_down)
            else:
                self.set_status(self.buy_up)

    def buy_down(self, candles):
        print('buy down')
        ticker = okexClient.ticker(self.instId)
        feishuClient.send_text(utils.build_order_message(strategy='trend', price=ticker['last'], side='做空'))

    def buy_up(self, candles):
        print('buy up')
        ticker = okexClient.ticker(self.instId)
        feishuClient.send_text(utils.build_order_message(strategy='trend', price=ticker['last'], side='做多'))
