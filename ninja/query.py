import configparser
import csv
import json
import logging.config

import nestargs
import numpy as np
import pandas as pd
import yaml
from dpath.util import get as pget
from jsonpath import jsonpath

from exchange import okex
from utils import SubArgsAction, StrListAction

cp = configparser.ConfigParser()
cp.read("config.ini")
config = cp['okex']

client = okex.Client(config)


def query_instruments(args):
    return client.get_instruments(inst_type=args.instType)


def query_ticker(args):
    return client.get_ticker(inst_id=args.instId)


def query_candles(args):
    candles = client.get_candles(inst_id=args['inst'], bar=args['bar'], limit=args['limit'])
    list = candles
    while len(candles) > 0 and len(list) < args['limit']:
        candles = client.get_candles(inst_id=args['inst'], bar=args['bar'], after=candles[0].timestamp)
        list.extend(candles)
    if 'indicators' in args:
        df = pd.DataFrame([vars(c) for c in list])
        for indicator_args in args['indicators']:
            indicator = __import__(f'query.indicator.{indicator_args["name"]}', fromlist=True)
            instance = getattr(indicator, 'create')(indicator_args)
            instance.compute(df)
        print(df)
    return list


def write_csv(args, data):
    with open(args['csv']['file'], 'w') as file:
        expressions = args['csv']['row']
        jsonobj = json.loads(json.dumps(data, default=vars))
        array = None
        for i, expression in enumerate(expressions):
            if array is None:
                array = np.array([format_data(jsonpath(jsonobj, expression), i)], dtype=str)
            else:
                array = np.vstack((array, format_data(jsonpath(jsonobj, expression), i)))
        array = array.transpose()

        if args['csv']['header'] is not None:
            array = np.vstack((np.array(args['csv']['header']), array))
        writer = csv.writer(file, delimiter=pget(args, 'csv.delimiter', separator='.', default=','))
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


def read_yaml(filepath):
    with open(filepath, 'r') as file:
        return yaml.load(file.read(), Loader=yaml.FullLoader)


queryFuncs = {
    'instruments': query_instruments,
    'ticker': query_ticker,
    'candles': query_candles
}


def get_func(api):
    return queryFuncs[api]


if __name__ == '__main__':
    logging.config.fileConfig('log.conf')
    logger = logging.getLogger(__name__)
    commonParser = nestargs.NestedArgumentParser(add_help=False)
    commonParser.add_argument('--csv.file', type=str, help='csv file')
    commonParser.add_argument('--csv.row', action=StrListAction, help='csv row')
    # commonParser.add_argument('--csv.row.format', nargs='+', action=KVAction, help='csv row format',
    #                           dest='csvRowFormat', default={})
    commonParser.add_argument('--csv.header', action=StrListAction, help='csv header')
    commonParser.add_argument('--csv.delimiter', default=',', help='csv delimiter')
    commonParser.add_argument('-f', '--file', type=str, default='', help='read query scheme from a file', dest='file')
    queryParser = nestargs.NestedArgumentParser(description='Query information.', parents=[commonParser])
    subparsers = queryParser.add_subparsers()

    instrumentParser = subparsers.add_parser("instruments", parents=[commonParser])
    instrumentParser.add_argument('--inst-type', type=str, default='SPOT',
                                  choices=['SPOT', 'SWAP', 'FUTURES', 'OPTION'], dest='instType')
    instrumentParser.add_argument('--uly', type=str)
    instrumentParser.add_argument('--inst', type=str, dest='instId')
    instrumentParser.set_defaults(func=get_func('instruments'))

    tickerParser = subparsers.add_parser("ticker", parents=[commonParser])
    tickerParser.add_argument('--inst', type=str, dest='instId')
    tickerParser.set_defaults(func=get_func('ticker'))

    candleParser = subparsers.add_parser("candles", parents=[commonParser])
    candleParser.add_argument('--bar', type=str, default='15m',
                              choices=['1m', '3m', '5m', '15m', '30m',
                                       '1H', '2H', '4H', '6H', '12H',
                                       '1D', '1W', '1M', '3M', '6M', '1Y'])
    candleParser.add_argument('--inst', type=str, dest='inst')
    candleParser.add_argument('--limit', type=int, default=100)
    candleParser.add_argument('--indicator', nargs='*', action=SubArgsAction, dest='indicators')
    candleParser.set_defaults(func=get_func('candles'))

    args, _ = queryParser.parse_known_args()
    if args.file:
        args = read_yaml(args.file)
        data = get_func(args['api'])(args['args'])
    else:
        kvargs = json.loads(json.dumps(args, default=vars))
        data = args.func(kvargs)
        args = kvargs

    if args['csv']:
        write_csv(args, data)
    else:
        logger.info(json.dumps(data, default=vars, indent=4))
