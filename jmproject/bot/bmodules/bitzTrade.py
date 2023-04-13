# from .setting import bitz
from django.contrib.auth.models import User
import ccxt


class bitzOrder(object):
    def __init__(self, pair, amount, author):
        self.amount = amount
        self.pair = pair
        apiKey = User.objects.filter(pk=author).first().bitz.bitz_apikey
        secret = User.objects.filter(pk=author).first().bitz.bitz_secret
        self.bitz = ccxt.bitz({
            'apiKey': apiKey,
            'secret': secret,
        })

    def buy_market_order(self):
        p = int(self.bitz.fetchTicker(self.pair)['last'])
        p = p + p
        ids = self.bitz.createLimitBuyOrder(self.pair, self.amount, p)
        return ids

    def sell_market_order(self):
        p = 1 / self.amount
        ids = self.bitz.createLimitSellOrder(self.pair, self.amount, p)
        return ids


class bitzGetaccount(object):
    def __init__(self, pair, author):
        self.pair = pair
        self.author = author
        apiKey = User.objects.filter(pk=author).first().bitz.bitz_apikey
        secret = User.objects.filter(pk=author).first().bitz.bitz_secret
        self.bitz = ccxt.bitz({
            'apiKey': apiKey,
            'secret': secret,
        })

    def accounthold(self):

        Currency = self.pair.split('/')
        quoteCurrency = Currency[1]
        baseCurrency = Currency[0]
        quoteCurrencyhold = 0
        baseCurrencyhold = 0

        balances = self.bitz.fetch_balance()['info']['balances']
        for elt in balances:
            if elt['asset'] == quoteCurrency:
                if elt['asset'] == 'BTC':
                    symbol = '₿'
                else:
                    symbol = '$'
                quoteCurrencyhold = symbol + '%.8f' % (float(elt['free']))
            elif elt['asset'] == baseCurrency:
                baseCurrencyhold = '%.8f' % (float(elt['free']))
        return quoteCurrencyhold, baseCurrencyhold

    def accountorder(self):

        order = self.bitz.fetchOrders(symbol=self.pair)
        return order

    def accountfees(self):
        markets = self.bitz.load_markets()
        # print(markets)
        fees = markets[self.pair]['taker']
        return fees

    def currentprice(self):
        return self.bitz.fetchTicker(self.pair)['last']
