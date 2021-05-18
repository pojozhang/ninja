import okex
from strategy.base import Strategy
from trade import okexConfig
from trade import feishuConfig
import feishu
import utils
import logging

okexClient = okex.Client(okexConfig)
feishuClient = feishu.Client(feishuConfig)
logger = logging.getLogger()


def execute(args):
    rsi = Trend(args)
    rsi.execute()


class Trend(Strategy):

    def __init__(self, args):
        self.instId = args['inst']
        self.growth = float(args['growth'])
        self.ceil = float(args['ceil'])
        self.status = self.init_status()
        self.price = -1
        self.direction = ''

    def execute(self):
        self.init_status()
        while True:
            try:
                candles = self.fetch_candles()
                self.update(candles)
            except Exception as e:
                logger.error(e)
                continue

    def init_status(self):
        return self.wait

    def fetch_candles(self):
        return okexClient.candles(inst_id=self.instId, limit=1)

    def update(self, candles):
        if len(candles) > 0:
            logger.info(candles[0])
            self.status(candles)

    def set_status(self, status):
        self.status = status

    def wait(self, candles):
        candle = candles[0]
        open = float(candle[1])
        close = float(candle[4])
        growth = abs((open - close)) / open * 100
        if growth > self.growth:
            if close < open:
                self.set_status(self.buy_down)
            else:
                self.set_status(self.buy_up)

    def buy_down(self, candles):
        logger.info('buy down')
        ticker = okexClient.ticker(self.instId)
        price = float(ticker['last'])
        text = utils.build_order_message(strategy='trend', price=price, side='做空')
        logging.info(text)
        feishuClient.send_text(text)
        self.price = price
        self.direction = 'down'
        self.set_status(self.wait_for_sell)

    def buy_up(self, candles):
        logger.info('buy up')
        ticker = okexClient.ticker(self.instId)
        price = float(ticker['last'])
        text = utils.build_order_message(strategy='trend', price=price, side='做多')
        logging.info(text)
        feishuClient.send_text(text)
        self.price = price
        self.direction = 'up'
        self.set_status(self.wait_for_sell)

    def wait_for_sell(self, candles):
        candle = candles[0]
        close = float(candle[4])
        if abs(close - self.price) / self.price * 100 <= self.ceil:
            return
        ticker = okexClient.ticker(self.instId)
        price = ticker['last']
        text = utils.build_order_message(strategy='trend', price=price, side='卖出')
        logging.info(text)
        feishuClient.send_text(text)
        self.set_status(self.wait)
