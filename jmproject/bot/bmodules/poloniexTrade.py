# from .setting import poloniex
from django.contrib.auth.models import User
import ccxt
import json

from .exchangeTrade import ExchangeOrder, ExchangeGetAccount


class PoloniexOrder(ExchangeOrder):
    def __init__(self, pair, amount, author):
        super().__init__(pair, amount)

        api_key = User.objects.filter(pk=author).first().poloniex.poloniex_apikey
        secret = User.objects.filter(pk=author).first().poloniex.poloniex_secret
        self.exchange = ccxt.poloniex({
            'apiKey': api_key,
            'secret': secret,
        })


class PoloniexGetAccount(ExchangeGetAccount):
    def __init__(self, pair, author):
        super().__init__(pair, author)
        api_key = User.objects.filter(pk=author).first().poloniex.poloniex_apikey
        secret = User.objects.filter(pk=author).first().poloniex.poloniex_secret
        self.exchange = ccxt.poloniex({
            'apiKey': api_key,
            'secret': secret,
        })

    def account_fee(self):
        markets = User.objects.filter(pk=self.author).first().poloniex.fees
        fees = json.loads(markets)[self.pair]["taker"]
        return fees
