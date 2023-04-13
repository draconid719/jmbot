import sys
from .botlog import BotLog
from .telegram import send_telegram_message
from .binanceTrade import BinanceOrder
from .poloniexTrade import PoloniexOrder
from .bittrexTrade import bittrexOrder
from .krakenTrade import krakenOrder
from .bitzTrade import bitzOrder
from .kucoinTrade import kucoinOrder
from .bwTrade import bwOrder
from .huobiproTrade import huobiproOrder
from .ftxTrade import ftxOrder
from .digifinexTrade import digifinexOrder
import json
from datetime import datetime

sys.path.append(".../bot")

exchange_orders = {'binance': BinanceOrder, 'poloniex': PoloniexOrder,
                   'bittrex': bittrexOrder, 'kraken': krakenOrder,
                   'bitz': bitzOrder, 'kucoin': kucoinOrder,
                   'bw': bwOrder, 'huobipro': huobiproOrder,
                   'ftx': ftxOrder, 'digifinex': digifinexOrder}


class BotTrade(object):
    def __init__(self, order_id, exchange, start_time, current_price, pair, amount, paper_trading, author, bot, fee,
                 entry_price=None, exit_price=None, status=None, end_time=None, stop_loss=0):
        self.id = order_id
        self.output = BotLog()
        self.status = "OPEN"
        self.entry_price = current_price
        self.exit_price = ""
        self.pair = pair
        self.amount = amount
        self.fee = fee
        self.g_fees = 0
        self.Profits = []
        self.orders = []
        self.exchange = exchange
        self.start_time = start_time
        self.end_time = ''
        self.author = author
        self.bot = bot
        self.paper_trading = paper_trading

        if current_price is None:
            self.status = status
            self.entry_price = entry_price
            self.exit_price = exit_price
            self.end_time = end_time
        # if (stopLoss):
        self.stop_loss = stop_loss

    # print(self.stopLoss)

    def open(self):
        if self.paper_trading is True or self.exchange is None:
            self.output.log("Trade opened(NOT LIVE)")
        else:
            order = exchange_orders[self.exchange](self.pair, self.amount, self.author).buy_market_order()
            self.output.log(order)
            self.output.log("Trade opened")
            return [order['datetime'], 'buy', order['id'], 'market', order['average'], self.amount,
                    order['fee']['cost'], self.author]

    def close(self, current_price, pair, amount, paper_trading, end_time=None):
        self.status = "CLOSED"
        self.exit_price = current_price
        self.end_time = end_time
        if self.paper_trading is True or self.exchange is None:
            self.output.log("Trade closed(NOT LIVE)")
        else:
            order = exchange_orders[self.exchange](self.pair, self.amount, self.author).sell_market_order()
            self.output.log(order)
            self.output.log("Trade closed")
            self.show_trade()
            return [order['datetime'], 'sell', order['id'], 'market', order['average'], amount,
                    order['fee']['cost'], self.author]
        self.show_trade()

    def tick(self, current_price, end_time=None):
        if self.stop_loss:  # TODO comparison with current_price and stop_loss is correct?
            if current_price < self.stop_loss:
                print(self.stop_loss)
                self.output.log(current_price)
                self.output.log(self.stop_loss)
                self.close(current_price, self.pair, self.amount, self.paper_trading, end_time)

    def show_trade(self):
        trade_status = "Entry Price: " + str(self.entry_price) + "\nStatus: " + str(self.status) + "\nExit Price: " + \
                       str(self.exit_price)

        if self.status == "CLOSED":
            trade_status = trade_status + "\nProfit: "
            if self.exit_price > self.entry_price:
                trade_status = trade_status + " "
            else:
                trade_status = trade_status + " "

            # Calculate total fee
            t_fees = ((float(self.fee) * float(self.amount)) * float(self.entry_price + self.exit_price))
            self.fee = t_fees
            print(self.fee)

            trade_status = trade_status + str(((self.exit_price - self.entry_price) * float(self.amount)) - t_fees)
            if self.exchange is not None and self.author is not None:
                send_telegram_message(self.author, trade_status)

        self.output.log(trade_status)
