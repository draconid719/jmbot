import time
from datetime import datetime

from .botlog import BotLog


class BotCandlestick(object):
    def __init__(self, period=300, open_price=None, close_price=None, high_price=None, low_price=None,
                 price_average=None, date=None):
        self.current = None
        self.open = open_price
        self.close = close_price
        self.high = high_price
        self.low = low_price
        self.startTime = time.time()
        self.date = date
        self.period = period
        self.output = BotLog()
        self.priceAverage = price_average

    def tick(self, current_price):
        self.current = float(current_price)
        if self.open is None:
            self.open = self.current

        if (self.high is None) or (self.current > self.high):
            self.high = self.current

        if (self.low is None) or (self.current < self.low):
            self.low = self.current

        if time.time() >= (self.startTime + self.period):
            self.close = self.current
            self.priceAverage = (self.high + self.low + self.close) / float(3)

        # self.output.log(
        #     "[" + str(datetime.now()) + "] " + "Open: " + str(self.open) + " Close: " + str(self.close) + " High: " +
        #     str(self.high) + " Low: " + str(
        #         self.low) + " Current: " + str(self.current))

    def is_closed(self):
        if self.close is not None:
            return True
        else:
            return False
