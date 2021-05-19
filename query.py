import argparse
import configparser
import json
import logging.config

import okex

cp = configparser.ConfigParser()
cp.read("config.ini")
config = cp['okex']

client = okex.Client(config)


def query_instruments(args):
    return client.instruments(inst_type=args.instType)


def query_ticker(args):
    return client.ticker(inst_id=args.instId)


def query_candles(args):
    candles = client.candles(inst_id=args.instId, bar=args.bar, limit=args.limit)
    list = candles
    while len(candles) > 0 and len(list) < args.limit:
        candles = client.candles(inst_id=args.instId, bar=args.bar, after=candles[0][0])
        list.extend(candles)
    return list


if __name__ == '__main__':
    logging.config.fileConfig('log.conf')
    logger = logging.getLogger(__name__)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument('--saveas', type=str, help='write data to a file')

    parser = argparse.ArgumentParser(description='Query information.')
    subparsers = parser.add_subparsers()

    instruments = subparsers.add_parser("instruments", parents=[common])
    instruments.add_argument('--instType', type=str, default='SPOT', choices=['SPOT', 'SWAP', 'FUTURES', 'OPTION'])
    instruments.add_argument('--uly', type=str)
    instruments.add_argument('--instId', type=str)
    instruments.set_defaults(func=query_instruments)

    ticker = subparsers.add_parser("ticker", parents=[common])
    ticker.add_argument('--instId', type=str)
    ticker.set_defaults(func=query_ticker)

    candles = subparsers.add_parser("candles", parents=[common])
    candles.add_argument('--bar', type=str, default='15m',
                         choices=['1m', '3m', '5m', '15m', '30m',
                                  '1H', '2H', '4H', '6H', '12H',
                                  '1D', '1W', '1M', '3M', '6M', '1Y'])
    candles.add_argument('--instId', type=str)
    candles.add_argument('--limit', type=int, default=100)
    candles.set_defaults(func=query_candles)

    args = parser.parse_args()
    data = json.dumps(args.func(args), indent=4)

    if args.saveas:
        file = open(args.saveas, 'w')
        file.write(data)
        file.close()
    else:
        logger.info(data)
