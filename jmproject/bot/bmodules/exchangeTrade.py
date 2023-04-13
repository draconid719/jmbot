from django.contrib.auth.models import User
import ccxt
import json


class ExchangeOrder(object):
    def __init__(self, pair, amount):
        self.amount = amount
        self.pair = pair
        self.exchange = None

    def buy_market_order(self):
        p = int(self.exchange.fetchTicker(self.pair)['last'])
        p = p + p
        ids = self.exchange.createLimitBuyOrder(self.pair, self.amount, p)
        return ids

    def sell_market_order(self):
        p = 1 / self.amount
        ids = self.exchange.createLimitSellOrder(self.pair, self.amount, p)
        return ids


class ExchangeGetAccount(object):
    def __init__(self, pair, author):
        self.pair = pair
        self.author = author
        self.exchange = None

    def account_hold(self):
        currency = self.pair.split('/')
        quote_currency = currency[1]
        base_currency = currency[0]

        balances_quote = self.exchange.fetch_balance()['info'][quote_currency]['available']
        balances_base = self.exchange.fetch_balance()['info'][base_currency]['available']

        if quote_currency == 'BTC':
            symbol = '₿'
        else:
            symbol = '$'
        quote_currency_hold = symbol + '%.8f' % (float(balances_quote))
        base_currency_hold = '%.8f' % (float(balances_base))

        return quote_currency_hold, base_currency_hold

    def account_order(self):
        account_order = self.exchange.fetchMyTrades(symbol=self.pair)
        return account_order

    def get_account_fees(self):
        markets = self.exchange.load_markets()
        return markets

    def current_price(self):
        return self.exchange.fetchTicker(self.pair)['last']

    def account_fee(self):
        pass
