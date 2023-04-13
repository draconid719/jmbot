from datetime import datetime, timedelta
import humanize
import pytz
from django.utils import translation

utc = pytz.UTC


def date_to_unix_milli(date):
    ini_t = datetime.strptime("Jan 1 70", "%b %d %y")
    da = datetime.strptime(date, "%Y-%m-%d")
    uni = da - ini_t
    uni = (uni.total_seconds()) * 1000
    return int(uni)


def date_precise_to_unix_milli(date):
    ini_t = datetime.strptime("Jan 1 70", "%b %d %y")
    da = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    uni = da - ini_t
    uni = (uni.total_seconds()) * 1000
    return int(uni)


def unix_milli_to_date(unix):
    print(unix)
    unix = int(float(unix) / 1000)
    ini_t = datetime.strptime("Jan 1 70", "%b %d %y")
    da = ini_t + timedelta(seconds=unix)

    return da


def string_to_sec(period):
    candle = {'1m': 60, '3m': 180, '5m': 300, '15m': 900, '30m': 1800,
              '1h': 3600, '2h': 7200, '4h': 14400, '6h': 2600,
              '8h': 28800, '12h': 43200, '1d': 86400, '3d': 259200}
    return candle[period]


def time_difference(end):
    lang = translation.get_language()
    humanize.i18n.activate(lang)
    now = datetime.now().replace(tzinfo=utc)
    end = end.replace(tzinfo=utc)
    diff = now - end

    total = diff.total_seconds()
    ago = humanize.naturaldelta(datetime.now() - timedelta(seconds=total))
    return ago


def inappropriate_char(string):
    keyword = ['RSI period', 'MA period', 'MAfast period', 'MAslow period', 'MACD fast', 'MACD slow', 'RSI period',
               'Stochastic period', 'Smoothing',
               ]
    flag = ''
    for elt in keyword:
        if elt in string:
            flag = True
    return flag
