import sys, getopt
import time
import pprint
import urllib
import requests

from .botchart import BotChart as BC
from .botstrategy import BotStrategy
from .botlog import BotLog
from .botcandlestick import BotCandlestick
from .arbitrage import arbitrageTrade


def live(exchange, pair, amount):
    papertrading = False
    chart = BC(exchange, pair, '5m', None, False)

    strategy = BotStrategy(pair, amount, papertrading)

    candlesticks = []
    developingCandlestick = BotCandlestick()

    while True:
        try:
            developingCandlestick.tick(chart.get_current_price())

        except urllib.error.URLError:
            time.sleep(int(30))
            developingCandlestick.tick(chart.get_current_price())

        except requests.exceptions.ConnectionError:
            time.sleep(int(30))
            developingCandlestick.tick(chart.get_current_price())

        if developingCandlestick.is_closed():
            candlesticks.append(developingCandlestick)
            strategy.tick(developingCandlestick)
            developingCandlestick = BotCandlestick()

        time.sleep(int(30))


live('binance', 'BTC/USDT', 100)
