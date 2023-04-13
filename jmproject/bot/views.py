from random import randrange

from django import db
from django.db.models import Sum, F, Case, When, Q, Func, Value, CharField
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.urls import reverse

from users.models import Profile
from .bmodules.observableThread import ObservableThread
from .models import Bot, ArbitrageBot, Thread, Shout, OrderHistory
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .Main import backtesting
from .Main import live as living
from .bmodules.tools import *
from .bmodules.botlog import BotLog
import sys, getopt
import time
import urllib
import requests
import json
from .bmodules.botchart import BotChart, chart_tick
from .bmodules.botstrategy import BotStrategy
from .bmodules.botlog import BotLog
from .bmodules.botcandlestick import BotCandlestick
from .bmodules.arbitrage import ArbitrageTrade
from .bmodules.binanceTrade import *
from .bmodules.poloniexTrade import *
from .bmodules.bittrexTrade import *
from .bmodules.bitzTrade import *
from .bmodules.bwTrade import *
from .bmodules.digifinexTrade import *
from .bmodules.ftxTrade import *
from .bmodules.huobiproTrade import *
from .bmodules.krakenTrade import *
from .bmodules.kucoinTrade import *
from .bmodules.setting import *
from django.core.paginator import Paginator
from django.contrib import messages
from django.http import HttpResponseRedirect
import os
import threading
from datetime import datetime
import dateutil.parser
from datetime import timedelta
from django.core import serializers
from django import forms
from django.conf import settings
import pytz
from django.utils import translation
from django.utils.translation import gettext_lazy as _, gettext
from ccxt.base.errors import ExchangeError, AuthenticationError
from requests.exceptions import HTTPError
from django.db.utils import OperationalError
import humanize
import ast
import urllib.parse
import re

# Create your views here.

utc = pytz.UTC


def intro(request):  # inroduction page
    return render(request, 'bot/intro.html')


def account(request):
    return render(request, 'bot/account.html')


######################Backtest Module###########################################


def createbacktest(request):  # backtest module
    if request.method == 'POST':
        start = request.POST['startdate']
        end = request.POST['endate']
        # end = datetime.strptime(end, "%Y-%m-%d")
        # end = end.strftime("%Y-%m-%d")
        end_time = date_precise_to_unix_milli(end)
        # if end == datetime.now().strftime("%Y-%m-%d"):
        #     end = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        #     endtime = date_precise_to_unix_milli(end)
        # else:
        #     end = datetime.strptime(end, "%Y-%m-%d")
        #     end = str(end + timedelta(hours=23, minutes=59, seconds=59))
        #     endtime = date_precise_to_unix_milli(end)
        c_bot = request.POST['pk']
        amount = request.POST['amount']
        bot = Bot.objects.filter(pk=c_bot).first()
        exchange = bot.exchange
        strategy = None

        strategy = bot.strategy
        candlesize = bot.candle_size
        amount = float(amount)
        pair = bot.pair
        indicator = bot.indicator

        # try:
        simultaneousTrades = int(bot.simultaneousTrades)
        start_time = date_precise_to_unix_milli(start)
        outcome, trade, tradePrice, backtrades = backtesting(start_time, end_time, amount, candlesize, bot.author, bot,
                                                             exchange, strategy, simultaneousTrades, pair, indicator)

        # Profit = (Profit/float(startamount))*100
        # endingam =round((((float(startamount)* float(Profit))/100)+float(startamount)),10)
        cur_symbol = pair.split('/')
        cur_symbol = cur_symbol[1]
        if cur_symbol == 'BTC':
            f = '.12f'
        else:
            f = '.4f'

        Profit = format(float(amount) * float(outcome), f)

        Profit = str(Profit) + ' ' + cur_symbol

        trades = [[trade.start_time, trade.end_time, backtrades.index(trade), round(trade.entry_price, 8),
                   round(trade.exit_price, 8), pair] for trade in backtrades if trade.exit_price != '']
        # tradechart = [{'time': str(trade.time), 'value': round((trade.exitPrice - trade.entryPrice),
        # 2)}  for trade in backtrades if trade.exitPrice != '' ]

        stri = ''
        for trade in trades:

            if (trade[4] - trade[3]) * amount < 0:
                instri = '''
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td class="crypt-up">{}</td>
                    <td class="crypt-down">{}</td>
                    <td>{}</td>
                    <td class="crypt-down"><b>{}</b></td>
                </tr>\n'''.format(trade[0], trade[1], 'Market/' + pair, format(trade[3], f),
                                  format(trade[4], f), float(amount),
                                  format((trade[4] - trade[3]) * amount, f))
            else:
                instri = '''
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td class="crypt-up">{}</td>
                    <td class="crypt-down">{}</td>
                    <td>{}</td>
                    <td class="crypt-up"><b>{}</b></td>
                </tr>\n'''.format(trade[0], trade[1], 'Market/' + pair, format(trade[3], f),
                                  format(trade[4], f), float(amount),
                                  format((trade[4] - trade[3]) * amount, f))

            stri += instri

        jsdata = {'tabletrade': stri, 'profit': Profit}

        return JsonResponse(jsdata)
        # except Exception as e:
        #     print(164, e)
        #     messages.warning(request, 'Backtest Error: ' + exchange + ' ' + str(e))
        #     jsdata = {}
        #     return JsonResponse(jsdata)

    return HttpResponse('')


##################################################################################

##############Arbitrage Module####################################################
@login_required
def arbitrage(request):  # displays the arbitrage bots

    context = {
        'bots': ArbitrageBot.objects.filter(author=request.user),
        'home': "",
        'backtest': "",
        'live': "",
        'paper': "",
        'arbitrage': "active",
        'profile': "",
        'mybots': "",
        'aboutus-page': "",
        'title': "Arbitrage Trading",

    }
    return render(request, 'bot/arbitrage.html', context)


def getcreatelivearbitrage(Lbot, mode, tradeamount, bot, exchange1, exchange2, botname, pair, spread, author,
                           pkid):  # accomplish the purpose of the thread
    exchanges = {'binance': binance,
                 'poloniex': poloniex,
                 'bittrex': bittrex,
                 'ftx': ftx,
                 'kraken': kraken,
                 'bitz': bitz,
                 'kucoin': kucoin,
                 'digifinex': digifinex,
                 'bw': bw,
                 'huobipro': huobipro}

    if mode == 'Live':
        paper = 'False'
    else:
        paper = 'True'

    bot_obj = ArbitrageBot.objects.filter(pk=Lbot).first()
    arb = ArbitrageTrade(exchange1, exchange2, pair, spread, tradeamount, author, paper)

    while Thread.objects.filter(user=str(pkid) + ':arb:' + str(botname)).first() != None:
        try:
            exchange1_price, exchange2_price = arb.check_market()
            arb.strategy(tradeamount, spread, exchange1, exchange1_price, exchange2, exchange2_price)
            arbtrades = arb.showTrades()

            if len(arbtrades) > 0:
                bot_obj.history = json.dumps(arbtrades)
                bot_obj.save()
        except:
            time.sleep(30)
            exchange1_price, exchange2_price = arb.check_market()
            arb.strategy(tradeamount, spread, exchange1, exchange1_price, exchange2, exchange2_price)
            arbtrades = arb.showTrades()

            if len(arbtrades) > 0:
                bot_obj.history = json.dumps(arbtrades)
                bot_obj.save()

        time.sleep(30)


def createlivearbitrage(request):  # instantiate the thread for the arbitrage bot

    if request.method == 'POST':
        Lbot = request.POST['pk']
        mode = request.POST['mode']
        amount = request.POST['amount']
        bot = ArbitrageBot.objects.filter(pk=Lbot).first()

        exchange1 = bot.firstExchange
        exchange2 = bot.secondExchange
        tradeamount = float(amount)
        botname = bot.name
        pair = bot.pair
        spread = bot.spread
        bot_obj = ArbitrageBot.objects.filter(pk=Lbot).first()
        bot_obj.save()

        pkid = str(request.user.pk)
        arguments = [Lbot, mode, tradeamount, bot_obj, exchange1, exchange2, botname, pair, spread, request.user.pk,
                     pkid]
        threadname = str(request.user.pk) + ':arb:' + botname
        t = threading.Thread(target=getcreatelivearbitrage, name=threadname, args=arguments)

        thr_obj = Thread(user=threadname, thread=t.name, amount=tradeamount, cursus=mode, author=request.user.pk,
                         botname=botname, starttime=datetime.now().replace(tzinfo=utc), clue='arbitrage')
        thr_obj.save()
        t.setDaemon(True)
        t.start()

    return HttpResponse()


def arbitragetornado(
        request):  # continously pull data from the database (exchange price, amount traded etc), similar to redis
    # tornado
    try:
        jsondec = json.decoder.JSONDecoder()
        if request.method == 'POST':
            Lbot = request.POST['pk']
            bot = ArbitrageBot.objects.filter(pk=Lbot).first()

            exchange1 = bot.firstExchange
            exchange2 = bot.secondExchange
            pair = bot.pair
            spread = bot.spread
            bot_obj = ArbitrageBot.objects.filter(pk=Lbot).first()

            tradeHistory = []
            trades = bot_obj.history
            if trades != None:
                trades = jsondec.decode(trades)
                # print(trades)
                tradeHistory.extend(trades)

            stri = ""
            if len(tradeHistory) > 0:
                for trade in tradeHistory[-9:][::-1]:
                    # fees = 0
                    instri = '''
                        <tr>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                            <td>{}</td>
                        </tr>\n'''.format(trade[0], trade[2], trade[3], trade[4], trade[5], trade[6], trade[7],
                                          round(((trade[5] - trade[3]) - trade[7]), 9))

                    stri += instri
                try:
                    thread = Thread.objects.filter(user=str(request.user.pk) + ':arb:' + bot.name).first()
                    amount = thread.amount
                    cursus = thread.cursus
                    is_bot_running = thread.is_alive()
                except Exception as e:
                    print(e)
                    amount = ''
                    cursus = ''
                    is_bot_running = False
                jsdata = {'tabletrade': stri, 'amount': amount, 'cursus': cursus, 'is_bot_running': is_bot_running}
                return JsonResponse(jsdata)

        return JsonResponse({})
    except ConnectionAbortedError:
        return None


def arbitrageExchangelive(request):  # fetch all data for the two exchange in arbitrage
    try:
        exchanges = {'binance': binance,
                     'poloniex': poloniex,
                     'bittrex': bittrex,
                     'ftx': ftx,
                     'kraken': kraken,
                     'bitz': bitz,
                     'kucoin': kucoin,
                     'digifinex': digifinex,
                     'bw': bw,
                     'huobipro': huobipro}
        if request.method == 'POST':
            Lbot = request.POST['pk']
            bot = ArbitrageBot.objects.filter(pk=Lbot).first()

            botname = bot.name
            bot_obj = ArbitrageBot.objects.filter(pk=Lbot).first()

            firstex = bot_obj.firstExchange
            secex = bot_obj.secondExchange

            firstexprice = round(exchanges[firstex].fetchTicker(bot_obj.pair)['last'], 9)
            firstexvolume = exchanges[firstex].fetchTicker(bot_obj.pair)['quoteVolume']
            firstexsymb = bot_obj.pair
            secexprice = round(exchanges[secex].fetchTicker(bot_obj.pair)['last'], 9)
            secexvolume = exchanges[secex].fetchTicker(bot_obj.pair)['quoteVolume']
            secexsymb = bot_obj.pair
            quote = secexsymb.split('/')
            quote = quote[1]
            jsdata = {'firstvolume': firstexvolume,
                      'firstprice': firstexprice,
                      'firstsymb': firstexsymb,
                      'secvolume': secexvolume,
                      'secprice': secexprice,
                      'secsymb': secexsymb,
                      'quote': quote}

            return JsonResponse(jsdata)

        return JsonResponse({})
    except ConnectionAbortedError:
        return None


