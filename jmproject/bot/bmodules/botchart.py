import json
import time
import threading
from django.core.cache import cache
from django import db

from .botcandlestick import BotCandlestick
from .observableThread import ObservableThread
from .setting import *
from .tools import unix_milli_to_date


class BotChart(object):
    def __init__(self, exchange, pair, period, startTime, endTime, backtest=True):
        self.pair = pair
        self.period = period
        self.exchange = exchange

        if startTime is not None:
            self.startTime = startTime
            self.endTime = endTime

        self.data = []

        if self.exchange == "poloniex":
            if backtest:
                print(startTime)
                print(endTime)
                exchange_data0 = poloniex.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                                     params={'end': int(endTime / 1000)})
                print(29, exchange_data0)
                for data in exchange_data0:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "bittrex":
            if backtest:

                endTime = str(unix_milli_to_date(endTime).strftime("%Y-%m-%dT%H:%M:%SZ"))

                print(endTime)
                exchange_data1 = bittrex.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                                    params={'endDate': str(endTime)})
                for data in exchange_data1:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "kraken":
            if backtest:

                exchange_data1 = kraken.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                                   params={'end': endTime})
                for data in exchange_data1:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "ftx":
            if backtest:

                exchange_data1 = ftx.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                                params={'end_time': int(endTime) / 1000})
                for data in exchange_data1:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "binance":
            if backtest:

                print(startTime)
                print(endTime)
                exchange_data2 = binance.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                                    params={'endTime': endTime})
                for data in exchange_data2:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "bitz":
            if backtest:

                exchange_data2 = bitz.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                                 limit=100000, params={'endTime': endTime})
                for data in exchange_data2:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "huobipro":
            if backtest:

                exchange_data2 = huobipro.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                                     params={'end-time': int(endTime / 1000)})
                for data in exchange_data2:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "digifinex":
            if backtest:

                exchange_data2 = digifinex.fetchOHLCV(symbol=self.pair, timeframe=self.period,
                                                      since=int(startTime / 1000),
                                                      params={'end_time': int(endTime / 1000)})
                for data in exchange_data2:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "bw":
            if backtest:

                exchange_data2 = bw.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime),
                                               params={'endDateTime': endTime})
                for data in exchange_data2:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

        if self.exchange == "kucoin":
            if backtest:

                exchange_data2 = kucoin.fetchOHLCV(symbol=self.pair, timeframe=self.period, since=int(startTime / 1000),
                                                   params={'endAt': int(endTime / 1000)})
                for data in exchange_data2:
                    if len(data) != 0:
                        weight_ave = ((float(data[4]) + float(data[2]) + float(data[3])) / float(3))
                        self.data.append(
                            BotCandlestick(self.period, data[1], data[4], data[2], data[3], weight_ave, data[0]))

    def get_points(self):
        return self.data

    def get_current_price(self):
        exchange_price = cache.get(f"{self.exchange}_price")
        if exchange_price is None:
            chart_tick()
            time.sleep(5)
            exchange_price = cache.get(f"{self.exchange}_price")
        pair_price = json.loads(exchange_price)[self.pair]['last']

        return pair_price


def chart_tick():
    exchanges = {'binance': binance, 'poloniex': poloniex, 'bittrex': bittrex, 'kraken': kraken, 'ftx': ftx,
                 'bitz': bitz, 'huobipro': huobipro, 'digifinex': digifinex, 'bw': bw, 'kucoin': kucoin}
    cache.clear()
    while True:
        all_threads = threading.enumerate()
        result = [a for a in all_threads if type(a) is ObservableThread and a.name == 't_price']
        if len(result) > 0:
            result[0].stop_event.wait()
        for key in exchanges.keys():
            try:
                last_pair_prices = exchanges[key].fetchTickers()
                cache.set(f"{key}_price", json.dumps(last_pair_prices))
            except Exception as e:
                print(key, e)

        db.connections.close_all()
        time.sleep(5)
