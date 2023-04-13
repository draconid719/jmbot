from .botlog import BotLog
from .botindicators import BotIndicators
from .bottrade import BotTrade
import datetime


class BotStrategy(object):
    def __init__(self, pair=None, amount=0, numSimulTrades=1, papertrading=None):
        self.output = BotLog()
        self.prices = []
        self.Lows = []
        self.Highs = []
        self.closes = []  # Needed for Momentum Indicator
        self.trades = []
        self.currentPrice = ""
        self.currentClose = ""
        self.numSimulTrades = numSimulTrades
        self.indicators = BotIndicators()
        self.pair = pair
        self.amount = amount
        self.papertrading = papertrading

    def tick(self, candlestick):
        self.currentPrice = float(candlestick.priceAverage)
        self.prices.append(self.currentPrice)
        self.Lows.append(float(candlestick.low))
        self.Highs.append(float(candlestick.high))

        # self.currentClose = float(candlestick['close'])
        # self.closes.append(self.currentClose)

        self.output.log("Price: " + str(candlestick.priceAverage) + "\tMoving Average: " + str(
            self.indicators.movingAverage(self.prices, 15)) + "\tSupport: " + str(
            self.indicators.supportCal(self.Lows, 15)) + "\tResistance: " + str(
            self.indicators.resistanceCal(self.Highs, 15)))
        MACDsignalLine, MACDline, MACDhistogram = self.indicators.MACD(self.prices)
        self.output.log(
            "MACD line: " + str(MACDline) + "\tMACD signal line: " + str(MACDsignalLine) + "\tMACD histogram: " + str(
                MACDhistogram))

        # if len(prices) >= 15:
        self.evaluatePositions()
        self.updateOpenTrades()

    # self.showPositions()

    def evaluatePositions(self):

        openTrades = []
        for trade in self.trades:
            if trade.status == "OPEN":
                openTrades.append(trade)

        if len(openTrades) < self.numSimulTrades:
            if (self.currentPrice < self.indicators.movingAverage(self.prices, 15)) and self.indicators.movingAverage(
                    self.prices, 15) != 0:
                timenow = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.trades.append(BotTrade(timenow, self.currentPrice, self.pair, self.amount, self.papertrading,
                                            stopLoss=self.indicators.supportCal(self.Lows, 15)))

        for trade in openTrades:
            if self.currentPrice > self.indicators.movingAverage(self.prices, 15):
                trade.close(self.currentPrice, self.pair, self.amount, self.papertrading)

    def updateOpenTrades(self):
        for trade in self.trades:
            if trade.status == "OPEN":
                trade.tick(self.currentPrice)

    def showPositions(self):
        # for trade in self.trades:
        #	trade.showTrade()
        return self.trades
