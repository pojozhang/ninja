import argparse
import configparser
import json

from jsonpath import jsonpath
import csv
import numpy as np
import logging.config
from utils import KVAction

from exchange import okex

cp = configparser.ConfigParser()
cp.read("config.ini")
config = cp['okex']

client = okex.Client(config)


def query_instruments(args):
    return client.get_instruments(inst_type=args.instType)


def query_ticker(args):
    return client.get_ticker(inst_id=args.instId)


def query_candles(args):
    candles = client.get_candles(inst_id=args.instId, bar=args.bar, limit=args.limit)
    list = candles
    while len(candles) > 0 and len(list) < args.limit:
        candles = client.get_candles(inst_id=args.instId, bar=args.bar, after=candles[0].timestamp)
        list.extend(candles)
    return list


def write_csv(args, data):
    assert args.csvRow is not None
    with open(args.csv, 'w') as file:
        expressions = args.csvRow.split(',')
        jsonobj = json.loads(json.dumps(data, default=vars))
        array = None
        for i, expression in enumerate(expressions):
            if array is None:
                array = np.array([format_data(jsonpath(jsonobj, expression), i, args.csvRowFormat)], dtype=str)
            else:
                array = np.vstack((array, format_data(jsonpath(jsonobj, expression), i, args.csvRowFormat)))
        array = array.transpose()

        if args.csvHeader is not None:
            array = np.vstack((np.array(args.csvHeader.split(',')), array))
        writer = csv.writer(file, delimiter=args.csvDelimiter)
        writer.writerows(array)


def format_data(data, i, formats={}):
    formats = {int(k): v for k, v in formats.items()}
    if i in formats:
        for j, _ in enumerate(data):
            data[j] = formats[i].format(data[j])
    else:
        for j, _ in enumerate(data):
            data[j] = str(data[j])
    return data


if __name__ == '__main__':
    logging.config.fileConfig('log.conf')
    logger = logging.getLogger(__name__)

    commonParser = argparse.ArgumentParser(add_help=False)
    commonParser.add_argument('--csv', type=str, help='csv file')
    commonParser.add_argument('--csv-row', type=str, help='csv row', dest='csvRow')
    commonParser.add_argument('--csv-row-format', nargs='+', action=KVAction, help='csv row format',
                              dest='csvRowFormat', default={})
    commonParser.add_argument('--csv-header', type=str, help='csv header', dest='csvHeader')
    commonParser.add_argument('--csv-delimiter', type=str, default=',', help='csv delimiter', dest='csvDelimiter')

    queryParser = argparse.ArgumentParser(description='Query information.')
    subparsers = queryParser.add_subparsers()

    instrumentParser = subparsers.add_parser("instruments", parents=[commonParser])
    instrumentParser.add_argument('--inst-type', type=str, default='SPOT',
                                  choices=['SPOT', 'SWAP', 'FUTURES', 'OPTION'], dest='instType')
    instrumentParser.add_argument('--uly', type=str)
    instrumentParser.add_argument('--inst', type=str, dest='instId')
    instrumentParser.set_defaults(func=query_instruments)

    tickerParser = subparsers.add_parser("ticker", parents=[commonParser])
    tickerParser.add_argument('--inst', type=str, dest='instId')
    tickerParser.set_defaults(func=query_ticker)

    candleParser = subparsers.add_parser("candles", parents=[commonParser])
    candleParser.add_argument('--bar', type=str, default='15m',
                              choices=['1m', '3m', '5m', '15m', '30m',
                                       '1H', '2H', '4H', '6H', '12H',
                                       '1D', '1W', '1M', '3M', '6M', '1Y'])
    candleParser.add_argument('--inst', type=str, dest='instId')
    candleParser.add_argument('--limit', type=int, default=100)
    candleParser.set_defaults(func=query_candles)

    args, _ = queryParser.parse_known_args()
    data = args.func(args)

    if args.csv:
        write_csv(args, data)
    else:
        logger.info(json.dumps(data, default=vars, indent=4))
