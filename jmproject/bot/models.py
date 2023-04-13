import threading

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F
from django.urls import reverse
import json
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _

from bot.bmodules.observableThread import ObservableThread

Exchange = [('binance', _('binance')), ('poloniex', _('poloniex')),
            ('bitz', _('bitz')), ('ftx', _('ftx')),
            ('kraken', _('kraken')), ('bittrex', _('bittrex')),
            ('kucoin', _('kucoin')), ('digifinex', _('digifinex')),
            ('bw', _('bw')), ('huobipro', _('huobipro'))]
Pair = [
    ('BTC/USDT', 'BTC-USDT'), ('ETH/USDT', 'ETH-USDT'), ('LINK/USDT', 'LINK-USDT'), ('XRP/USDT', 'XRP-USDT'),
    ('BCH/USDT', 'BCH-USDT'), ('XTZ/USDT', 'XTZ-USDT'), ('ETH/BTC', 'ETH-BTC'), ('LTC/USDT', 'LTC-USDT'),
    ('EOS/USDT', 'EOS-USDT'), ('DASH/USDT', 'DASH-USDT'), ('XLM/USDT', 'XLM-USDT'), ('SOL/BTC', 'SOL-BTC'),
    ('ZEC/USDT', 'ZEC-USDT'), ('XTZ/BTC', 'XTZ-BTC'), ('XMR/BTC', 'XMR-BTC'), ('TRX/USDT', 'TRX-USDT'),
    ('ADA/USDT', 'ADA-USDT'), ('XRP/BTC', 'XRP-BTC'), ('NEO/USDT', 'NEO-USDT'), ('LTC/BTC', 'LTC-BTC'),
    ('DASH/BTC', 'DASH-BTC'), ('EOS/BTC', 'EOS-BTC'), ('DATA/BTC', 'DATA-BTC'), ('ATOM/USDT', 'ATOM-USDT'),
    ('QTUM/USDT', 'QTUM-USDT'), ('ADA/BTC', 'ADA-BTC'), ('NAV/BTC', 'NAV-BTC'), ('ENJ/USDT', 'ENJ-USDT'),
    ('ALGO/USDT', 'ALGO-USDT'), ('IOTA/USDT', 'IOTA-USDT'), ('TRX/BTC', 'TRX-BTC'), ('LTO/BTC', 'LTO-BTC')
]