@login_required
def arbtrade(request, pk):  # page of operation for arbitrage

    base = ArbitrageBot.objects.filter(pk=pk).first().pair
    base = base.split('/')
    base = base[0]
    context = {
        'bots': ArbitrageBot.objects.filter(pk=pk).first(),
        'home': "",
        'backtest': "",
        'live': "active",
        'paper': "",
        'arbitrage': "",
        'pair': ArbitrageBot.objects.filter(pk=pk).first().pair,
        'profile': "",
        'mybots': "",
        'base': base,
        'aboutus-page': "",
        'title': "Live Trading",
        'pk': pk,
        'firstexurl': 'bot/images/{}.png'.format(ArbitrageBot.objects.filter(pk=pk).first().firstExchange),
        'secexurl': 'bot/images/{}.png'.format(ArbitrageBot.objects.filter(pk=pk).first().secondExchange)

    }
    bot_obj = ArbitrageBot.objects.filter(pk=pk).first()
    return render(request, 'bot/arboperation.html', context)


##################################################################################


##################################################################################
def get_live_status(request):  # get the status of a particular bot if it is working or not
    try:
        if request.method == 'POST':
            pk = request.POST['pk']
            bot = Bot.objects.filter(pk=pk).first()

            if hasattr(bot, 'thread'):
                return JsonResponse({'bot': 'true'})
            return JsonResponse({'bot': 'false'})

        return JsonResponse({})
    except ConnectionAbortedError:
        return None


def getarblivestatus(request):  # get the status of a particular arbitrage bot if it is working or not
    try:
        if request.method == 'POST':
            pk = request.POST['pk']
            bot = ArbitrageBot.objects.filter(pk=pk).first()
            # print(bots)
            threadname = str(request.user.pk) + ':arb:' + str(bot.name)

            if Thread.objects.filter(user=threadname).first() is not None:
                jsdata = {'bot': 'true'}
                return JsonResponse(jsdata)
            # print('none')
            jsdata = {'bot': 'false'}
            return JsonResponse(jsdata)

        return JsonResponse({})
    except ConnectionAbortedError:
        return None


def deactivate_live(request):  # stop a particular bot
    if request.method == 'POST':
        bot_pk = request.POST['pk']
        bot = Bot.objects.filter(pk=bot_pk).first()
        bot.thread.delete()
        print(str(request.user) + ':' + str(bot.name) + ' process stopped')

    return HttpResponse('')


def deactivatelivearb(request):  # stop a particular arbitrage bot
    if request.method == 'POST':
        Lbot = request.POST['pk']
        bot = ArbitrageBot.objects.filter(pk=Lbot).first()

        bot_obj = ArbitrageBot.objects.filter(pk=Lbot).first()
        threadname = str(request.user.pk) + ':arb:' + str(bot.name)
        thread = Thread.objects.filter(user=threadname).first()

        bot_obj.livestatus = 'Inactive'
        bot_obj.save()
        thread.delete()
        print(str(request.user) + ':arb:' + str(bot.name) + ' process stoped')

    return HttpResponse('')


#############################################
# Live Trading Module
#############################################


@login_required
def do_trade(request, pk):  # page of operation for bot
    bot = Bot.objects.filter(pk=pk).first()
    base = bot.pair
    base = base.split('/')
    base = base[0]
    botexchange = bot.exchange
    # print(pk)
    redirect_api_setting(botexchange, request)

    jsondec = json.decoder.JSONDecoder()
    strat = get_strategy(request.LANGUAGE_CODE)
    exp = get_exp()

    strategyexp = exp[bot.strategy]
    strategydef = strat[bot.strategy]

    history = jsondec.decode(bot.longhistory)
    # history = []

    # bot = Bot.objects.filter(name='testing').first()
    # print(bot.pk)
    transactionHtml = ""
    transactionHtml2 = ""

    if len(history) > 0:
        for trade in history:
            if trade['author'] == request.user.username and trade['exitPrice'] != '':
                script = '''
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>\n'''.format(trade['time'], trade['amount'], trade['entryPrice'], trade['exitPrice'],
                                      trade['pair'], format(
                        round((trade['exitPrice'] - trade['entryPrice']) * float(trade['amount']) - trade['fees'],
                              9), '.9f'))
                if not trade['papertrading']:
                    transactionHtml += script
                else:
                    transactionHtml2 += script

    context = {
        'bots': Bot.objects.filter(pk=pk).first(),
        'pk': pk,
        'home': "",
        'backtest': "",
        'live': "active",
        'paper': "",
        'arbitrage': "",
        'profit': '%.9f' % (Bot.objects.filter(pk=pk).first().profit),
        'profile': "",
        'mybots': "",
        'base': base,
        'strategyexp': strategyexp,
        'strategydef': strategydef,
        'rawhtml': transactionHtml,
        'rawhtml2': transactionHtml2,
        'aboutus-page': "",
        'title': "displayname",
        'name': Bot.objects.filter(pk=pk).first().name.upper(),
        'exchange': Bot.objects.filter(pk=pk).first().exchange.upper(),
        'exchangeurl': 'bot/images/{}.png'.format(Bot.objects.filter(pk=pk).first().exchange)

    }
    bot_obj = Bot.objects.filter(pk=pk).first()
    return render(request, 'bot/operation.html', context)


def getcreatelive(bot_pk, mode, amount, bot, exchange, strategy, candle_size, pair, simultaneous_trades, author,
                  bot_name, indicator, pk_id):  # accomplish the purpose of the thread
    exchanges, hold = get_exchange_hold()

    jsondec = json.decoder.JSONDecoder()

    if mode == 'Paper':
        is_paper_trading = True
    else:
        is_paper_trading = False

    chart = BotChart(exchange, pair, candle_size, None, None, False)

    fee = 0
    while fee == 0:
        try:
            fee = hold[bot.exchange](bot.pair, author).account_fee()
        except Exception as e:
            print(581, bot_pk, e)
            time.sleep(int(randrange(30, 60)))
            continue
    print(f'{bot_pk} fee:', fee)

    strategy = BotStrategy(strategy, indicator, simultaneous_trades, author, bot, exchange, pair, amount, fee,
                           is_paper_trading)

    candle_stick = BotCandlestick(string_to_sec(candle_size))

    while hasattr(bot, 'thread'):
        all_threads = threading.enumerate()
        result = [a for a in all_threads if type(a) is ObservableThread and a.name == bot.thread.name]
        if len(result) > 0:
            result[0].stop_event.wait()
        try:
            candle_stick.tick(chart.get_current_price())
        except requests.exceptions.ConnectionError as e:
            print(597, bot_name, e)
            time.sleep(int(30))
            candle_stick.tick(chart.get_current_price())
        except Exception as e:
            print(602, bot_name, e)
            time.sleep(int(30))
            continue

        if candle_stick.is_closed():
            strategy.tick(candle_stick)  # TODO Exception
            candle_stick = BotCandlestick(string_to_sec(candle_size))

            bot_trades = strategy.show_positions()
            if len(bot_trades) > 0:
                # retrieving history
                prof = 0
                for trade in bot_trades:
                    if trade.exit_price != '':
                        prof = float(prof) + (((float(trade.exit_price) - trade.entry_price) * float(trade.amount)) -
                                              float(trade.fee))
                        if bot.root:
                            root = Bot.objects.filter(name=bot.root).first()
                            root.profit = '%.9f' % (float(root.profit) + prof)
                            root_history = jsondec.decode(root.history)
                            if trade not in root_history:
                                root_history.append(trade)
                            root.history = json.dumps(root_history)
                            root.longhistory = json.dumps(root_history)
                            root.save()

                for trade in bot_trades:
                    if trade.status == 'OPEN' and trade.id is None:
                        order = OrderHistory(bot=bot, exchange=exchange, pair=pair, amount=amount,
                                             entry_price=trade.entry_price, fee=trade.fee, start_time=trade.start_time,
                                             status='OPEN', paper_trading=trade.paper_trading, live_detail=trade.orders)
                        try:
                            order.save()
                        except Exception as err:
                            print(err)
                    elif trade.status == 'CLOSE':
                        if trade.id:
                            order = OrderHistory.objects.filter(pk=trade.id).first()
                            order.exit_price = trade.exit_price
                            order.end_time = trade.end_time
                            order.status = 'CLOSE'
                            order.live_detail = trade.orders
                            order.fee = trade.fee
                            order.save()
                        else:
                            order = OrderHistory(bot=bot, exchange=exchange, pair=pair, amount=amount,
                                                 entry_price=trade.entry_price, exit_price=trade.exit_price,
                                                 end_time=trade.end_time, fee=trade.fee, start_time=trade.start_time,
                                                 status='CLOSE', paper_trading=trade.paper_trading)
                            order.save()

                bot.profit = '%.9f' % prof

                if bot.pair.split('/')[1] != 'USDT':
                    usd_value = exchanges[bot.exchange].fetchTicker('BTC/USDT')['last']
                    bot.profit = '%.2f' % (float(prof) * float(usd_value))
                else:
                    bot.profit = '%.2f' % prof

                bot.save()

                # TODO: Need to check if db connection is still alive, not then close
                db.connections.close_all()

        time.sleep(int(30))


