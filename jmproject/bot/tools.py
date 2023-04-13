from datetime import datetime
import pytz
from django.contrib.auth.models import User
from bot.models import Bot, Thread

utc = pytz.UTC
author = User.objects.filter(username='crypto').first()
exchanges = ['poloniex']
candle_sizes = ['1m', '3m', '5m', '15m', '30m']
simultaneous_trades_numbers = [1, 3, 5]
strategies = ['MACDgoldencross', 'RSIsignals', 'MAcrossover', 'MAgoldenCross', 'MACDandRSI', 'RSIandMACross',
              'StochSignal', 'Stochcrossover', 'MACDandStoch', 'StoCrossSignal', 'BollingerBand']

for exchange in exchanges:
    for strategy in strategies:
        for candle_size in candle_sizes:
            for simultaneousTrades in simultaneous_trades_numbers:
                name = f'{exchange}_{strategy}_{candle_size}_{simultaneousTrades}'
                bot = Bot.objects.filter(name=name).first()
                if bot is None:
                    bot = Bot(name=name, exchange=exchange, author=author, candle_size=candle_size, strategy=strategy,
                              simultaneousTrades=simultaneousTrades)
                    bot.save()
                    print(bot)
                else:
                    print('bot_exist')

                if hasattr(bot, 'thread') is False:
                    thr_obj = Thread(bot=bot, name=f'{author.pk}:{name}', amount=1, mode='Paper',
                                     author=author.pk, start_time=datetime.now().replace(tzinfo=utc),
                                     clue='market')
                    thr_obj.save()
                    print(thr_obj)
                else:
                    print('thread_exist')