class Bot(models.Model):
    Candle = [
        ('1m', '1m'), ('3m', '3m'), ('5m', '5m'), ('15m', '15m'), ('30m', '30m'),
        ('1h', '1h'), ('2h', '2h'), ('4h', '4h'), ('6h', '6h'),
        ('8h', '8h'), ('12h', '12h'), ('1d', '1d'), ('3d', '3d')
    ]

    Strategies = [('MACDgoldencross', 'MACDgoldencross'),
                  ('RSIsignals', 'RSIsignals'),
                  ('MAcrossover', 'MAcrossover'),
                  ('MAgoldenCross', 'MAgoldenCross'),
                  ('MACDandRSI', 'MACDandRSI'),
                  ('RSIandMACross', 'RSIandMACross'),
                  ('StochSignal', 'StochSignal'),
                  ('Stochcrossover', 'Stochcrossover'),
                  ('MACDandStoch', 'MACDandStoch'),
                  ('StoCrossSignal', 'StoCrossSignal'),
                  ('BollingerBand', 'BollingerBand')]

    name = models.CharField(_("Name"), max_length=255)
    exchange = models.CharField(_("Exchange"), max_length=50, choices=Exchange, default='binance',
                                help_text=_('The cryptocurrency market being used'))
    candle_size = models.CharField(_("Candle Size"), max_length=50, choices=Candle, default='5m',
                                   help_text=_('The interval of time to consider as a single price data point'))
    strategy = models.CharField(_("Strategy"), max_length=100, choices=Strategies, default='MAgoldenCross',
                                help_text=_('The algorithm to use for trading using the market indicators'))
    indicator = models.TextField(null=True, help_text=_('The indicator parameter to use'))
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pair = models.CharField(_("Pair"), max_length=50, choices=Pair, default='BTC/USDT',
                            help_text=_('The cryptocurrency pair being used'))
    simultaneousTrades = models.IntegerField(_("SimultaneousTrades"), default=1,
                                             help_text=_(
                                                 'The number of trades the bot is allowed to enter at the same time'),
                                             validators=[MinValueValidator(1), MaxValueValidator(100)])
    visible = models.CharField(_("Visible"), max_length=10, choices=[('yes', _('yes')), ('no', _('no'))], default='yes',
                               help_text=_("Your bot will be visible by all user of this website"))
    profit = models.FloatField(default=0)
    bot_type = models.TextField(null=True, default='Trade')
    root = models.IntegerField(default=None, null=True)
    identification = models.IntegerField(null=True)
    sec = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_live(self):
        threads = Thread.objects.filter(bot_id=self.pk).values('mode').all()
        if len(threads) > 0:
            is_live = ''
            for thread in threads:
                is_live += str(thread['mode'])
            return is_live
        else:
            return _('Not running')
    is_live.short_description = 'Live'

    @property
    def profitusd(self):
        return self.orderhistory_set.filter(status='close').aggregate(
            total_profit_usd=Sum((F('exit_price')-F('entry_price'))*F('amount')-F('fee')))

    def total_profit(self):
        try:
            [result] = self.orderhistory_set.filter(status='CLOSE').values('bot_id').annotate(
                total_profit_usd=Sum((F('exit_price')-F('entry_price'))*F('amount')-F('fee')),
                total_profit=Sum(((F('exit_price')-F('entry_price'))*F('amount')-F('fee'))/F('entry_price')*100)
            )
            return {
                "usd_profit": "%.2f" % round(result['total_profit_usd'], 2),
                "percent_profit": "%.2f" % round(result['total_profit'], 2),
            }
        except Exception as err:
            print(err)
            return {
                "usd_profit": 0,
                "percent_profit": 0,
            }
    total_profit.short_description = 'USD Total Profit'

    def paper_profit(self):
        try:
            [result] = self.orderhistory_set.filter(status='CLOSE', paper_trading=True).values('bot_id').annotate(
                total_profit_usd=Sum((F('exit_price') - F('entry_price')) * F('amount') - F('fee')),
                total_profit=Sum(
                    ((F('exit_price') - F('entry_price')) * F('amount') - F('fee')) / F('entry_price') * 100)
            )
            return {
                "usd_profit": "%.2f" % round(result['total_profit_usd'], 2),
                "percent_profit": "%.2f" % round(result['total_profit'], 2),
            }
        except Exception as err:
            return {
                "usd_profit": 0,
                "percent_profit": 0,
            }
    paper_profit.short_description = 'USD Paper Profit'

    def live_profit(self):
        try:
            [result] = self.orderhistory_set.filter(status='CLOSE', paper_trading=False).values('bot_id').annotate(
                total_profit_usd=Sum((F('exit_price') - F('entry_price')) * F('amount') - F('fee')),
                total_profit=Sum(
                    ((F('exit_price') - F('entry_price')) * F('amount') - F('fee')) / F('entry_price') * 100)
            )
            return {
                "usd_profit": "%.2f" % round(result['total_profit_usd'], 2),
                "percent_profit": "%.2f" % round(result['total_profit'], 2),
            }
        except Exception as err:
            return {
                "usd_profit": 0,
                "percent_profit": 0,
            }
    live_profit.short_description = 'USD Live Profit'

    def save(self, *args, **kwargs):
        super(Bot, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('my-bots-page')

    def __str__(self):
        return self.name


class ArbitrageBot(models.Model):
    Exchange1 = [('binance', _('binance')), ('poloniex', _('poloniex')),
                 ('huobipro', _('huobipro')),
                 ('ftx', _('ftx')), ('kraken', _('kraken')), ('bittrex', _('bittrex'))]
    Exchange2 = [('binance', _('binance')), ('poloniex', _('poloniex')),
                 ('huobipro', _('huobipro')),
                 ('ftx', _('ftx')), ('kraken', _('kraken')), ('bittrex', _('bittrex'))]
    Pair = [
        ('BTC/USDT', 'BTC-USDT'), ('ETH/USDT', 'ETH-USDT'),
    ]

    name = models.CharField(_("Name"), max_length=60)
    firstExchange = models.CharField(_("First Exchange"), max_length=50, choices=Exchange1, default='binance',
                                     help_text=_('The first exchange from the exchange pair'))
    secondExchange = models.CharField(_("Second Exchange"), max_length=50, choices=Exchange2, default='poloniex',
                                      help_text=_('The second exchange from the exchange pair'))
    spread = models.IntegerField(_("Spread"), default=5, help_text=_('The gap between two different exchanges'),
                                 validators=[MinValueValidator(0)])
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    pair = models.CharField(_("Pair"), max_length=50, choices=Pair, default='BTC/USDT',
                            help_text=_('The cryptocurrency pair being used'))
    botype = models.TextField(null=True, default='Arbitrage')
    history = models.TextField(null=True)
    livestatus = models.TextField(null=True, choices=[('Active', _('Active')), ('Inactive', _('Inactive'))],
                                  default='Inactive')
    current_profit = models.FloatField(default=0)

    def get_absolute_url(self):
        return reverse('myarbitbots-page')

    def __str__(self):
        return self.name


class Thread(models.Model):
    bot = models.OneToOneField(Bot, default=None, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.FloatField(default=0.0)
    mode = models.TextField(choices=[('Paper', 'Paper'), ('Live', 'Live')], default='')
    author = models.CharField(max_length=50, default='')
    start_time = models.DateTimeField(default=None)
    clue = models.CharField(max_length=20, default='')

    def is_live(self):
        all_threads = threading.enumerate()
        for t in all_threads:
            if t.name == self.name and type(t) is ObservableThread and t.is_running() is True:
                return _('Running')
        return _('Not running')

    is_live.short_description = 'Active'

    def save(self, *args, **kwargs):
        super(Thread, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class OrderHistory(models.Model):

    class Meta:
        db_table = 'bot_order_history'

    bot = models.ForeignKey(Bot, default=None, on_delete=models.CASCADE)
    exchange = models.CharField(max_length=20, choices=Exchange, default='')
    pair = models.CharField(choices=Pair, max_length=10, default='')
    amount = models.FloatField(default=0.0)
    entry_price = models.FloatField(default=0.0)
    exit_price = models.FloatField(null=True, default=0.0)
    fee = models.FloatField(default=0.0)
    start_time = models.DateTimeField(default=None)
    end_time = models.DateTimeField(null=True, default=None)
    live_detail = models.TextField(null=False, default=json.dumps([]))
    status = models.CharField(max_length=5, choices=[('OPEN', 'OPEN'), ('CLOSE', 'CLOSE')], default='')
    paper_trading = models.BooleanField(default=True)

    @property
    def profit_usd(self):
        if self.status == 'CLOSE':
            return (self.exit_price - self.entry_price) * self.amount - self.fee
        else:
            return 0

    def __str__(self):
        return str(self.id) + '| ' + self.exchange


class Shout(models.Model):
    name = models.CharField(max_length=50)
    comment = models.TextField(null=False)
    date = models.DateTimeField()

    def __str__(self):
        return 'From: ' + self.name + '| ' + self.comment

    def save(self, *args, **kwargs):
        super(Shout, self).save(*args, **kwargs)
