import logging

from strategy.base import Strategy

logger = logging.getLogger()


def create(context):
    return Trend(context)


class Trend(Strategy):
    states = ['init', 'watch', 'order_long', 'order_short', 'guard_long', 'guard_short', 'sell']
    transitions = [
        {'trigger': 'watch', 'source': 'init', 'dest': 'watch', 'after': 'on_watch'},
        {'trigger': 'order_long', 'source': 'watch', 'dest': 'order_long', 'after': 'on_order_long'},
        {'trigger': 'order_short', 'source': 'watch', 'dest': 'order_short', 'after': 'on_order_short'},
        {'trigger': 'guard_long', 'source': ['init', 'order_long'], 'dest': 'guard_long', 'after': 'on_guard_long'},
        {'trigger': 'guard_short', 'source': ['init', 'order_short'], 'dest': 'guard_short',
         'after': 'on_guard_short'},
        {'trigger': 'sell', 'source': ['guard_long', 'guard_short'], 'dest': 'sell', 'after': 'on_sell'},
        {'trigger': 'deal', 'source': 'sell', 'dest': 'watch', 'after': 'on_watch'},
    ]

    def __init__(self, context):
        super().__init__(context, 'init', Trend.states, Trend.transitions)
        self.instId = self.args['inst']
        self.volume = self.args['volume']
        self.growth = float(self.args['growth'])
        self.ceil = float(self.args['ceil'])

    def run(self):
        self.next('watch')

    def on_watch(self):
        while self.context.active:
            candles = self.context.get_candles(inst_id=self.instId, limit=1)
            if len(candles) == 0:
                continue
            candle = candles[0]
            logger.info(candle)
            open = float(candle[1])
            close = float(candle[4])
            growth = abs((close - open)) / open * 100
            if growth > self.growth:
                if close < open:
                    self.next('order_short')
                else:
                    self.next('order_long')
                break

    def on_order_long(self):
        ticker = self.context.get_ticker(inst_id=self.instId)
        logger.info(ticker)
        price = float(ticker['last'])
        self.context.place_order(inst_id=self.instId, trade_mode='cross', price=price, side='buy',
                                 position_side='long', order_type='limit', volume=self.volume)
        self.next('guard_long', price)

    def on_order_short(self):
        ticker = self.context.get_ticker(inst_id=self.instId)
        logger.info(ticker)
        price = float(ticker['last'])
        self.context.place_order(inst_id=self.instId, trade_mode='cross', price=price, side='buy',
                                 position_side='short', order_type='limit', volume=self.volume)
        self.next('guard_short', price)

    def on_guard_long(self, price):
        while self.context.active:
            ticker = self.context.get_ticker(inst_id=self.instId)
            logger.info(ticker)
            current_price = float(ticker['last'])
            if abs(price - current_price) / price * 100 <= self.ceil:
                continue
            self.next('sell', current_price)
            break

    def on_guard_short(self, price):
        while self.context.active:
            ticker = self.context.get_ticker(inst_id=self.instId)
            logger.info(ticker)
            current_price = float(ticker['last'])
            if abs(price - current_price) / price * 100 <= self.ceil:
                continue
            self.next('sell', current_price)
            break

    def sell(self, price):
        self.context.place_order(inst_id=self.instId, trade_mode='cross', price=price, side='sell',
                                 order_type='limit', volume=self.volume)
        self.next('deal')
