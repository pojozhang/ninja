import datetime
import json
import logging
import textwrap
import argparse

logger = logging.getLogger()


def print_json(data):
    logger.info(json.dumps(data, indent=4))


def parse_args(kv):
    if kv.startswith('--'):
        kv = kv[2:]
    return kv


def build_order_message(strategy, price, side):
    return textwrap.dedent(f"""\
    交易策略：{strategy}
    订单价格：{price}
    订单方向：{side}
    触发时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}""")


class KVAction(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        d = getattr(args, self.dest) or {}
        for kv in values:
            try:
                (k, v) = kv.split("=", 2)
            except ValueError as ex:
                raise argparse.ArgumentError(self, f"could not parse argument \"{kv}\" as k=v format")
            d[k] = v
        setattr(args, self.dest, d)