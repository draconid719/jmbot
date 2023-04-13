# from .setting import bw
from django.contrib.auth.models import User
import ccxt


class bwOrder(object):
    def __init__(self, pair, amount, author):
        self.amount = amount
        self.pair = pair
        apiKey = User.objects.filter(pk=author).first().bw.bw_apikey
        secret = User.objects.filter(pk=author).first().bw.bw_secret
        self.bw = ccxt.bw({
            'apiKey': apiKey,
            'secret': secret,
        })

    def buy_market_order(self):
        p = int(self.bw.fetchTicker(self.pair)['last'])
        p = p + p
        ids = self.bw.createLimitBuyOrder(self.pair, self.amount, p)
        return ids

    def sell_market_order(self):
        p = 1 / self.amount
        ids = self.bw.createLimitSellOrder(self.pair, self.amount, p)
        return ids


class bwGetaccount(object):
    def __init__(self, pair, author):
        self.pair = pair
        self.author = author
        apiKey = User.objects.filter(pk=author).first().bw.bw_apikey
        secret = User.objects.filter(pk=author).first().bw.bw_secret
        bw = ccxt.bw({
            'apiKey': apiKey,
            'secret': secret,
        })

    def accounthold(self):

        Currency = self.pair.split('/')
        quoteCurrency = Currency[1]
        quoteCurrencyhold = 0

        balances = self.bw.fetch_balance()['info']['balances']
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

        order = self.bw.fetchOrders(symbol=self.pair)
        return order

    def accountfees(self):
        markets = self.bw.load_markets()
        # print(markets)
        fees = markets[self.pair]['taker']
        return fees

    def currentprice(self):
        return self.bw.fetchTicker(self.pair)['last']
