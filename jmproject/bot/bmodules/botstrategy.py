from .botlog import BotLog
from .botindicators import BotIndicators
from .bottrade import BotTrade
from .tools import unix_milli_to_date
import sys
import json
import ast
from bot.models import Bot
import datetime
from termcolor import colored

sys.path.append("../bot")


class BotStrategy(object):
    def __init__(self, strategy, indicator, numSimulTrades=1, author=None, bot=None, exchange=None, pair=None,
                 amount=0, fee=0, papertrading=None):
        Strategies = {
            'MAcrossover': self.MAcrossover,
            'MAgoldenCross': self.MAgoldenCross,
            'MACDgoldencross': self.MACDgoldencross,
            'RSIsignals': self.RSIsignals,
            'MACDandRSI': self.MACDandRSI,
            'RSIandMACross': self.RSIandMACross,
            'StochSignal': self.StochSignal,
            'Stochcrossover': self.Stochcrossover,
            'MACDandStoch': self.MACDandStoch,
            'StoCrossSignal': self.StoCrossSignal,
            'BollingerBand': self.BollingerBand
        }
        self.output = BotLog()
        self.prices = []
        self.Lows = []
        self.Highs = []
        self.closes = []  # Needed for Momentum Indicator
        self.trades = []
        self.orders = []
        self.currentPrice = ""
        self.currentClose = 0
        self.numSimulTrades = numSimulTrades
        self.indicators = BotIndicators()
        self.pair = pair
        self.date = None
        self.amount = amount
        self.fee = fee
        self.author = author
        self.bot = bot
        self.botindicator = indicator
        self.exchange = exchange
        self.evaluatePositions = Strategies[strategy]
        self.papertrading = papertrading
        self.candlestick = None

    def tick(self, candlestick):
        print(self.bot.name, candlestick.priceAverage)
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        self.prices = self.prices[-30:]
        self.Lows.append(float(candlestick.low))
        self.Lows = self.Lows[-30:]
        self.Highs.append(float(candlestick.high))
        self.Highs = self.Highs[-30:]
        self.currentClose = float(candlestick.close)
        self.closes.append(self.currentClose)
        self.closes = self.closes[-30:]
        self.date = candlestick.date
        self.candlestick = candlestick

        self.output.log(colored(f"{self.bot.name}\t", 'blue') + "Price: " + str(
            candlestick.priceAverage) + "\tMoving Average: " + str(
            self.indicators.movingAverage(self.prices, 25)) + "\tRSI: " + str(
            self.indicators.RSI(self.prices)) + "\tSupport: " + str(
            self.indicators.supportCal(self.Lows, 15)) + "\tResistance: " + str(
            self.indicators.resistanceCal(self.Highs, 15)))

        MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
        self.output.log(
            "MACD line: " + str(MACDline) + "\tMACD signal line: " + str(MACDsignalLine) + "\tMACD histogram: " + str(
                MACDhistogram))

        kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)
        self.output.log("STO-kLine: " + str(kline) + "\tSTO-dline: " + str(dline))

        low, middle, high = self.indicators.Boll(self.prices)
        self.output.log(
            "Bollinger low:" + str(low) + "\tBollinger middle:" + str(middle) + "\tBollinger high:" + str(high))
        # if len(prices) >= 15:
        self.get_data()  # With Bot history from db set self.trades
        self.evaluatePositions()  # evaluate position and If the conditions are satisfied, proceed with the transaction.

    # self.showPositions()

    def RSIsignals(self):
        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            if self.indicators.RSI(self.prices) <= 30:
                self.open_trade()

        for trade in openTrades:
            if self.indicators.RSI(self.prices) >= 70:
                self.close_trade(trade)

    def StochSignal(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)

            if kline <= 20:
                self.open_trade()

        for trade in openTrades:
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)

            if kline >= 80:
                self.close_trade(trade)

    # , stopLoss= self.indicators.supportCal(self.Lows,15)
    def MACDandStoch(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)
            if kline > dline and MACDline > MACDsignalLine and kline >= 50:
                self.open_trade()

        for trade in openTrades:
            MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)
            if kline < dline or MACDline < MACDsignalLine:
                self.close_trade(trade)

    def Stochcrossover(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)
            if kline > dline:
                self.open_trade()

        for trade in openTrades:
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)
            if kline < dline:
                self.close_trade(trade)

    def StoCrossSignal(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)
            if dline < kline <= 20:
                self.open_trade()

        for trade in openTrades:
            kline, dline = self.indicators.Stochastic(self.Lows, self.Highs, self.closes)
            if kline < dline or kline >= 80:
                self.close_trade(trade)

    def MACDandRSI(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
            if MACDline > MACDsignalLine and self.indicators.RSI(self.prices) <= 30:
                self.open_trade()

        for trade in openTrades:
            MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
            if MACDline < MACDsignalLine or self.indicators.RSI(self.prices) >= 70:
                self.close_trade(trade)

    def MACDgoldencross(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
            if MACDline > MACDsignalLine:
                self.open_trade()

        for trade in openTrades:
            MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
            if MACDline < MACDsignalLine:
                self.close_trade(trade)

    def MAcrossover(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)
        ma = self.indicators.movingAverage(self.prices, 9)
        if len(openTrades) < self.numSimulTrades:
            if (self.currentPrice > (1 - self.fee) * ma) and \
                    self.indicators.movingAverage(self.prices, 9) != 0:
                self.open_trade()

        for trade in openTrades:
            if self.currentPrice < (1 + self.fee) * ma:
                self.close_trade(trade)

    def RSIandMACross(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            if (self.indicators.movingAverage(self.prices, 25) > self.indicators.movingAverage(self.prices, 20)) and (
                    self.indicators.RSI(self.prices) <= 30) and self.indicators.movingAverage(self.prices, 25) != 0:
                self.open_trade()

        for trade in openTrades:
            if (self.indicators.movingAverage(self.prices, 25) < self.indicators.movingAverage(self.prices, 20) or (
                    self.indicators.RSI(self.prices) >= 70)):
                self.close_trade(trade)

    def MAgoldenCross(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            mv_l = self.indicators.movingAverage(self.prices, 40)
            mv_m = self.indicators.movingAverage(self.prices, 20)
            mv_s = self.indicators.movingAverage(self.prices, 5)
            cond_1 = mv_l < mv_m < mv_s
            cond_2 = mv_m < mv_l < mv_s
            if (cond_1 or cond_2) and mv_l != 0:
                self.open_trade()

        for trade in openTrades:
            if self.indicators.movingAverage(self.prices, 20) > self.indicators.movingAverage(self.prices, 5):
                self.close_trade(trade)

    def BollingerBand(self):
        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            low, middle, high = self.indicators.Boll(self.prices)
            if self.currentPrice < low != 0:
                self.open_trade()

        for trade in openTrades:
            low, middle, high = self.indicators.Boll(self.prices)
            if self.currentPrice * (1 + self.fee) > high != 0:
                self.close_trade(trade)

    def show_positions(self):
        return self.trades

    def show_orders(self):
        return self.orders

    def get_data(self):
        if self.exchange is not None:
            w_trades = []

            trades = self.bot.orderhistory_set.filter(status="open")
            for trade in trades:
                bot_trade = BotTrade(trade.id, trade.exchange, trade.start_time, None, trade.pair, trade.amount,
                                     trade.paper_trading, self.author, self.bot.name, trade.fee, trade.entry_price,
                                     trade.exit_price, trade.status, trade.end_time)
                try:
                    bot_trade.orders = ast.literal_eval(trade.live_detail)
                except Exception as err:
                    print(err)
                w_trades.append(bot_trade)

            self.trades = w_trades

    def open_trade(self):
        try:
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if self.date is not None:
                now_time = unix_milli_to_date(self.date)
            t = BotTrade(None, self.exchange, now_time, self.currentPrice, self.pair, self.amount, self.papertrading,
                         self.author, self.bot, self.fee)
            o = t.open()

            if o is not None:
                t.start_time = o[0]
                t.entry_price = o[4]
                t.orders.append(o)
                self.orders.append(o)
            else:
                t.start_time = now_time
                t.entry_price = self.currentPrice

            self.trades.append(t)
        except Exception as err:
            print(self.bot.name, ' open trade error ', err)

    def close_trade(self, trade):
        try:
            now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            if self.date is not None:
                now_time = unix_milli_to_date(self.date)
            o = trade.close(self.currentPrice, self.pair, self.amount, self.papertrading, now_time)

            trade.status = 'CLOSE'
            if o is not None:
                trade.end_time = o[0]
                trade.exit_price = o[4]
                trade.orders.append(o)
                self.orders.append(o)
            else:
                trade.exit_price = self.currentPrice
                trade.end_time = now_time

        except Exception as err:
            print(self.bot.name, ' close trade error ', err)
