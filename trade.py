import argparse
import configparser
import logging
import logging.config
import okex
from strategy.base import run
from context import TradeContext
from utils import print_json

cp = configparser.ConfigParser()
cp.read("config.ini")
appConfig = cp
okexConfig = appConfig['okex']
feishuConfig = appConfig['feishu']


def parse_strategy_args(kv):
    if kv.startswith('--'):
        kv = kv[2:]
    return kv


def init_logger():
    logging.config.fileConfig('log.conf')


def build_context(args):
    trader = okex.Client(okexConfig)
    return TradeContext(args=args, trader=trader)


if __name__ == '__main__':
    init_logger()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Start trading.')
    parser.add_argument('--strategy', dest='strategy', type=str, nargs='?', default='rsi',
                        help='choose a strategy to trade')
    args, unknown = parser.parse_known_args()

    strategy_args = {parse_strategy_args(k): v for k, v in zip(unknown[::2], unknown[1::2])}
    logger.info(f'Run [{args.strategy}] strategy with args:')
    print_json(strategy_args)

    strategy = __import__(f'strategy.{args.strategy}', fromlist=True)
    context = build_context(strategy_args)
    instance = getattr(strategy, 'create')(context)
    run(instance)
