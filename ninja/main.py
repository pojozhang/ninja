# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import ccxt  # noqa: E402
import talib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdate
import maya
from exchange import okex


def print_hi(name):
    okex.g()
    # dates = ['01/02/1999', '01/03/1999', '01/04/1999']
    # xs = [datetime.strptime(d, '%m/%d/%Y').date() for d in dates]
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.
    # print(ccxt.binance().fetch_tickers('ETH/USDT'))
    exchange = ccxt.okex({

        'timeout': 30000,
        'enableRateLimit': True,
    })
    exchange.load_markets()
    kline = exchange.fetchOHLCV('ETH/USDT', timeframe='15m', since=1618880000000)
    print(kline)
    upperband, middleband, lowerband = talib.BBANDS(np.array(list(map(lambda k: k[4], kline))),
                                                    timeperiod=20,
                                                    nbdevup=2,
                                                    nbdevdn=2,
                                                    matype=0)
    times = list(map(lambda k: maya.parse(exchange.iso8601(k[0])).datetime(), kline))

    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.xaxis.set_major_formatter(mdate.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdate.AutoDateLocator())

    ax.plot(times, upperband)
    ax.plot(times, middleband)
    ax.plot(times, lowerband)

    plt.print_json()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
