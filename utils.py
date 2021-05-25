import json
import datetime
import textwrap
import logging

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
