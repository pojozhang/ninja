import logging

from strategy.base import Strategy

logger = logging.getLogger()


def create(context):
    return Trend(context)


class Trend(Strategy):

    def __init__(self, context):
        super().__init__(context)
        self.instId = self.args['inst']
        self.volume = self.args['volume']
        self.growth = float(self.args['growth'])
        self.ceil = float(self.args['ceil'])
        self.price = None
        self.goto(self.on_watch)

    def run(self):
        candles = self.context.get_candles(inst_id=self.instId, limit=1)
        if len(candles) == 0:
            return
        logger.info(candles[0])
        self.trigger(candles[0])

    def on_watch(self, data):
        open = float(data[1])
        close = float(data[4])
        growth = abs((close - open)) / open * 100
        if growth > self.growth:
            ticker = self.context.get_ticker(inst_id=self.instId)
            logger.info(ticker)
            price = float(ticker['last'])
            self.price = price
            if close < open:
                self.context.place_order(inst_id=self.instId, trade_mode='cross', price=price, side='buy',
                                         position_side='short', order_type='limit', volume=self.volume)
                self.goto(self.on_guard_short)
            else:
                self.context.place_order(inst_id=self.instId, trade_mode='cross', price=price, side='buy',
                                         position_side='long', order_type='limit', volume=self.volume)
                self.goto(self.on_guard_long)

    def on_guard_long(self, data):
        ticker = self.context.get_ticker(inst_id=self.instId)
        logger.info(ticker)
        current_price = float(ticker['last'])
        if abs(self.price - current_price) / self.price * 100 > self.ceil:
            self.goto(self.on_sell)

    def on_guard_short(self, data):
        ticker = self.context.get_ticker(inst_id=self.instId)
        logger.info(ticker)
        current_price = float(ticker['last'])
        if abs(self.price - current_price) / self.price * 100 > self.ceil:
            self.goto(self.on_sell)

    def on_sell(self, data):
        self.context.place_order(inst_id=self.instId, trade_mode='cross', price=self.price, side='sell',
                                 order_type='limit', volume=self.volume)
        self.goto(self.on_watch)
