import argparse
import configparser
import logging.config
from exchange import okex
from trade.context import Context
from utils import print_json, parse_args

cp = configparser.ConfigParser()
cp.read("config.ini")
appConfig = cp
okexConfig = appConfig['okex']
okexHeadersConfig = dict(appConfig['okex.headers']) if appConfig.has_section('okex.headers') else {}
feishuConfig = appConfig['feishu']

logging.config.fileConfig('log.conf')

logger = logging.getLogger(__name__)


def build_context(args):
    trader = okex.Client(config=okexConfig, headers=okexHeadersConfig)
    return Context(args=args, trader=trader)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start trading.')
    parser.add_argument('--strategy', dest='strategy', type=str, nargs='?', default='rsi',
                        help='choose a strategy to trade')
    args, unknown = parser.parse_known_args()

    strategy_args = {parse_args(k): v for k, v in zip(unknown[::2], unknown[1::2])}
    logger.info(f'Run [{args.strategy}] strategy with args:')
    print_json(strategy_args)

    strategy = __import__(f'strategy.{args.strategy}', fromlist=True)
    context = build_context(strategy_args)
    instance = getattr(strategy, 'create')(context)
    instance.run()
