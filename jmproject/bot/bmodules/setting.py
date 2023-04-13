import ccxt
from django.conf import settings

# Enter API credential here

binance = ccxt.binance({
    'apiKey': settings.BINANCE_API_KEY,
    'secret': settings.BINANCE_SECRET_KEY,
})

poloniex = ccxt.poloniex({
    'apiKey': settings.POLONIEX_API_KEY,
    'secret': settings.POLONIEX_SECRET_KEY,
})

kraken = ccxt.kraken({
    'apiKey': settings.KRAKEN_API_KEY,
    'secret': settings.KRAKEN_SECRET_KEY,
    'enableRateLimit': False,
    'options': {  # ←--------------------- inside 'options' sub key
        'fetchMinOrderAmounts': False,  # ←---------- set to False 
    }
})

bittrex = ccxt.bittrex({
    'apiKey': settings.BITTREX_API_KEY,
    'secret': settings.BITTREX_SECRET_KEY,
})
ftx = ccxt.ftx({
    'apiKey': settings.FTX_API_KEY,
    'secret': settings.FTX_SECRET_KEY,
    'enableRateLimit': False
})

bitz = ccxt.bitz({
    'apiKey': settings.BITZ_API_KEY,
    'secret': settings.BITZ_SECRET_KEY,
})

bw = ccxt.bw({
    'apiKey': settings.BW_API_KEY,
    'secret': settings.BW_SECRET_KEY,
})

digifinex = ccxt.digifinex({
    'apiKey': settings.DIGIFINEX_API_KEY,
    'secret': settings.DIGIFINEX_SECRET_KEY,
})
huobipro = ccxt.huobipro({
    'apiKey': settings.HUOBIPRO_API_KEY,
    'secret': settings.HUOBIPRO_SECRET_KEY,
})
kucoin = ccxt.kucoin({
    'apiKey': settings.KUCOIN_API_KEY,
    'secret': settings.KUCOIN_SECRET_KEY,
})





