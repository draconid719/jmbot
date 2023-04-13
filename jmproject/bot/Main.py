import sys, getopt
import time
import pprint
import urllib
import requests

from .bmodules.botchart import BotChart
from .bmodules.botstrategy import BotStrategy
from .bmodules.botlog import BotLog
from .bmodules.botcandlestick import BotCandlestick
from .bmodules.arbitrage import ArbitrageTrade


def backtesting(start_time, end_time, amount, candle_size, author, bot, exchange, strategy, simTrade, pair, indicator):
    total = 0
    tradePrice = []
    chart = BotChart('binance', pair, candle_size, start_time, end_time)

    strategy = BotStrategy(strategy, indicator, simTrade, author, bot)

    for candlestick in chart.get_points():
        strategy.tick(candlestick)

    trades = strategy.show_positions()
    # print(trades)
    for trade in trades:
        if trade.exit_price != '' and trade.entry_price != '':
            total += float(trade.exit_price) - float(trade.entry_price)
            subtotal = []
            subtotal.append('')
            subtotal.append(round(trade.entry_price, 8))
            tradePrice.append(subtotal)
            subtotal = []
            subtotal.append('')
            subtotal.append(round(trade.exit_price, 8))
            tradePrice.append(subtotal)
    trnum = len(trades)
    return total, trnum, tradePrice, trades


class live(object):
    def __init__(self, exchange, pair, amount):
        self.exchange = exchange
        self.pair = pair
        self.amount = amount
        self.trade = []

    def slive(self):
        papertrading = False
        chart = BotChart(self.exchange, self.pair, '5m', None, False)

        strategy = BotStrategy(self.pair, self.amount, papertrading)

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

            if (developingCandlestick.is_closed()):
                candlesticks.append(developingCandlestick)
                strategy.tick(developingCandlestick)
                developingCandlestick = BotCandlestick()

            self.trades = strategy.show_positions()
            time.sleep(int(30))

    def get_live_data(self):

        # whole_data = []
        # for trade in trades:
        #	subdata = []
        #	date = trade.timenow
        #	subdata.append(date)
        #	entryPrice = trade.entryPrice
        #	subdata.append(entryPrice)
        #	exitPrice = trade.exitPrice
        #	subdata.append(exitPrice)
        #	pair = trade.pair
        #	subdata.append(pair)

        #	whole_data.append(subdata)

        return self.trades
