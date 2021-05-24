class TradeContext:

    def __init__(self, args, trader, listener={}):
        self.args = args
        self.trader = trader
        self.listener = listener
        self.active = True

    def get_candles(self, inst_id, bar='15m', limit=1):
        return self.trader.get_candles(inst_id=inst_id, bar=bar, limit=limit)

    def get_ticker(self, inst_id):
        return self.trader.get_ticker(inst_id=inst_id)

    def place_order(self, inst_id, trade_mode, side, position_side, order_type, price, volume):
        self.trader.place_order(inst_id=inst_id, trade_mode=trade_mode, side=side, position_side=position_side,
                                order_type=order_type, price=price, volume=volume)
        if hasattr(self.listener, 'on_place_order'):
            self.listener.on_place_order()

    def before_state_change(self, state):
        if hasattr(self.listener, 'before_state_change'):
            self.listener.before_state_change(state)

    def after_state_change(self, state):
        if hasattr(self.listener, 'after_state_change'):
            self.listener.after_state_change(state)