def create_live(request):  # instantiate the thread with all information (amount, pair etc)
    if request.method == 'POST':
        bot_pk = request.POST['pk']
        mode = request.POST['mode']
        amount = request.POST['amount']
        author = request.user.pk
        bot = Bot.objects.filter(pk=bot_pk).first()

        api_key = User.objects.filter(pk=author).first().poloniex.poloniex_apikey
        secret = User.objects.filter(pk=author).first().poloniex.poloniex_secret
        if not api_key or api_key.isspace() or not secret or secret.isspace():
            return JsonResponse({
                'status': 'error',
                'message': _('You must set API key and secret pair. Please click below button to set keys.')
            })

        exchanges, hold = get_exchange_hold()
        try:
            quote_currency_hold, base_currency_hold = hold[bot.exchange](bot.pair, request.user.pk).account_hold()
        except AuthenticationError as e:
            return JsonResponse({
                'status': 'error',
                'message': _('Invalid API key and secret pair. Please check API key and secret key again.')
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': e})

        exchange = bot.exchange
        strategy = bot.strategy
        candle_size = bot.candle_size
        amount = float(amount)
        pair = bot.pair
        simultaneous_trades = bot.simultaneousTrades
        bot_name = bot.name
        indicator = bot.indicator
        thread_name = str(request.user.pk) + ':' + str(bot_name)
        pk_id = request.user.pk
        arguments = [bot_pk, mode, amount, bot, exchange, strategy, candle_size, pair, simultaneous_trades,
                     request.user.pk, bot_name, indicator, pk_id]

        all_threads = threading.enumerate()
        result = [a for a in all_threads if type(a) is ObservableThread and a.name == thread_name]
        if len(result) == 0:
            t = ObservableThread(target=getcreatelive, name=thread_name, args=arguments)
            t.setDaemon(True)
            t.start_thread()
        else:
            result = [a for a in result if a.is_running() is False]
            if len(result) > 0:
                result[0].restart_thread()

        thr_obj = Thread(name=thread_name, amount=amount, mode=mode, author=request.user.pk,
                         bot=bot, start_time=datetime.now().replace(tzinfo=utc), clue='market')
        thr_obj.save()

    return JsonResponse({})


def elapsed(request):
    if request.method == 'POST':
        bot_pk = request.POST['pk']
        bot_type = request.POST['type']

        if bot_type == 'bot':
            bot = Bot.objects.filter(pk=bot_pk).first()
            try:
                thread = bot.thread
                elapsed_time = time_difference(thread.start_time)
            # elapsed = elapsed[:-3]
            except:
                elapsed_time = _('Not running')
        else:
            bot = ArbitrageBot.objects.filter(pk=bot_pk).first()
            try:
                thread = Thread.objects.filter(user=str(request.user.pk) + ':arb:' + str(bot.name)).first()
                elapsed_time = time_difference(thread.starttime).replace('ago', '').replace('an hour',
                                                                                            '1 hour').replace(
                    'a minute', '1 minute').replace('a month', '1 month')
            # elapsed = elapsed[:-3]
            except:
                elapsed_time = _('Not running')

        js_data = {'elapsed': elapsed_time}
        return JsonResponse(js_data)
    return JsonResponse({})


def live_tornado(request):  # continuously fetch data from the database, similar to redis tornado
    try:
        exchanges, hold = get_exchange_hold()

        if request.method == 'POST':
            bot_pk = request.POST['pk']
            bot = Bot.objects.filter(pk=bot_pk).first()

            try:
                quote_currency_hold, base_currency_hold = hold[bot.exchange](bot.pair, request.user.pk).account_hold()
            except ExchangeError as e:
                print(736, request.POST['pk'], str(e))
                time.sleep(30)
                return JsonResponse({'error': str(e)})
            except HTTPError as e:
                print(737, e)
                time.sleep(30)
                return JsonResponse({'error': str(e)})

            if '$' in quote_currency_hold:
                balance_sym = 'USDT'
            else:
                balance_sym = 'BTC'

            quote_int = re.findall('(\d+(?:\.\d+)?)', quote_currency_hold)
            quote_index = quote_currency_hold.index(quote_int[0])
            quote_sym = quote_currency_hold[:quote_index]
            quote_currency_hold = quote_sym + format(float(quote_int[0]), '.2f')

            base_sym = bot.pair.split('/')[0]
            # try:
            base_currency_hold_usd = float(base_currency_hold) * float(
                hold[bot.exchange](base_sym + '/USDT', request.user.pk).current_price())
            # except:
            # 	base_currency_hold_usd = '--'

            fees = hold[bot.exchange](bot.pair, request.user.pk).account_fee()
            current_price = float(hold[bot.exchange](bot.pair, request.user.pk).current_price())

            trade_history = bot.orderhistory_set.order_by('-start_time').all()[:50]

            otp = '%.2f' % 0
            trans_html1 = trans_html2 = ""

            if len(trade_history) > 0:
                for trade in trade_history:
                    if trade.bot.author.pk == request.user.pk:
                        if trade.status == 'OPEN':
                            exit_price = current_price
                            exit_time = '--'
                            otp = format(float(otp) + (((exit_price - float(trade.entry_price)) * float(trade.amount))
                                                       - (float(fees * float(trade.amount)) * float(
                                        trade.entry_price))), '.2f')
                            amount = float(trade.amount)
                            infees = (float(fees * amount) * float(trade.entry_price))
                            script = '''<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>
                                    <td>{}</td><td>{}</td><td><button onclick="deleteRow('{}')">{}</button></td>
                                </tr>'''.format(trade.start_time, exit_time, format(amount, '.4f'),
                                                format(trade.entry_price, '.2f'),
                                                format(exit_price, '.2f'), trade.pair, format(infees, '.2f'),
                                                format(((exit_price - trade.entry_price) * amount) - infees, '.2f'),
                                                trade.id, _("Cancel"))
                            trans_html1 += script
                        else:
                            exit_price = float(trade.exit_price)
                            exit_time = trade.end_time
                            amount = float(trade.amount)
                            infees = trade.fee
                            script = '''<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>
                                    <td>{}</td><td>{}</td><td></td></tr>''' \
                                .format(trade.start_time, exit_time, format(amount, '.4f'),
                                        format(trade.entry_price, '.2f'), format(exit_price, '.2f'), trade.pair,
                                        format(infees, '.2f'),
                                        format(((exit_price - trade.entry_price) * amount) - infees, '.2f'))
                            trans_html2 += script

            order_html = ""
            order_history = []
            try:
                order_history_buy = bot.orderhistory_set.filter(paper_trading=False) \
                    .annotate(order_time=F('start_time'), order_price=F('entry_price'),
                              order_side=Value(_("Buy"), output_field=CharField())).order_by('-order_time')
                order_history_sell = bot.orderhistory_set.filter(paper_trading=False, status='CLOSE') \
                    .annotate(order_time=F('end_time'), order_price=F('exit_price'),
                              order_side=Value(_("Sell"), output_field=CharField())).order_by('-order_time')
                order_history = order_history_buy.union(order_history_sell).order_by('-order_time').all()[:50]
            except Exception as e:
                print(e)
            for order in order_history:
                if int(order.bot.author.pk) == request.user.pk:
                    live_detail = ast.literal_eval(order.live_detail)
                    order_id = ""
                    if len(live_detail) > 1:
                        # Sell order
                        order_id = live_detail[1][2]
                    elif len(live_detail) == 1:
                        # Buy order
                        order_id = live_detail[0][2]

                    script = '''<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>''' \
                        .format(order.order_time, order.order_side, order_id, "market", order.order_price,
                                order.amount)
                    order_html += script

            # Check if bot thread is running
            is_bot_running = False
            if hasattr(bot, 'thread'):
                thread = bot.thread
                amount = thread.amount
                mode = thread.mode
                all_threads = threading.enumerate()
                for t in all_threads:
                    if t.name == thread.name:
                        print(t)
                        is_bot_running = True
            else:
                amount = 0
                mode = ''

            if bot.pair.split('/')[1] == 'USDT':
                ctp = bot.total_profit()
            else:
                ctp = bot.total_profit()
            tp = format(float(otp) + float(ctp['usd_profit']), '.2f')
            js_data = {'order': order_html, 'table_trade1': trans_html1, 'table_trade2': trans_html2,
                       'balance_base': base_currency_hold, 'base_sym': base_sym, 'balance': quote_currency_hold,
                       'usd_balance': ' $' + '%.2f' % base_currency_hold_usd,
                       'balance_sym': balance_sym, 'amount': amount, 'mode': mode, 'otp': otp, 'ctp': ctp, 'tp': tp,
                       'is_bot_running': is_bot_running}
            return JsonResponse(js_data)

        return JsonResponse({})
    except Exception as e:
        print(e)
        return None


def delete_trade(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']

        order = OrderHistory.objects.filter(pk=order_id).first()
        order.delete()

    return JsonResponse({})


def manualtornado(
        request):  # for manual mode, continously fetch data from the database and apis, similar to redis tornado
    try:
        exchanges, hold = get_exchange_hold()

        jsondec = json.decoder.JSONDecoder()
        if request.method == 'POST':
            amount = request.POST['amount']
            pair = request.POST['pair']
            exchange = request.POST['exchange']

            Currency = pair.split('/')
            quoteCurrency = Currency[1]
            baseCurrency = Currency[0]
            quoteCurrencyhold = 0

            base = Currency[::-1]
            coins = '/'.join(Currency)

            try:
                quoteCurrencyhold = hold[exchange](pair, request.user.pk).accounthold()
                account_order = hold[exchange](pair, request.user.pk).accountorder()
                baseCurrencyhold = hold[exchange](coins, request.user.pk).accounthold()

            except urllib.error.URLError:
                time.sleep(30)

                quoteCurrencyhold = hold[exchange](pair, request.user.pk).accounthold()
                account_order = hold[exchange](pair, request.user.pk).accountorder()
                baseCurrencyhold = hold[exchange](coins, request.user.pk).accounthold()
            except Exception as e:
                time.sleep(60)

                quoteCurrencyhold = hold[exchange](pair, request.user.pk).accounthold()
                account_order = hold[exchange](pair, request.user.pk).accountorder()
                baseCurrencyhold = hold[exchange](coins, request.user.pk).accounthold()

            fees = 0
            amount = float(amount)
            market = exchanges[exchange].markets

            orderHtml = ""
            account_order = account_order[::-1][0:10]

            for order in account_order:
                script = '''
                    <tr>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                        <td>{}</td>
                    </tr>\n'''.format(order['datetime'], order['id'], order['type'], order['price'], order['amount'])

                orderHtml += script

            jsdata = {'balance1': baseCurrencyhold, 'balance2': quoteCurrencyhold, 'order': orderHtml}
            return JsonResponse(jsdata)

        return JsonResponse({})
    except ConnectionAbortedError:
        return None


###############################MANUAL#################################
def manual_page(request, slug):  # the manual module
    coin = slug
    coin = coin.upper()
    coin = coin.replace('-', '/')
    # print(coin)

    tobase = coin.split('/')
    base = tobase[0]
    quote = tobase[1]
    context = {
        'coin': coin,
        'base': base,
        'quote': quote
    }
    return render(request, 'bot/manual.html', context)


def exchange_buy(request):  # effectuate buy order
    exchanges = {'binance': BinanceOrder,
                 'poloniex': PoloniexOrder,
                 'bittrex': bittrexOrder,
                 'ftx': ftxOrder,
                 'kraken': krakenOrder,
                 'bitz': bitzOrder,
                 'kucoin': kucoinOrder,
                 'digifinex': digifinexOrder,
                 'bw': bwOrder,
                 'huobipro': huobiproOrder}
    if request.method == 'POST':
        exchange = request.POST['exchange']
        amount = float(request.POST['amount'])
        pair = request.POST['pair']

        exchanges[exchange](pair, amount, request.user.pk).buy_market_order()

    return JsonResponse({})


def exchange_sell(request):  # effectuate sell order
    exchanges = {'binance': BinanceOrder,
                 'poloniex': PoloniexOrder,
                 'bittrex': bittrexOrder,
                 'ftx': ftxOrder,
                 'kraken': krakenOrder,
                 'bitz': bitzOrder,
                 'kucoin': kucoinOrder,
                 'digifinex': digifinexOrder,
                 'bw': bwOrder,
                 'huobipro': huobiproOrder}
    if request.method == 'POST':
        exchange = request.POST['exchange']
        amount = float(request.POST['amount'])
        pair = request.POST['pair']

        exchanges[exchange](pair, amount, request.user.pk).sell_market_order()
    return JsonResponse({})


########################################################################


@login_required
def my_bots(request, slug):  # display all the bot of a user
    query = ''
    filter_query = ''

    bots = Bot.objects.filter(author=request.user)

    if 'filter' in request.GET:
        filter_query = request.GET['filter']
        if request.GET['filter'] == 'Inactive':
            bots = Bot.objects.filter(author=request.user).filter(thread__isnull=True)
        elif request.GET['filter'] == 'Active':
            bots = Bot.objects.filter(author=request.user).filter(thread__isnull=False)

    if 'search' in request.GET:
        bots = bots.filter(name__icontains=request.GET['search'])

    # Order By
    if slug == 'default':
        order_key = request.user.profile.sorting_preference
    else:
        order_key = slug

    if order_key == 'profit' or order_key == '-profit':
        bots = bots.annotate(profit_usd=Coalesce(Sum(
            Case(When(orderhistory__status='open', then=0),
                 default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                     'orderhistory__amount') - F('orderhistory__fee')))), 0)
        ).order_by(order_key + '_usd')
    else:
        bots = bots.order_by(order_key)

    if slug in ['profit', 'name', '-profit']:
        userprof = User.objects.filter(username=request.user).first()
        userprof = userprof.profile
        userprof.sorting_preference = slug
        userprof.save()

    paginator = Paginator(bots, 8)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bots': page_obj,
        'home': "",
        'backtest': "",
        'live': "",
        'paper': "",
        'arbitrage': "",
        'profile': "",
        'mybots': "active",
        'aboutus-page': "",
        'title': "Bots",
        'selected': order_key,
        'filter': filter_query,
        'usercreator': request.user,
        'term': query
    }
    return render(request, 'bot/mybots.html', context)


