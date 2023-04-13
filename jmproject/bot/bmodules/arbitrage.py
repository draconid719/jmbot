from .setting import *
import datetime
from .botlog import BotLog
from .binanceTrade import *
from .poloniexTrade import *
from .bittrexTrade import *
from .krakenTrade import *
from .ftxTrade import *
from .bitzTrade import *
from .huobiproTrade import *
from .digifinexTrade import *
from .kucoinTrade import *
from .bwTrade import *
from .telegram import send_telegram_message


class ArbitrageTrade(object):
    def __init__(self, first_exchange, second_exchange, pair, spread, amount, author, paper='False'):
        self.exchanges = {"binance": binance, "poloniex": poloniex, "bittrex": bittrex,
                          'kraken': kraken, 'ftx': ftx,
                          'bitz': bitz, 'digifinex': digifinex, 'bw': bw,
                          'huobipro': huobipro, 'kucoin': kucoin}

        self.exchangeOrder = {'binance': BinanceOrder, 'poloniex': PoloniexOrder,
                              'bittrex': bittrexOrder, 'kraken': krakenOrder,
                              'bitz': bitzOrder, 'ftx': ftxOrder,
                              'kucoin': kucoinOrder, 'digifinex': digifinexOrder,
                              'bw': bwOrder, 'huobipro': huobiproOrder}
        self.hold = {'binance': BinanceGetAccount,
                     'poloniex': PoloniexGetAccount,
                     'bittrex': bittrexGetaccount,
                     'ftx': ftxGetaccount,
                     'kraken': krakenGetaccount,
                     'bitz': bitzGetaccount,
                     'kucoin': kucoinGetaccount,
                     'digifinex': digifinexGetaccount,
                     'bw': bwGetaccount,
                     'huobipro': huobiproGetaccount}
        self.trades = []
        self.first_exchange = first_exchange
        self.second_exchange = second_exchange
        self.pair = pair
        self.spread = spread
        self.amount = amount
        self.paper = paper
        self.author = author

    def check_market(self):
        try:
            one = self.exchanges[self.first_exchange].fetchTicker(self.pair)['last']
            sec = self.exchanges[self.second_exchange].fetchTicker(self.pair)['last']
            return one, sec
        except:
            print("pair is not available")

    def is_profitable(self, sell_price, buy_price, sell_market, buy_market):
        buy_fee = self.get_fees(buy_market)
        sell_fee = self.get_fees(sell_market)

        if (float(buy_fee) + float(buy_price)) < (float(sell_fee) + float(sell_price)):
            return True, float(buy_fee) + float(sell_fee)
        return False, None

    def have_sufficient(self, exchange, pair, amount, order):

        currency = pair.split('/')

        if order == 'buy':
            cholding, otherholding = self.hold[exchange](pair, self.author).accounthold()
        else:
            currency = currency[::-1]
            coins = '/'.join(currency)
            cholding, otherholding = self.hold[exchange](coins, self.author).accounthold()

        cholding = cholding.replace('₿', '').replace('$', '')
        if float(cholding) >= float(amount):
            return True
        else:
            return False

    def get_fees(self, exchange):

        fees = self.hold[exchange](self.pair, self.author).accountfees()
        fees = float(self.exchanges[exchange].fetchTicker(self.pair)['last']) * (float(self.amount) * float(fees))
        return fees

    def strategy(self, amount, spread, exchange1, market1, exchange2, market2):
        if float(market1) > float(market2) and float(market1) - float(market2) >= float(spread):
            state, fees = self.is_profitable(market1, market2, exchange1, exchange2)
            order1 = self.have_sufficient(exchange1, self.pair, self.amount, 'sell')
            order2 = self.have_sufficient(exchange2, self.pair, self.amount, 'buy')

            if state is True and order1 is True and order2 is True:

                # Place market1 sell order

                if self.paper != 'True':
                    print('sell exchange 1')
                    self.exchangeOrder[exchange1](self.pair, self.amount, self.author).sell_market_order()

                # Place market2 buy order
                if self.paper != 'True':
                    print('buy exchange 2')
                    self.exchangeOrder[exchange2](self.pair, self.amount, self.author).buy_market_order()

                current_trade = []
                current_trade.append(str(datetime.datetime.now()))
                current_trade.append(len(self.trades) + 1)
                current_trade.append(exchange2)
                current_trade.append(market2)
                current_trade.append(exchange1)
                current_trade.append(market1)
                current_trade.append(self.pair)
                current_trade.append(fees)

                self.trades.append(current_trade)
                message = 'Sell Exchange: ' + exchange1 + '\n' + 'Sell Price: ' + str(
                    market1) + '\n' + 'Buy Exchange: ' + exchange2 + '\n' + 'Buy Price: ' + str(
                    market2) + '\n' + 'Profit: ' + str(round((float(market1) - float(market2)) - fees, 2))
                send_telegram_message(self.author, message)

        if float(market2) > float(market1) and float(market2) - float(market1) >= float(spread):
            state, fees = self.is_profitable(market2, market1, exchange2, exchange1)
            order2 = self.have_sufficient(exchange2, self.pair, self.amount, 'sell')
            order1 = self.have_sufficient(exchange1, self.pair, self.amount, 'buy')

            if state is True and order2 is True and order1 is True:
                # Place market2 sell order

                if self.paper != 'True':
                    print('sell exchange 2')
                    self.exchangeOrder[exchange2](self.pair, self.amount).sell_market_order()

                # Place market1 buy order
                if self.paper != 'True':
                    print('buy exchange 1')
                    self.exchangeOrder[exchange1](self.pair, self.amount).buy_market_order()

                current_trade = []
                current_trade.append(str(datetime.datetime.now()))
                current_trade.append(len(self.trades) + 1)
                current_trade.append(exchange1)
                current_trade.append(market1)
                current_trade.append(exchange2)
                current_trade.append(market2)
                current_trade.append(self.pair)
                current_trade.append(fees)

                self.trades.append(current_trade)
                message = 'Sell Exchange: ' + exchange2 + '\n' + 'Sell Price: ' + str(
                    market2) + '\n' + 'Buy Exchange: ' + exchange1 + '\n' + 'Buy Price: ' + str(
                    market1) + '\n' + 'Profit: ' + str(round((float(market2) - float(market1)) - fees, 2))
                send_telegram_message(self.author, message)

    def showTrades(self):
        return self.trades
