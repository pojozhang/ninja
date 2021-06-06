import argparse
import configparser
import logging
import logging.config
import backtrader as bt
from backtrader.dataseries import TimeFrame
import pandas as pd
from backtest.context import Context
from backtest.proxy import Proxy
from utils import print_json, parse_args

cp = configparser.ConfigParser()
cp.read("config.ini")
appConfig = cp

logging.config.fileConfig('log.conf')

logger = logging.getLogger(__name__)


def build_context(args):
    return Context(args=args, trader=None)


if __name__ == '__main__':
    commonParser = argparse.ArgumentParser(add_help=False)
    commonParser.add_argument('--csv', type=str, help='read csv file')
    commonParser.add_argument('--csv-delimiter', default=',', type=str, help='csv delimiter', dest='csvDelimiter')

    strategyParser = argparse.ArgumentParser(description='Start back test.', parents=[commonParser])
    strategyParser.add_argument('--strategy', dest='strategy', type=str, nargs='?',
                                help='choose a strategy to test')

    args, unknown = strategyParser.parse_known_args()
    strategy_args = {parse_args(k): v for k, v in zip(unknown[::2], unknown[1::2])}
    logger.info(f'Test [{args.strategy}] strategy with args:')
    print_json(strategy_args)

    strategy = __import__(f'strategy.{args.strategy}', fromlist=True)

    context = build_context(strategy_args)
    instance = getattr(strategy, 'create')(context)

    dataframe = pd.read_csv(args.csv, sep=args.csvDelimiter)

    cerebro = bt.Cerebro()
    cerebro.addstrategy(Proxy, args={
        'strategy': instance
    })
    cerebro.adddata(bt.feeds.PandasData(dataname=dataframe, timeframe=TimeFrame.Minutes, compression=5))
    cerebro.broker.setcash(100)
    logger.info(cerebro.broker.getvalue())
    cerebro.run()
    logger.info(cerebro.broker.getvalue())