@login_required
def filter(request, slug):  # filter the bots by active inactive etc

    query = ''
    bots = Bot.objects.filter(author=request.user)
    if slug == 'all':
        allbot = Bot.objects.filter(author=request.user)
        if 'search' in request.GET:
            query = request.GET['search']
            allbot = allbot.order_by(request.user.profile.sorting_preference)
            result = []
            for ob in allbot:
                if query in ob.name:
                    result.append(ob)
        else:
            result = allbot.order_by(request.user.profile.sorting_preference)
    elif slug == 'inactive':
        allbot = Bot.objects.filter(author=request.user).filter(livestatus='Inactive')
        if 'search' in request.GET:
            query = request.GET['search']
            allbot = allbot.order_by(request.user.profile.sorting_preference)
            result = []
            for ob in allbot:
                if query in ob.name:
                    result.append(ob)
        else:
            result = allbot.order_by(request.user.profile.sorting_preference)
    else:
        result = []
        allactive = Thread.objects.filter(author=request.user)
        if 'search' in request.GET:
            query = request.GET['search']
            allbot = bots.order_by(request.user.profile.sorting_preference)
            for ob in allactive:
                if 'arb' not in ob.user and query in ob.botname:
                    result.append(Bot.objects.filter(name=ob.botname).first())
        else:
            for ob in allactive:
                if 'arb' not in ob.user:
                    result.append(Bot.objects.filter(name=ob.botname).first())

    paginator = Paginator(result, 8)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bots': page_obj,
        'home': "",
        'backtest': "",
        'live': "",
        'paper': "",
        'arbitrage': "",
        'profile': "",
        'mybots': "active",
        'aboutus-page': "",
        'title': "Bots",
        'selected': request.user.profile.sorting_preference,
        'filter': slug,
        'term': query,

    }
    return render(request, 'bot/mybots.html', context)


@login_required
def arbfilter(request, slug):  # filter the arbitrage bots by active inactive etc

    if slug == 'all':
        allbot = ArbitrageBot.objects.filter(author=request.user)
        allbot = allbot.order_by('name')
    elif slug == 'inactive':
        allbot = ArbitrageBot.objects.filter(author=request.user).filter(livestatus='Inactive')
        allbot = allbot.order_by('name')
    else:
        allbot = ArbitrageBot.objects.filter(author=request.user).filter(livestatus='Active')
        allbot = allbot.order_by('name')

    paginator = Paginator(allbot, 8)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bots': page_obj,
        'home': "",
        'backtest': "",
        'live': "",
        'paper': "",
        'arbitrage': "",
        'profile': "",
        'mybots': "active",
        'aboutus-page': "",
        'title': "Bots",
        'filter': slug,

    }
    return render(request, 'bot/myarbitragebot.html', context)


@login_required
def myarbitragebots(request):  # displays all arbitrage bots of a user
    threads = Thread.objects.filter(author=request.user.pk)
    allbot = ArbitrageBot.objects.filter(author=request.user)
    filterquery = ''
    if 'filter' in request.GET:
        if request.GET['filter'] == 'Active':
            allbot = ArbitrageBot.objects.filter(author=request.user).filter(livestatus='Active')
            allbot = allbot.order_by('name')

        elif request.GET['filter'] == 'Inactive':
            allbot = ArbitrageBot.objects.filter(author=request.user).filter(livestatus='Inactive')
            allbot = allbot.order_by('name')
        else:
            allbot = ArbitrageBot.objects.filter(author=request.user)
            allbot = allbot.order_by('name')
        filterquery = request.GET['filter']

    for bot in allbot:
        bot.livestatus = 'Inactive'
        for thread in threads:
            if bot.name in thread.botname and 'arb' in thread.user:
                bot.livestatus = 'Active'
        bot.save()
    allbot = allbot.order_by('name')
    paginator = Paginator(allbot, 8)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'bots': page_obj,
        'home': "",
        'backtest': "",
        'live': "",
        'paper': "",
        'arbitrage': "",
        'profile': "",
        'mybots': "active",
        'aboutus-page': "",
        'title': "Bots",
        'filter': filterquery,
        'stat': 'active'

    }
    return render(request, 'bot/myarbitragebot.html', context)


@login_required
def get_bots(request):  # displays all visible bot on the platform
    all_bots = Bot.objects
    mine = False
    url = request.META['PATH_INFO']
    if url == '/bots/mine':
        mine = True
        all_bots = all_bots.filter(author=request.user)
    else:
        all_bots = all_bots.filter(visible='yes', root__isnull=True)

    for extra_col in ['total_prof', 'paper_prof', 'live_prof', 'candle_size_sec']:
        if extra_col == 'candle_size_sec':
            filter_obj = Case(When(candle_size__iendswith='h',
                                   then=Func(Func(F('candle_size'), Value('%l h'), function='str_to_date'),
                                             function='TIME_TO_SEC')),
                              default=Func(Func(F('candle_size'), Value('%i m'), function='str_to_date'),
                                           function='TIME_TO_SEC'))

        if extra_col == 'total_prof':
            filter_obj = Coalesce(Sum(
                Case(When(orderhistory__status='open', then=0),
                     default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                         'orderhistory__amount') - F('orderhistory__fee')) * 100 / F(
                         'orderhistory__entry_price'))), 0)

        if extra_col == 'paper_prof':
            filter_obj = Coalesce(Sum(
                Case(When(Q(orderhistory__status='open') | Q(orderhistory__paper_trading=0), then=0),
                     default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                         'orderhistory__amount') - F('orderhistory__fee')) * 100 / F(
                         'orderhistory__entry_price'))), 0)

        if extra_col == 'live_prof':
            filter_obj = Coalesce(Sum(
                Case(When(Q(orderhistory__status='open') | Q(orderhistory__paper_trading=1), then=0),
                     default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                         'orderhistory__amount') - F('orderhistory__fee')) * 100 / F(
                         'orderhistory__entry_price'))), 0)
        all_bots = all_bots.annotate(**{extra_col: filter_obj})

    # Show more than 0% for public bots
    if not mine:
        all_bots = all_bots.filter(total_prof__gte=0)

    if request.is_ajax():

        # columns = ['name', 'exchange', 'pair', 'candle_size', 'simultaneousTrades', 'strategy', 'creator',
        # 'total_prof', 'paper_prof', 'live_prof', 'status', 'visible']
        post = request.POST.copy()
        sort_by = []
        for key in post:
            if re.search('\[search]\[value]', key) is not None and post[key] != '':
                search_index = re.findall('\d+', key)
                column_name = post['columns[' + search_index[0] + '][data]']

                if column_name == 'status':
                    if post[key] == 'active':
                        all_bots = all_bots.filter(thread__isnull=False)
                    elif post[key] == 'inactive':
                        all_bots = all_bots.filter(thread__isnull=True)
                    elif post[key] == 'live':
                        all_bots = all_bots.filter(thread__isnull=False).filter(thread__mode='Live')
                    elif post[key] == 'paper':
                        all_bots = all_bots.filter(thread__isnull=False).filter(thread__mode='paper')
                elif column_name in ['total_prof', 'paper_prof', 'live_prof', 'candle_size_sec']:
                    search_key = 0 if not mine and int(post[key]) <= 0 else int(post[key])
                    all_bots = all_bots.filter(**{column_name + '__gte': search_key})
                else:
                    if post[key] != 'all':
                        search_cri = re.sub('분', 'm', post[key])
                        all_bots = all_bots.filter(**{column_name + '__icontains': search_cri})

            if re.search('^order\[[\d+]]\[column]', key) is not None and post[key] != '':
                order_index = re.findall('\d+', key)

                order_col_index = request.POST['order[' + order_index[0] + '][column]']
                order_col = request.POST['columns[' + order_col_index + '][data]']

                if order_col == 'rank':
                    order_col = 'total_prof'
                elif order_col == 'creator':
                    order_col = 'author__username'
                elif order_col == 'candle_size':
                    order_col = 'candle_size_sec'

                order_dir = '-' if request.POST['order[' + order_index[0] + '][dir]'] == 'desc' else ''
                sort_by.append(order_dir + order_col)

        all_bots = all_bots.order_by(*sort_by)

        if 'columns' in request.POST:
            all_bots = all_bots.filter(name__icontains=request.POST.get('search[value]'))

    per_page = 20
    if request.POST.get('length'):
        per_page = int(request.POST.get('length'))
    paginator = Paginator(all_bots, per_page)

    page_number = 1
    if request.POST.get('start'):
        start = int(request.POST.get('start'))
        page_number = start / per_page + 1

    page_obj = paginator.get_page(page_number)

    bots = []
    if request.is_ajax():
        lang = translation.get_language()
        humanize.i18n.activate(lang)

        for index, bot in enumerate(page_obj.object_list):
            total_profit = bot.total_profit()
            paper_profit = bot.paper_profit()
            live_profit = bot.live_profit()
            if hasattr(bot, 'thread'):
                elapsed_time = time_difference(bot.thread.start_time)
            else:
                elapsed_time = ''
            row = {
                "rank": (page_number - 1) * per_page + index + 1,
                "id": bot.id,
                "name": bot.name,
                "exchange": bot.exchange,
                "pair": bot.pair,
                "candle_size": humanize.naturaldelta(string_to_sec(bot.candle_size)),
                "simultaneousTrades": bot.simultaneousTrades,
                "strategy": bot.strategy,
                "creator": bot.author.username,
                "total_prof": total_profit,
                "paper_prof": paper_profit,
                "live_prof": live_profit,
                "visible": _(bot.visible),
                "elapsed_time": elapsed_time
            }
            if mine:
                row['status'] = hasattr(bot, 'thread')
                row['status_msg'] = _('Active') if hasattr(bot, 'thread') else _('Inactive')
                if row['status']:
                    row['mode'] = _(bot.thread.mode)
            bots.append(row)
        return JsonResponse({'data': bots, "recordsTotal": paginator.count, "recordsFiltered": paginator.count,
                             "view_mode": request.POST.get("view_mode")})

    context = {
        'bot_count': paginator.count,
        "mine": mine
    }

    return render(request, 'bot/all_bots_list.html', context)


