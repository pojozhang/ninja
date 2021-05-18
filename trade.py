import argparse
import configparser
import logging
import logging.config
from utils import print_json

cp = configparser.ConfigParser()
cp.read("config.ini")
appConfig = cp
okexConfig = appConfig['okex']
feishuConfig = appConfig['feishu']


def parse_property(kv):
    if kv.startswith('--'):
        kv = kv[2:]
    return kv


def init_logger():
    logging.config.fileConfig('log.conf')


if __name__ == '__main__':
    init_logger()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='Start trading.')
    parser.add_argument('--strategy', dest='strategy', type=str, nargs='?', default='rsi',
                        help='choose a strategy to trade')
    args, unknown = parser.parse_known_args()
    properties = {parse_property(k): v for k, v in zip(unknown[::2], unknown[1::2])}
    logger.info(f'Run [{args.strategy}] strategy with args:')
    print_json(properties)
    m = __import__(f'strategy.{args.strategy}', fromlist=True)
    getattr(m, 'execute')(properties)
