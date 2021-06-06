import backtrader as bt


class Proxy(bt.Strategy):

    def __init__(self, args):
        super().__init__()
        self.strategy = args['strategy']

    def next(self):
        print('66')
