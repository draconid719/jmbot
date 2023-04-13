# from .setting import kucoin
from django.contrib.auth.models import User
import ccxt


class kucoinOrder(object):
    def __init__(self, pair, amount, author):
        self.amount = amount
        self.pair = pair
        apiKey = User.objects.filter(pk=author).first().kucoin.kucoin_apikey
        secret = User.objects.filter(pk=author).first().kucoin.kucoin_secret
        password = User.objects.filter(pk=author).first().kucoin.kucoin_password
        self.kucoin = ccxt.kucoin({
            'apiKey': apiKey,
            'secret': secret,
            'password': password
        })

    def buy_market_order(self):
        ids = self.kucoin.createMarketBuyOrder(self.pair, self.amount)
        return ids

    def sell_market_order(self):
        ids = self.kucoin.createMarketSellOrder(self.pair, self.amount)
        return ids


class kucoinGetaccount(object):
    def __init__(self, pair, author):
        self.pair = pair
        self.author = author
        apiKey = User.objects.filter(pk=author).first().kucoin.kucoin_apikey
        secret = User.objects.filter(pk=author).first().kucoin.kucoin_secret
        password = User.objects.filter(pk=author).first().kucoin.kucoin_password
        self.kucoin = ccxt.kucoin({
            'apiKey': apiKey,
            'secret': secret,
            'password': password
        })

    def accounthold(self):

        Currency = self.pair.split('/')
        quoteCurrency = Currency[1]
        baseCurrency = Currency[0]
        quoteCurrencyhold = 0
        baseCurrencyhold = 0

        balances = self.kucoin.fetch_balance()['info']['data']
        for elt in balances:
            if elt['currency'] == quoteCurrency:
                if elt['currency'] == 'BTC':
                    symbol = '₿'
                else:
                    symbol = '$'
                quoteCurrencyhold = symbol + '%.8f' % (float(elt['available']))
            elif elt['currency'] == baseCurrency:
                baseCurrencyhold = '%.8f' % (float(elt['available']))
        return quoteCurrencyhold, baseCurrencyhold

    def accountorder(self):

        order = self.kucoin.fetchOrders(symbol=self.pair)
        return order

    def accountfees(self):
        markets = self.kucoin.load_markets()
        # print(markets)
        fees = markets[self.pair]['taker']
        return fees

    def currentprice(self):
        return self.kucoin.fetchTicker(self.pair)['last']
