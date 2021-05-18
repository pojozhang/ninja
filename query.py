import argparse
import configparser
import logging.config

import okex
from utils import print_json

cp = configparser.ConfigParser()
cp.read("config.ini")
config = cp['okex']

client = okex.Client(config)


def query_instruments(args):
    print_json(client.instruments(inst_type=args.instType))


def query_ticker(args):
    print_json(client.ticker(inst_id=args.instId))


if __name__ == '__main__':
    logging.config.fileConfig('log.conf')

    parser = argparse.ArgumentParser(description='Query information.')
    subparsers = parser.add_subparsers()

    instruments = subparsers.add_parser("instruments")
    instruments.add_argument('--instType', type=str, default='SPOT', choices=['SPOT', 'SWAP', 'FUTURES', 'OPTION'])
    instruments.add_argument('--uly', type=str)
    instruments.add_argument('--instId', type=str)
    instruments.set_defaults(func=query_instruments)

    ticker = subparsers.add_parser("ticker")
    ticker.add_argument('--instId', type=str)
    ticker.set_defaults(func=query_ticker)

    args = parser.parse_args()
    args.func(args)