@login_required
def activity(request, pk=None):  # displays all visible bot on the platform
    user = request.user
    order_histories = OrderHistory.objects.filter(bot__author=user, status='close')
    if pk is not None:
        order_histories = order_histories.filter(bot__pk=pk)
    # filter_obj = Coalesce(Sum(
    #     Case(When(orderhistory__status='open', then=0),
    #          default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
    #              'orderhistory__amount') - F('orderhistory__fee')))), 0)

    if request.is_ajax():

        for extra_col in ['profit', 'paper_prof', 'live_prof']:
            if extra_col == 'profit':
                filter_obj = Coalesce(Sum(
                    Case(When(status='open', then=0),
                         default=((F('exit_price') - F('entry_price')) * F('amount') - F('fee')))), 0)
            elif extra_col == 'paper_prof':
                filter_obj = Coalesce(Sum(
                    Case(When(Q(status='open') | Q(paper_trading=0), then=0),
                         default=((F('exit_price') - F('entry_price')) * F(
                             'amount') - F('fee')))), 0)
            else:
                filter_obj = Coalesce(Sum(
                    Case(When(Q(status='open') | Q(paper_trading=1), then=0),
                         default=((F('exit_price') - F('entry_price')) * F(
                             'amount') - F('fee')))), 0)

            order_histories = order_histories.annotate(**{extra_col: filter_obj})

        if 'start_time' in request.POST:
            order_histories = order_histories.filter(start_time__gte=request.POST.get('start_time'))

        if 'end_time' in request.POST:
            order_histories = order_histories.filter(end_time__lte=request.POST.get('end_time'))

        post = request.POST.copy()
        sort_by = []
        for key in post:
            if re.search('\[search]\[value]', key) is not None and post[key] != '':
                search_index = re.findall('\d+', key)
                column_name = post['columns[' + search_index[0] + '][data]']

                if column_name == 'bot':
                    order_histories = order_histories.filter(bot__name__icontains=post[key])
                elif column_name == 'paper_trading':
                    if post[key] == 'live':
                        order_histories = order_histories.filter(paper_trading=False)
                    elif post[key] == 'paper':
                        order_histories = order_histories.filter(paper_trading=True)
                else:
                    order_histories = order_histories.filter(**{column_name + '__icontains': post[key]})

            if re.search('^order\[[\d+]]\[column]', key) is not None and post[key] != '':
                order_index = re.findall('\d+', key)

                order_col_index = request.POST['order[' + order_index[0] + '][column]']
                order_col = request.POST['columns[' + order_col_index + '][data]']

                if order_col == 'no':
                    order_col = 'end_time'

                order_dir = '-' if request.POST['order[' + order_index[0] + '][dir]'] == 'desc' else ''
                sort_by.append(order_dir + order_col)

        order_histories = order_histories.order_by(*sort_by)

    per_page = 20
    if request.POST.get('length'):
        per_page = int(request.POST.get('length'))

    range_total_profit = order_histories.aggregate(
        usd_profit=Coalesce(Sum(((F('exit_price') - F('entry_price')) * F('amount') - F('fee'))), 0),
        percent_profit=Coalesce(Sum(
            ((F('exit_price') - F('entry_price')) * F('amount') - F('fee')) * 100 / F('entry_price')), 0),
    )
    range_paper_profit = order_histories.filter(status='CLOSE', paper_trading=True).values('bot_id').aggregate(
        usd_profit=Coalesce(Sum((F('exit_price') - F('entry_price')) * F('amount') - F('fee')), 0),
        percent_profit=Coalesce(Sum(
            ((F('exit_price') - F('entry_price')) * F('amount') - F('fee')) / F('entry_price') * 100), 0)
    )
    range_live_profit = order_histories.filter(status='CLOSE', paper_trading=False).aggregate(
        usd_profit=Coalesce(Sum(
            ((F('exit_price') - F('entry_price')) * F('amount') - F('fee') * 100 / F('entry_price'))), 0),
        percent_profit=Coalesce(Sum(
            ((F('exit_price') - F('entry_price')) * F('amount') - F('fee')) / F('entry_price') * 100), 0)
    )
    paginator = Paginator(order_histories, per_page)

    page_number = 1
    if request.POST.get('start'):
        start = int(request.POST.get('start'))
        page_number = start / per_page + 1

    page_obj = paginator.get_page(page_number)

    orders = []
    if request.is_ajax():
        for index, order in enumerate(page_obj.object_list):
            row = {
                "no": (page_number - 1) * per_page + index + 1,
                "bot": {'id': order.bot.id, 'name': order.bot.name},
                "exchange": order.exchange,
                "pair": order.pair,
                "amount": order.amount,
                "entry_price": order.entry_price,
                "exit_price": order.exit_price,
                "fee": order.fee,
                "start_time": order.start_time,
                "end_time": order.end_time,
                "paper_trading": order.paper_trading,
                "profit": order.profit_usd
            }
            orders.append(row)
        return JsonResponse({
            'data': orders,
            "recordsTotal": paginator.count,
            "recordsFiltered": paginator.count,
            "range_total_profit": range_total_profit,
            "range_paper_profit": range_paper_profit,
            "range_live_profit": range_live_profit
        })

    context = {
        'order_histories': page_obj,
        'total_profit': range_total_profit,
        'backtest': "",
        'live': "",
        'paper': "",
        'arbitrage': "",
    }
    if pk is not None:
        bot = Bot.objects.filter(pk=pk).first()
        context['pk'] = pk
        context['total_profit'] = bot.total_profit() if bot is not None else 0

    return render(request, 'bot/activity.html', context)


# Rank the 10 best performing bot
def ranking(request):
    all_bots = Bot.objects.filter(visible='yes', root__isnull=True)

    sort_by = 'profit_usd'
    filter_obj = Coalesce(Sum(
        Case(When(orderhistory__status='open', then=0),
             default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                 'orderhistory__amount') - F('orderhistory__fee')))), 0)

    if request.is_ajax():

        if request.POST.get('order[0][column]') is not None:
            order_col_index = request.POST['order[0][column]']
            order_col = request.POST['columns[' + order_col_index + '][data]']

            if order_col == 'rank':
                order_col = 'total_prof'
            elif order_col == 'creator':
                order_col = 'author__username'

            order_dir = '-' if request.POST['order[0][dir]'] == 'asc' else ''
            sort_by = order_dir + order_col

            if order_col == 'total_prof':
                if request.POST['unit'] == 'percent':
                    filter_obj = Coalesce(Sum(
                        Case(When(orderhistory__status='open', then=0),
                             default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                                 'orderhistory__amount') - F('orderhistory__fee')) * 100 / F(
                                 'orderhistory__entry_price'))), 0)
                else:
                    filter_obj = Coalesce(Sum(
                        Case(When(orderhistory__status='open', then=0),
                             default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                                 'orderhistory__amount') - F('orderhistory__fee')))), 0)

            if order_col == 'paper_prof':
                if request.POST['unit'] == 'percent':
                    filter_obj = Coalesce(Sum(
                        Case(When(Q(orderhistory__status='open') | Q(orderhistory__paper_trading=0), then=0),
                             default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                                 'orderhistory__amount') - F('orderhistory__fee')) * 100 / F(
                                 'orderhistory__entry_price'))), 0)
                else:
                    filter_obj = Coalesce(Sum(
                        Case(When(Q(orderhistory__status='open') | Q(orderhistory__paper_trading=0), then=0),
                             default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                                 'orderhistory__amount') - F('orderhistory__fee')))), 0)

            if order_col == 'live_prof':
                if request.POST['unit'] == 'percent':
                    filter_obj = Coalesce(Sum(
                        Case(When(Q(orderhistory__status='open') | Q(orderhistory__paper_trading=1), then=0),
                             default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                                 'orderhistory__amount') - F('orderhistory__fee')) * 100 / F(
                                 'orderhistory__entry_price'))), 0)
                else:
                    filter_obj = Coalesce(Sum(
                        Case(When(Q(orderhistory__status='open') | Q(orderhistory__paper_trading=1), then=0),
                             default=((F('orderhistory__exit_price') - F('orderhistory__entry_price')) * F(
                                 'orderhistory__amount') - F('orderhistory__fee')))), 0)

            if order_col in ['total_prof', 'paper_prof', 'live_prof']:
                all_bots = all_bots.annotate(**{order_col: filter_obj})

        all_bots = all_bots.order_by(sort_by)[:10]
    tnb = Bot.objects.filter(visible='yes', root__isnull=True).count()

    bots = []
    if request.is_ajax():
        for index, bot in enumerate(all_bots):
            total_profit = bot.total_profit()
            paper_profit = bot.paper_profit()
            live_profit = bot.live_profit()
            row = {
                "rank": index + 1,
                "name": bot.name,
                "exchange": bot.exchange,
                "pair": bot.pair,
                "candle_size": bot.candle_size,
                "simultaneousTrades": bot.simultaneousTrades,
                "strategy": bot.strategy,
                "creator": bot.author.username,
                "total_prof": total_profit,
                "paper_prof": paper_profit,
                "live_prof": live_profit
            }
            bots.append(row)
        return JsonResponse({'data': bots})

    context = {
        'bots': all_bots,
        'tnb': tnb
    }
    return render(request, 'bot/ranking.html', context)


class BotCreateView(LoginRequiredMixin, CreateView):  # used to create a bot
    model = Bot
    fields = ['name', 'exchange', 'pair', 'candle_size', 'simultaneousTrades', 'strategy', 'visible']

    def form_valid(self, form):
        form.instance.author = self.request.user

        name = form.instance.name
        argus = {'name': name, 'author': form.instance.author}
        if Bot.objects.filter(**argus).exists():
            messages.warning(self.request, gettext("name %(bot_name) already exists") % {"bot_name": name})
            return HttpResponseRedirect(reverse('create-bot-page'))
        else:
            return super().form_valid(form)


class BotUpdateView(LoginRequiredMixin, UpdateView):  # used to update an existing bot
    model = Bot
    fields = ['name', 'exchange', 'pair', 'candle_size', 'simultaneousTrades', 'strategy', 'visible']

    def form_valid(self, form):
        form.instance.author = self.request.user

        messages.success(self.request, _('Changes will be applied on next bot operation'))

        return super().form_valid(form)


class BotDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):  # used to delete a bot
    model = Bot

    def test_func(self):
        bot = self.get_object()
        if self.request.user == bot.author:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse('my-bots-page')


# def BotDeleteView(pk):
# 	bot_obj = Bot.objects.filter(pk=pk).first()
# 	bot_obj.deleted = True
# 	bot_obj.save()

# 	return reverse('mybots-page', kwargs={'slug':'-profit'} )


class ArbitrageBotCreateView(LoginRequiredMixin, CreateView):  # used to create an arbitrage bot
    model = ArbitrageBot
    fields = ['name', 'firstExchange', 'secondExchange', 'spread', 'pair']

    def form_valid(self, form):
        form.instance.author = self.request.user

        name = form.instance.name
        argus = {'name': name, 'author': form.instance.author}
        if ArbitrageBot.objects.filter(**argus).exists():
            messages.warning(self.request, 'name {} already exits'.format(name))
            return HttpResponseRedirect(reverse('myarbitbots-page'))
        else:
            return super().form_valid(form)


class ArbitrageBotUpdateView(LoginRequiredMixin, UpdateView):  # used to update an existing arbitrage bot
    model = ArbitrageBot
    fields = ['name', 'firstExchange', 'secondExchange', 'spread', 'pair']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class ArbitrageBotDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):  # used to delete an arbitrage bot
    model = ArbitrageBot

    def test_func(self):
        bot = self.get_object()
        if self.request.user == bot.author:
            return True
        else:
            return False

    def get_success_url(self):
        return reverse('myarbitbots-page')


def returnview(request):
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def bot_detail(request, pk):  # displays some detail of the bot and host the backtest
    init_users(request.user.pk)
    bot_obj = Bot.objects.filter(pk=pk).first()
    if bot_obj is None:
        return HttpResponseRedirect(reverse('my-bots-page'))
    bot_exchange = bot_obj.exchange

    # If api key is not set, redirect to profile page
    redirect_api_setting(bot_exchange, request)

    strategy_detail = get_strategy(request.LANGUAGE_CODE)
    strategy_exp = get_exp()
    strategy_links = get_links(request.LANGUAGE_CODE)

    name = bot_obj.name
    creator = bot_obj.author
    exchange = bot_obj.exchange
    candle_size = bot_obj.candle_size
    profit = '%.9f' % (bot_obj.profit)
    strategy = bot_obj.strategy
    pair = bot_obj.pair
    indicator = bot_obj.indicator
    base = pair.split('/')
    base = base[0]
    simultaneousTrades = bot_obj.simultaneousTrades

    exchanges, hold = get_exchange_hold()
    try:
        quote_currency_hold, base_currency_hold = hold[bot_exchange](pair, request.user.pk).account_hold()
    except Exception as e:
        quote_currency_hold = None

    amount = ""
    if hasattr(bot_obj, 'thread'):
        amount = bot_obj.thread.amount

    strategyexp = strategy_exp[strategy]
    strategydef = strategy_detail[strategy]
    strategylink = strategy_links[strategy]

    history = bot_obj.orderhistory_set.all()
    transactionHtml = ""
    transactionHtml2 = ""

    if len(history) > 0:
        authorspaper = {}
        authorslive = {}
        authorsgainpaper = {}
        authorsgainlive = {}
        for trade in history:
            if trade.status == 'CLOSE':
                profit = round((trade.exit_price - trade.entry_price) * float(trade.amount) - trade.fee, 9)
                script = '''
                <tr>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                    <td>{}</td>
                </tr>\n'''.format(trade.start_time, trade.amount, trade.entry_price, trade.exit_price,
                                  trade.pair, format(profit, '.9f'))

                def set_trade_history(live, gain_live):
                    user = trade.bot.author
                    if user is not None:
                        userid = user.username
                    else:
                        userid = 'deleted'
                    try:
                        live[userid] += script
                        gain_live[userid] += profit
                    except:
                        live[userid] = script
                        gain_live[userid] = profit
                    return [live, gain_live]

                if trade.paper_trading is True:
                    [authorspaper, authorsgainpaper] = set_trade_history(authorspaper, authorsgainpaper)
                else:
                    [authorslive, authorsgainlive] = set_trade_history(authorslive, authorsgainlive)

        table_index = 1
        for key, value in authorslive.items():
            transactionHtml += '''
            <tr data-toggle="collapse" id="table{}" data-target=".table{}">
                <td>{}</td>
                <td>{}</td>
                <td><button class="btn btn-default btn-sm" style="color:white">{}</button></td>
            </tr>
            <tr class="collapse table{}">
                <td colspan="999">
                    <div>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th scope="col">{}</th>
                                    <th scope="col">{}</th>
                                    <th scope="col">{}</th>
                                    <th scope="col">{}</th>
                                    <th scope="col">{}</th>
                                    <th scope="col">{}</th>
                                </tr>
                            </thead>
                            <tbody>{}</tbody>
                        </table>
                    </div>
                </td>
            </tr>'''.format(table_index, table_index, key, authorsgainlive[key], _("View More"), table_index, _("Time"),
                            _("Amount"), _("Entry Price"), _("Exit Price"), _("Currency Pair"), _("Profit"), value)

            table_index += 1

        for key, value in authorspaper.items():
            transactionHtml2 += '''
            <tr data-toggle="collapse" id="table''' + str(table_index) + '''" data-target=".table''' + str(
                table_index) + '''">
                <td>''' + str(key) + '''</td>
                <td>''' + str(authorsgainpaper[key]) + '''</td>
                <td><button class="btn btn-default btn-sm" style="color:white">''' + str(_("View More")) + '''</button></td>
            </tr>
            <tr class="collapse table''' + str(table_index) + '''">
                <td colspan="999">
                    <div>
                        <table class="table table-striped">
                            <thead>
                                <tr>
                                    <th scope="col">''' + str(_("Time")) + '''</th>
                                    <th scope="col">''' + str(_("Amount")) + '''</th>
                                    <th scope="col">''' + str(_("Entry Price")) + '''</th>
                                    <th scope="col">''' + str(_("Exit Price")) + '''</th>
                                    <th scope="col">''' + str(_("Currency Pair")) + '''</th>
                                    <th scope="col">''' + str(_("Profit")) + '''</th>
                                </tr>
                            </thead>
                            <tbody>''' + str(value) + '''</tbody>
                        </table>
                    </div>
                </td>
            </tr>'''

            table_index += 1

    lang = translation.get_language()
    humanize.i18n.activate(lang)
    context = {
        'pk': pk,
        'bot': bot_obj,
        'exchange': exchange.upper(),
        'backtest': "",
        'live': "active",
        'paper': "",
        'profile': "",
        'mybots': "",
        'aboutus-page': "",
        'amount': amount,
        'indicator': indicator,
        'candlesize': humanize.naturaldelta(string_to_sec(candle_size)),
        'strategy': strategy,
        'strategydef': strategydef,
        'strategyexp': strategyexp,
        'strategylink': strategylink,
        'pair': pair,
        'simultaneousTrades': simultaneousTrades,
        'name': name.upper(),
        'creator': creator,
        'profit': bot_obj.total_profit(),
        'base': base,
        'rawhtml': transactionHtml,
        'rawhtml2': transactionHtml2,
        'root': bot_obj.root,
        'title': 'displayname',
        'exchangeurl': 'bot/images/{}.png'.format(bot_obj.exchange),
        'quote_currency_hold': quote_currency_hold
    }
    return render(request, 'bot/bot_detail1.html', context)


def get_current_price(request):
    bots = ['aaa']
    return JsonResponse({'data': bots})


def test_page(request):
    return render(request, 'bot/test.html')


def arbbotdetail(request, pk):  # display some information about the arbitrage bot
    bot_obj = ArbitrageBot.objects.filter(pk=pk).first()
    name = bot_obj.name
    creator = bot_obj.author
    exchange1 = bot_obj.firstExchange
    exchange2 = bot_obj.secondExchange
    profit = bot_obj.profit
    pair = bot_obj.pair
    spread = bot_obj.spread

    context = {'pk': pk,
               'exchange1': exchange1,
               'exchange2': exchange2,
               'pair': pair,
               'spread': spread,
               'name': name,
               'creator': creator,
               'profit': profit,
               'firstexurl': 'bot/images/{}.png'.format(exchange1),
               'secexurl': 'bot/images/{}.png'.format(exchange2)
               }
    return render(request, 'bot/arbdescriptions.html', context)


def about_us(request):  # displays the about page

    return render(request, 'bot/about.html')


def contactus(request):  # display the contact page
    if request.method == 'POST':
        # lahadope-3191@yopmail.com
        # widebotlivechat
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        email = request.POST['email']
        # print(firstname)
        current_site = get_current_site(request)
        mail_subject = request.POST['text']
        message = 'User Firstname: ' + firstname + '\n' + 'User Lastname: ' + lastname + '\n' + 'User Email: ' + email + '\n' + \
                  request.POST['message']
        to_email = settings.EMAIL_HOST_USER
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        email.send()
        return render(request, 'bot/messagesent.html')
    return render(request, 'bot/contact.html')


@login_required
def chat(request):  # displays the chat
    profile = request.user.profile
    profile.chat_visit = datetime.now().replace(tzinfo=utc)
    profile.save()
    context = {
        'home': "",
        'backtest': "",
        'live': "",
        'paper': "",
        'arbitrage': "",
        'profile': "",
        'mybots': "",
        'aboutus': "",

    }
    return render(request, 'bot/chat.html', context)


###################################Shout########################################

def publish(request):  # save shouts to the database
    if request.method == 'POST':
        username = request.POST['username']
        comment = request.POST['comment']
        shout_obj = Shout(name=username, comment=comment, date=datetime.now().replace(tzinfo=utc))
        shout_obj.save()
    return HttpResponse('')


def load(request):  # load shouts from the database
    try:
        if request.method == 'GET':
            Shouts = Shout.objects.all()
            Shouts = list(Shouts)
            if len(Shouts) > 20:
                Shouts = Shouts[-20:]

            Shoutslist = []
            for shout in Shouts:
                Shoutsdict = {}
                Shoutsdict['name'] = shout.name
                Shoutsdict['text'] = shout.comment
                Shoutsdict['timeAgo'] = time_difference(shout.date)
                Shoutslist.append(Shoutsdict)

            return JsonResponse(Shoutslist, safe=False)
        return JsonResponse({})
    except ConnectionAbortedError:
        return None


