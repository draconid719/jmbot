# from .setting import binance
from django.contrib.auth.models import User
import ccxt
import json

from .exchangeTrade import ExchangeOrder, ExchangeGetAccount


class BinanceOrder(ExchangeOrder):
    def __init__(self, pair, amount, author):
        super().__init__(pair, amount)

        api_key = User.objects.filter(pk=author).first().binance.binance_apikey
        secret = User.objects.filter(pk=author).first().binance.binance_secret
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
        })

    def buy_market_order(self):
        ids = self.exchange.createMarketBuyOrder(self.pair, self.amount, params={'recvWindow': 60000})
        return ids

    def sell_market_order(self):
        ids = self.exchange.createMarketSellOrder(self.pair, self.amount, params={'recvWindow': 60000})
        return ids


class BinanceGetAccount(ExchangeGetAccount):
    def __init__(self, pair, author):
        super().__init__(pair, author)
        api_key = User.objects.filter(pk=author).first().binance.binance_apikey
        secret = User.objects.filter(pk=author).first().binance.binance_secret
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': secret,
        })

    def account_hold(self):
        currency = self.pair.split('/')
        quote_currency = currency[1]
        base_currency = currency[0]
        quote_currency_hold = 0
        base_currency_hold = 0

        balances = self.exchange.fetch_balance(params={'recvWindow': 60000})['info']['balances']
        for elt in balances:
            if elt['asset'] == quote_currency:
                if elt['asset'] == 'BTC':
                    symbol = '₿'
                else:
                    symbol = '$'
                quote_currency_hold = symbol + '%.8f' % (float(elt['free']))
            elif elt['asset'] == base_currency:
                base_currency_hold = '%.8f' % (float(elt['free']))
        return quote_currency_hold, base_currency_hold

    def account_order(self):
        account_order = self.exchange.fetchOrders(symbol=self.pair, params={'recvWindow': 60000})
        return account_order

    def account_fee(self):
        markets = User.objects.filter(pk=self.author).first().binance.fees
        fees = json.loads(markets)[self.pair]['taker']
        return fees
