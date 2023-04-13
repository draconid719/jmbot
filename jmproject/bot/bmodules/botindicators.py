import numpy as np
import pandas as pd
import tulipy as ti


class BotIndicators(object):
    def __init__(self):
        pass

    def supportCal(self, dataPoints, period):
        if len(dataPoints) > 1:
            dataPoints = dataPoints[-period:]
            lowest = dataPoints[0]
            for elt in dataPoints:
                if elt < lowest:
                    lowest = elt
            return float(lowest)
        else:
            return 0

    def resistanceCal(self, dataPoints, period):
        if len(dataPoints) > 1:
            dataPoints = dataPoints[-period:]
            highest = dataPoints[0]
            for elt in dataPoints:
                if elt > highest:
                    highest = elt
            return float(highest)
        else:
            return 0

    def movingAverage(self, dataPoints, period):
        if len(dataPoints) > 1:
            return sum(dataPoints[-period:]) / float(len(dataPoints[-period:]))
        else:
            return 0

    def momentum(self, dataPoints, period=14):
        if len(dataPoints) > period - 1:
            return dataPoints[-1] * 100 / dataPoints[-period]

    def EMA(self, prices, period):
        x = np.asarray(prices)
        weights = None
        weights = np.exp(np.linspace(-1., 0., period))
        weights /= weights.sum()

        a = np.convolve(x, weights, mode='full')[:len(x)]
        a[:period] = a[period]
        return a

    def MACD(self, prices, nslow=26, nfast=12):
        if len(prices) < 27:
            return 0, 0, 0
        emaslow = self.EMA(prices, nslow)
        emafast = self.EMA(prices, nfast)
        histogram = emafast - emaslow
        return emaslow[-1], emafast[-1], histogram[-1]

    def RSI(self, prices, period=14):
        if len(prices) > period:
            deltas = np.diff(prices)
            seed = deltas[:period + 1]
            up = seed[seed >= 0].sum() / period
            down = -seed[seed < 0].sum() / period
            rs = up / down
            rsi = np.zeros_like(prices)
            rsi[:period] = 100. - 100. / (1. + rs)

            for i in range(period, len(prices)):
                delta = deltas[i - 1]  # cause the diff is 1 shorter
                if delta > 0:
                    upval = delta
                    downval = 0.
                else:
                    upval = 0.
                    downval = -delta

                up = (up * (period - 1) + upval) / period
                down = (down * (period - 1) + downval) / period
                rs = up / down
                rsi[i] = 100. - 100. / (1. + rs)
            return rsi[-1]
        else:
            return 50  # output a neutral amount until enough prices in list to calculate RSI

    def Stochastic(self, lowlist, highlist, closeprice, period=14, smoothing=3):

        if len(highlist) > 17 and len(lowlist) > 17 and len(closeprice) > 17:
            high = np.array(highlist)
            low = np.array(lowlist)
            close = np.array(closeprice)

            stoch_k, stoch_d = ti.stoch(high, low, close, period, 3, 3)

            return stoch_k[-1], stoch_d[-1]
        else:
            return 50, 50

    def Boll(self, prices, period=20):
        price_array = np.array(prices)
        if len(prices) > period:
            boll = ti.bbands(price_array, period, 2)
            return boll[0][-1], boll[1][-1], boll[2][-1]
        else:
            return 0, 0, 0
