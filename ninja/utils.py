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


def to_dict(obj):
    return json.loads(json.dumps(obj, default=vars))


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


class StrListAction(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        setattr(args, self.dest, values.split(",", -1))


class SubArgsAction(argparse.Action):

    def __call__(self, parser, args, values, option_string=None):
        list = getattr(args, self.dest) or []
        d = {'name': values[0]}
        d.update({values[i]: values[i + 1] for i in range(1, len(values), 2)})
        list.append(d)
        setattr(args, self.dest, list)
