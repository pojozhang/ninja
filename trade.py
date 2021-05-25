import argparse
import configparser
import logging
import logging.config
import okex
from trade.context import Context
from utils import print_json, parse_args

cp = configparser.ConfigParser()
cp.read("config.ini")
appConfig = cp
okexConfig = appConfig['okex']
okexHeadersConfig = dict(appConfig['okex.headers']) if appConfig.has_section('okex.headers') else {}
feishuConfig = appConfig['feishu']


def init_logger():
    logging.config.fileConfig('log.conf')


def build_context(args):
    trader = okex.Client(config=okexConfig, headers=okexHeadersConfig)
    return Context(args=args, trader=trader)


if __name__ == '__main__':
    init_logger()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Start trading.')
    parser.add_argument('--strategy', dest='strategy', type=str, nargs='?', default='rsi',
                        help='choose a strategy to trade')
    predefined_args, unknown_args = parser.parse_known_args()

    args = {parse_args(k): v for k, v in zip(unknown_args[::2], unknown_args[1::2])}
    logger.info(f'Run [{predefined_args.strategy}] strategy with args:')
    print_json(args)

    strategy = __import__(f'strategy.{predefined_args.strategy}', fromlist=True)
    context = build_context(args)
    instance = getattr(strategy, 'create')(context)
    instance.run()