def ping(request):
    try:
        if request.method == 'GET':
            if request.user.id is None:
                return JsonResponse({})

            profile = request.user.profile
            new = ''
            newbot = ''
            ping = ''

            Shouts = Shout.objects.all()
            if len(list(Shouts)) > 0:
                lastshout = list(Shouts)[-1]

                if '@' + str(request.user) in lastshout.comment:
                    if request.user.profile.received_notification is None:
                        profile.received_notification = datetime.now().replace(tzinfo=utc)
                        profile.save()
                        new = [lastshout.name, lastshout.comment]

                    elif lastshout.date > request.user.profile.received_notification:
                        profile.received_notification = datetime.now().replace(tzinfo=utc)
                        profile.save()
                        new = [lastshout.name, lastshout.comment]
                    if request.user.profile.chat_visit is None:
                        ping = 'true'
                    else:
                        if lastshout.date > request.user.profile.chat_visit:
                            ping = 'true'
                        else:
                            ping = 'false'

            bots = Bot.objects.all()
            if len(list(bots)) > 0:
                lastbot = list(bots)[-1]
                lengthbot = len(list(bots))
                if request.user.profile.received_new_bot_notification is None:
                    profile.received_new_bot_notification = lastbot.name
                    profile.save()
                    newbot = ['ADMIN', 'Take the time to check the bots already on the platform']

                elif lastbot.name != request.user.profile.received_new_bot_notification:
                    profile.received_new_bot_notification = lastbot.name
                    profile.save()
                    newbot = [lastbot.author.username, lastbot.name]
            return JsonResponse({'new_mess': new, 'ping': ping, 'new_bot': newbot})

        return JsonResponse({})
    except ConnectionAbortedError:
        return JsonResponse({})
    except Exception as e:
        print('error', e)
        return JsonResponse({})


def pingbot(request):
    try:
        if request.method == 'GET':
            bots = Bot.objects.all()
            lastbot = list(bots)[-1]
            profile = request.user.profile
            new = ''

            if request.user.profile.received_new_bot_notification is None:
                profile.received_new_bot_notification = datetime.now().replace(tzinfo=utc)
                profile.save()
                new = [lastbot.author, lastbot.name]

            elif lastbot.date > request.user.profile.received_notification:
                profile.received_new_bot_notification = datetime.now().replace(tzinfo=utc)
                profile.save()
                new = [lastbot.author, lastbot.name]

            return JsonResponse({'new_mess': new})

        return JsonResponse({})
    except ConnectionAbortedError:
        return None


def faq(request):  # serve the faq page
    return render(request, 'bot/faq.html')


def redirect_api_setting(bot_exchange, request):
    if bot_exchange == 'binance' and request.user.binance.binance_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'poloniex' and request.user.poloniex.poloniex_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'bitz' and request.user.bitz.bitz_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'ftx' and request.user.ftx.ftx_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'kraken' and request.user.kraken.kraken_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'bittrex' and request.user.bittrex.bittrex_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'kucoin' and request.user.kucoin.kucoin_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'digifinex' and request.user.digifinex.digifinex_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'bw' and request.user.bw.bw_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})
    elif bot_exchange == 'huobipro' and request.user.huobipro.huobipro_apikey == '':
        return render(request, 'bot/addapi.html', {'exchange': bot_exchange})


def copy_bot(request, pk):
    user = request.user
    root_bot = Bot.objects.filter(pk=pk).first()

    if user == root_bot.author:
        messages.warning(request, _('Failed copying this bot. This is your bot.'))
        return HttpResponseRedirect(reverse('detail-bot-page', args=(pk,)))

    self_copied_bot = Bot.objects.filter(author=user).filter(root=pk)
    if len(self_copied_bot) == 0:
        root_name = root_bot.name
        root_bot.pk = None  # reset bot pk
        root_bot.author = user
        root_bot.name = root_name + '(' + str(user) + 'copy)'
        root_bot.profit = 0
        root_bot.root = pk
        root_bot.save()
        messages.success(request, _('Bot is successfully copied'))
        return HttpResponseRedirect(reverse('my-bots-page'))
    else:
        messages.warning(request, _('Same bot exists, this is same bot you tried to copy.'))
        return HttpResponseRedirect(reverse('detail-bot-page', args=(self_copied_bot.first().pk,)))


def get_strategy(lang_code):
    return {
        'MACDandRSI': _('''Crossovers are one of the main moving average strategies. <br/>The first type is a price crossover, 
        which is when the price crosses above or below a moving average to signal a potential change in trend.<br/>
        <br/>Another strategy is to apply two moving averages to a chart: one longer and one shorter. 
        <br/>When the shorter-term MA crosses above the longer-term MA, it's a buy signal, as it indicates that the 
        trend is shifting up. <br/>This is known as a "<b>Golden cross</b>".<br/> 
        <br/>Meanwhile, when the shorter-term MA crosses below the longer-term MA, it's a sell signal, as it indicates 
        that the trend is shifting down. <br/>This is known as a "<b>Dead/Death cross.</b>"'''),
        'MACDandStoch': _('''Combine Macd indicator and Stochastic'''),
        'MACDgoldencross': _('''Having a strong entry strategy can increase the probability of success by confirming 
        the direction of the trend before entering a trade. <br/>In the case of the MACD crossover, the most widely 
        used entry signal is when the MACD line crosses over the signal line in the direction of the trend. 
        <br/>A bullish signal is present when the MACD line crosses ABOVE the signal line and is below the zero line. 
        When the crossover takes place, traders may look for confirmation of an upward trend by waiting for the 
        MACD line to cross over the zero line before opening a long position. 
        <br/>Likewise, a bearish signal is present when the MACD line crosses BELOW the signal line and is above the 
        zero line. Once again, confirmation can be seen when the MACD line crosses below the zero line. '''),
        'MAcrossover': _('''A moving average helps cut down the amount of "Noise" on a price chart. 
        <br/>Look at the direction of the moving average to get a basic idea of which way the price is moving. 
        <br/>If it is angled up, the price is moving up (or was recently) overall; angled down, and the price is moving 
        down overall; moving sideways, and the price is likely in a range.<br/>
        A moving average can also act as support or resistance. In an uptrend, a 50-day, 100-day or 200-day 
        moving average may act as a support level, as shown in the figure below. This is because the average 
        acts like a floor (support), so the price bounces up off of it. In a downtrend, a moving average may 
        act as resistance; like a ceiling, the price hits the level and then starts to drop again. 
        <br/><br/>
        The price won't always "Respect" the moving average in this way. The price may run through it slightly or 
        stop and reverse prior to reaching it. 
        <br/><br/>
        As a general guideline, if the price is above a moving average, the trend is up. If the price is below a 
        moving average, the trend is down. However,  moving averages can have different lengths (discussed 
        shortly), so one MA may indicate an uptrend while another MA indicates a downtrend. '''),
        'MAgoldenCross': _('''Crossovers are one of the main moving average strategies. <br/>The first type is a price 
        crossover, which is when the price crosses above or below a moving average to signal a potential change in 
        trend. <br />Another strategy is to apply two moving averages to a chart: one longer and one shorter. 
        <br/><br/>
        When the shorter-term MA crosses above the longer-term MA, it's a buy signal, as it indicates that the trend is 
        shifting up. This is known as a "<b>Golden cross.</b>" 

        Meanwhile, when the shorter-term MA crosses below the longer-term MA, it's a sell signal, as it indicates 
        that the trend is shifting down. This is known as a "<b>Dead/Death cross.</b>" '''),
        'RSIandMACross': _('''Combine RSI indicator and Moving average crossover '''),
        'RSIsignals': _('''As any other oscillator, the RSI indicator is not plotted on the price chart, but in a 
        separate window below. <br/>This technical instrument consists of a single line and two levels set by default. 
        <br><br>Vertical axis range of the indicator is set to 1 to 100 showing extremality of current price against its 
        previous values. 
        <br><br>Usually standard overbought and oversold levels are 70 and 30. If the indicator’s line goes above the 70 
        level, it signals that market is overbought and the trend may reverse downwards. 
        <br><br>If the indicator’s line goes below the level 30, it signifies that market is oversold and the trend may 
        reverse upwards. 
        <br><br>The reference level is 50, and it is the median value. If the indicator chart is ranging between the 
        levels 30 and 70, the market is flat or that the current trend is smooth, steady and there is less of a 
        likelihood for reversal in short-term 
        <br><br>Sometimes, overbought and oversold levels are set at 80 and 20 instead of 70 and 30. This setting is 
        used during increased market volatility. '''),
        'Stochcrossover': _('''The stochastic oscillator uses a quite complex mathematical formula to calculate simple 
        moving averages.<br>
        <br>%K = 100(C – L14)/(H14 – L14)
        <br>L14 = the low of the 14 previous trading sessions
        <br>Where:
        <span class="br-small pl-4">
            <span class="br-small">C = the most recent closing price</span>
            <span class="br-small">H14 = the highest price traded during the same 14-day period</span>
            <span class="br-small">%K= the current market rate for the currency pair</span>
            <span class="br-small">%D = 3-period moving average of %K</span>
        </span>
        <br>This step is similar to the previous rule, but this time we apply the rules on the 15-minute time frame: 
        wait for the Stochastic indicator to hit the 20 level and the %Kline (blue line) is crossing above the 
        %D line (orange line).  '''),
        'StochSignal': _('''This strategy uses the Stochastic indicator, enter a trade when the 
        market is oversold(below 20) and exit a trade when the market is overbought(above 80).
         <br><br>The charted stochastic oscillator actually consists of two lines: 
         <span class="br-small ml-4">the indicator itself is represented by %K, and a signal line reflecting the three-day simple moving 
         average (SMA) of %K, which is called %D. </span><br>Like other range-bound momentum oscillators, 
         such as the relative strength index (RSI) and Williams %R, the stochastic oscillator is 
        also useful for determining overbought or oversold conditions. <br>Ranging from 0 to 100, the stochastic 
        oscillator reflects overbought conditions with readings over 80 and oversold conditions with readings under 
        20.'''),
        'StoCrossSignal': _('''This strategy uses the Stochastic indicator and combine the 
        Stochcrossover strategy and the Stochsignal strategy.<br><br> The stochastic oscillator uses a quite complex 
        mathematical formula to calculate simple moving averages: 
<br>
        <br>%K = 100(C – L14)/(H14 – L14)
        <br>L14 = the low of the 14 previous trading sessions
        <br>Where:
        <span class="br-small pl-4">
            <span class="br-small">C = the most recent closing price</span>
            <span class="br-small">H14 = the highest price traded during the same 14-day period</span>
            <span class="br-small">%K= the current market rate for the currency pair</span>
            <span class="br-small">%D = 3-period moving average of %K</span>
        </span>
        <br>This step is similar to the previous rule, but this time we apply the rules on the 15-minute time frame: 
        wait for the Stochastic indicator to hit the 20 level and the %Kline (blue line) is crossing above the 
        %D line (orange line).  '''),
        'BollingerBand': _('''Bollinger Bands® are composed of three lines. 
        <br>One of the more common calculations uses a 20-day simple moving average (SMA) for the middle band. 
        <br>The upper band is calculated by taking the middle band and adding twice the daily standard deviation 
        to that amount. <br>The lower band is calculated by taking the middle band minus two times the daily standard 
        deviation.<br><br>
        The Bollinger Band® formula consists of the following:<br>
        BOLU=MA(TP,n)+m∗σ[TP,n]<br> BOLD=MA(TP,n)−m∗σ[TP,n] 
        <br>where:<br>
        <span class="br-small pl-4">
            <span class="br-small">BOLU=Upper Bollinger Band</span> 
            <span class="br-small">BOLD=Lower Bollinger Band</span> 
            <span class="br-small">MA=Moving average</span> 
            <span class="br-small">TP (typical price)=(High+Low+Close)÷3</span> 
            <span class="br-small">n=Number of days in smoothing period</span>
            <span class="br-small">m=Number of standard deviations</span>
            <span class="br-small">σ[TP,n]=Standard Deviation over last n periods of TP</span>
        </span>
        <br>Overbought and Oversold Strategy
        <br>A common approach when using Bollinger Bands® is to identify overbought or oversold market conditions. 
        <br>When the price of the asset breaks below the lower band of the Bollinger Bands®, prices have perhaps fallen 
        too much and are due to bounce. On the other hand, when price breaks above the upper band, 
         the market is perhaps overbought and due for a pullback.''')
    }


