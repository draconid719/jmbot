# from .setting import bittrex
from django.contrib.auth.models import User
import ccxt


class bittrexOrder(object):
    def __init__(self, pair, amount, author):
        self.amount = amount
        self.pair = pair
        apiKey = User.objects.filter(pk=author).first().bittrex.bittrex_apikey
        secret = User.objects.filter(pk=author).first().bittrex.bittrex_secret
        self.bittrex = ccxt.bittrex({
            'apiKey': apiKey,
            'secret': secret,
        })

    def buy_market_order(self):
        ids = self.bittrex.createMarketBuyOrder(self.pair, self.amount)
        return ids

    def sell_market_order(self):
        ids = self.bittrex.createMarketSellOrder(self.pair, self.amount)
        return ids


class bittrexGetaccount(object):
    def __init__(self, pair, author):
        self.pair = pair
        self.author = author
        apiKey = User.objects.filter(pk=author).first().bittrex.bittrex_apikey
        secret = User.objects.filter(pk=author).first().bittrex.bittrex_secret
        self.bittrex = ccxt.bittrex({
            'apiKey': apiKey,
            'secret': secret,
        })

    def accounthold(self):

        Currency = self.pair.split('/')
        quoteCurrency = Currency[1]
        baseCurrency = Currency[0]
        quoteCurrencyhold = 0
        baseCurrencyhold = 0

        balances = self.bittrex.fetch_balance()['info']['balances']
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

        order = self.bittrex.fetchOrders(symbol=self.pair)
        return order

    def accountfees(self):
        markets = self.bittrex.load_markets()
        # print(markets)
        fees = markets[self.pair]['taker']
        return fees

    def currentprice(self):
        return self.bittrex.fetchTicker(self.pair)['last']
