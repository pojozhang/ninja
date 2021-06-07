import argparse
import configparser
import logging
import logging.config
import backtrader as bt
from backtrader.dataseries import TimeFrame
import pandas as pd
from backtest.context import Context
from backtest.proxy import Proxy
from backtest.data import CSVData
from utils import print_json, parse_args
from datetime import datetime

cp = configparser.ConfigParser()
cp.read("config.ini")
appConfig = cp

logging.config.fileConfig('log.conf')

logger = logging.getLogger(__name__)


def dateparse(x):
    return datetime.utcfromtimestamp(int(x) / 1000).strftime('%Y-%m-%d %H:%M:%S')


def build_context(args):
    return Context(args=args, trader=None)


if __name__ == '__main__':
    commonParser = argparse.ArgumentParser(add_help=False)
    commonParser.add_argument('--csv', type=str, help='read csv file')
    commonParser.add_argument('--reverse', action=argparse.BooleanOptionalAction, default=False,
                              help='reverse csv data')
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

    cerebro = bt.Cerebro(stdstats=False)
    cerebro.addstrategy(Proxy, args={
        'strategy': instance
    })
    datapath = (args.csv)

    dataframe = pd.read_csv(
        args.csv,
        parse_dates=True,
        date_parser=dateparse,
        index_col='datetime',
    )

    if args.reverse:
        dataframe[:] = dataframe[::-1]

    data = CSVData(dataname=dataframe,
                   nocase=True,
                   timeframe=TimeFrame.Minutes)
    cerebro.adddata(data)
    cerebro.broker.setcash(100)
    logger.info(cerebro.broker.getvalue())
    result = cerebro.run()
    logger.info(cerebro.broker.getvalue())