def get_exp():
    return {
        'MACDandRSI': _('''This is a strategy that combines the MACD indicator and the RSI'''),
        'MACDandStoch': _('''This is a strategy that combines the MACD indicator with the 
            Stochastic indicator.'''),
        'MACDgoldencross': _('''This is a strategy that uses the MACD indicator, enter a trade 
           when the MACD line is above the Signal line and exit when the MACD line is below the Signal line'''),
        'MAcrossover': _('''This strategy uses the Moving Average, enter a trade when the 
           Moving Average falls below the current price average and exit a trade when the Moving Average is above the 
           current price average.'''),
        'MAgoldenCross': _('''This strategy uses the Moving Average indicator, enter a trade 
           when the Moving Average of a short period falls below the Moving Average of a long period.'''),
        'RSIandMACross': _('''This strategy uses RSI and Moving Average Combined.'''),
        'RSIsignals': _('''This strategy uses RSI, enter a trade when the market is oversold(
           below 30) and exit a trade when the market is overbought(over 70).'''),
        'Stochcrossover': _('''This strategy uses the Stochastic indicator, enter a trade when 
           the Kline is above the Dline, and exit a trade when the Kline is below the Dline.'''),
        'StochSignal': _('''This strategy uses the Stochastic indicator, enter a trade when the 
           market is oversold(below 20) and exit a trade when the market is overbought(above 80).'''),
        'StoCrossSignal': _('''This strategy uses the Stochastic indicator and combine the 
           Stochcrossover strategy and the Stochsignal strategy.'''),
        'BollingerBand': _('''This strategy use the Bollinger band to assess oversold and 
           overbought signal ''')
    }


def get_links(lang):
    wiki_base_link = "https://wide-bot.gitbook.io/v/" + lang + "/"
    return {
        'MACDandRSI': [{"content": "MACD", "link": wiki_base_link + "strategies-indicators/indicators/macd"},
                       {"content": "Golden cross", "link": "http://wiki.hash.kr/index.php/%EA%B3%A8%EB%93%A0%ED"
                                                           "%81%AC%EB%A1%9C%EC%8A%A4"},
                       {"content": "RSI",
                        "link": "http://wiki.hash.kr/index.php/%EC%83%81%EB%8C%80%EA%B0%95%EB%8F%84%EC%A7%80%EC%88%98"}],
        'MACDandStoch': [],
        'MACDgoldencross': [{"content": "MACD", "link": wiki_base_link + "strategies-indicators/indicators/macd"},
                            {"content": "Golden cross", "link": "http://wiki.hash.kr/index.php/%EA%B3%A8%EB%93%A0%ED"
                                                                "%81%AC%EB%A1%9C%EC%8A%A4"}],
        'MAcrossover': [
            {"content": "MA", "link": wiki_base_link + "strategies-indicators/indicators/moving-average-ma"},
            {"content": "Golden cross", "link": "http://wiki.hash.kr/index.php/%EA%B3%A8%EB%93%A0%ED"
                                                "%81%AC%EB%A1%9C%EC%8A%A4"}],
        'MAgoldenCross': [
            {"content": "MA", "link": wiki_base_link + "strategies-indicators/indicators/moving-average-ma"},
            {"content": "Golden cross", "link": "http://wiki.hash.kr/index.php/%EA%B3%A8%EB%93%A0%ED"
                                                "%81%AC%EB%A1%9C%EC%8A%A4"}],
        'RSIandMACross': [
            {"content": "MA", "link": wiki_base_link + "strategies-indicators/indicators/moving-average-ma"},
            {"content": "Golden cross", "link": "http://wiki.hash.kr/index.php/%EA%B3%A8%EB%93%A0%ED"
                                                "%81%AC%EB%A1%9C%EC%8A%A4"},
            {"content": "RSI",
             "link": wiki_base_link + "strategies-indicators/indicators/rsi"}],
        'RSIsignals': [{"content": "RSI",
                        "link": wiki_base_link + "strategies-indicators/indicators/rsi"}],
        'Stochcrossover': [
            {"content": "Stochastic", "link": wiki_base_link + "strategies-indicators/indicators/stochastic"}],
        'StochSignal': [
            {"content": "Stochastic", "link": wiki_base_link + "strategies-indicators/indicators/stochastic"}],
        'StoCrossSignal': [
            {"content": "Stochastic", "link": wiki_base_link + "strategies-indicators/indicators/stochastic"}],
        'BollingerBand': [{"content": "Bollinger Band",
                           "link": wiki_base_link + "strategies-indicators/indicators/bollinger-band"}]
    }


def get_exchange_hold():
    exchanges = {
        'binance': binance,
        'poloniex': poloniex,
        'bittrex': bittrex,
        'ftx': ftx,
        'kraken': kraken,
        'bitz': bitz,
        'kucoin': kucoin,
        'digifinex': digifinex,
        'bw': bw,
        'huobipro': huobipro
    }

    hold = {
        'binance': BinanceGetAccount,
        'poloniex': PoloniexGetAccount,
        'bittrex': bittrexGetaccount,
        'ftx': ftxGetaccount,
        'kraken': krakenGetaccount,
        'bitz': bitzGetaccount,
        'kucoin': kucoinGetaccount,
        'digifinex': digifinexGetaccount,
        'bw': bwGetaccount,
        'huobipro': huobiproGetaccount
    }
    return exchanges, hold


def start_thread(_all_thread=None):
    if _all_thread is None:
        _all_thread = Thread.objects.all()

    for _thread in _all_thread:
        if 'arb' in _thread.name and _thread.clue == 'arbitrage':
            _thread_arb_bot = ArbitrageBot.objects.filter(name=_thread.botname).first()
            if _thread_arb_bot:
                _bot_pk = _thread_arb_bot.pk
                _mode = _thread.cursus
                _trade_amount = _thread.amount
                _exchange1 = _thread_arb_bot.firstExchange
                _exchange2 = _thread_arb_bot.secondExchange
                _bot_name = _thread_arb_bot.name
                _pair = _thread_arb_bot.pair
                _spread = _thread_arb_bot.spread
                _pk_id = _thread.author

                _arguments = [_bot_pk, _mode, _trade_amount, _thread_arb_bot, _exchange1, _exchange2, _bot_name, _pair,
                              _spread, _thread.author, _pk_id]
                _t = threading.Thread(target=getcreatelivearbitrage, name=_thread.user, args=_arguments)
                _t.setDaemon(True)
                _t.start()
        else:
            _thread_bot = _thread.bot
            if _thread_bot:
                _bot_pk = _thread_bot.pk
                _mode = _thread.mode
                _amount = _thread.amount
                _exchange = _thread_bot.exchange
                _strategy = _thread_bot.strategy
                _candle_size = _thread_bot.candle_size
                _pair = _thread_bot.pair
                _simultaneousTrades = _thread_bot.simultaneousTrades
                _author = _thread.author
                _bot_name = _thread_bot.name
                _indicator = _thread_bot.indicator
                _pk_id = _author

                _thread.name = str(_author) + ':' + str(_bot_name)

                _arguments = [_bot_pk, _mode, _amount, _thread_bot, _exchange, _strategy, _candle_size, _pair,
                              _simultaneousTrades, _author, _bot_name, _indicator, _pk_id]

                all_threads = threading.enumerate()
                result = [a for a in all_threads if type(a) is ObservableThread and a.name == _thread.name]
                if len(result) == 0:
                    _t = ObservableThread(target=getcreatelive, name=_thread.name, args=_arguments)
                    _t.setDaemon(True)
                    thread_id = _t.name
                    print(thread_id)
                    _thread.save()
                    _t.start_thread()
                else:
                    result = [a for a in result if a.is_running() is False]
                    if len(result) > 0:
                        result[0].restart_thread()


def stop_thread(_all_thread=None):
    time.sleep(int(3))
    all_threads = threading.enumerate()
    if _all_thread is None:
        _all_thread = Thread.objects.all()
    for thread in _all_thread:
        result = [a for a in all_threads if type(a) is ObservableThread and a.name == thread.name]
        if len(result) > 0:
            result[0].stop_thread()


def init_users(user_id=None):
    pairs = ['BTC/USDT', 'ETH/USDT', 'LINK/USDT', 'XRP/USDT', 'BCH/USDT', 'XTZ/USDT', 'ETH/BTC', 'LTC/USDT', 'EOS/USDT',
             'ZEC/USDT', 'XTZ/BTC', 'XMR/BTC', 'TRX/USDT', 'ADA/USDT', 'XRP/BTC', 'NEO/USDT', 'LTC/BTC', 'DASH/BTC',
             'EOS/BTC', 'DATA/BTC', 'ATOM/USDT', 'QTUM/USDT', 'ADA/BTC', 'NAV/BTC', 'ENJ/USDT', 'ALGO/USDT',
             'IOTA/USDT', 'TRX/BTC', 'LTO/BTC']
    if user_id is None:
        users = User.objects.all()
    else:
        users = User.objects.filter(pk=user_id)
    for _user in users:
        exchanges, holds = get_exchange_hold()
        if _user.binance.binance_apikey and _user.binance.binance_apikey != '' and \
                _user.binance.binance_secret and _user.binance.binance_secret != '':
            fees = holds['binance']('', _user.pk).get_account_fees()
            new_fees = {}
            for pair in pairs:
                try:
                    new_fees[pair] = {'taker': fees[pair]['taker']}
                except Exception as e:
                    print('pairs', e)
            _user.binance.fees = json.dumps(new_fees)
            _user.save()

        if _user.poloniex.poloniex_apikey and _user.poloniex.poloniex_apikey != '' and \
                _user.poloniex.poloniex_secret and _user.poloniex.poloniex_secret != '':
            fees = holds['poloniex']('', _user.pk).get_account_fees()
            new_fees = {}
            for pair in pairs:
                try:
                    new_fees[pair] = {'taker': fees[pair]['taker']}
                except Exception as e:
                    print('taker', e)
            _user.poloniex.fees = json.dumps(new_fees)
            _user.save()


def start_chart_thread():
    all_threads = threading.enumerate()
    result = [a for a in all_threads if type(a) is ObservableThread and a.name == 't_price']
    if len(result) == 0:
        _t = ObservableThread(target=chart_tick, name='t_price')
        _t.setDaemon(True)
        _t.start_thread()
    else:
        result = [a for a in result if a.is_running() is False]
        if len(result) > 0:
            result[0].restart_thread()


def stop_chart_thread():
    all_threads = threading.enumerate()
    result = [a for a in all_threads if type(a) is ObservableThread and a.name == 't_price']
    if len(result) > 0:
        result[0].stop_thread()
