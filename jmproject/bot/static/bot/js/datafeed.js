'use strict';

const lastBarsCache = new Map();

var Datafeed = {
    onReady: function onReady(callback) {
        console.log('[onReady]: Method call');
        setTimeout(() => callback(configurationData));
    },
    searchSymbols: async function searchSymbols(userInput, exchange, symbolType, onResultReadyCallback) {
        console.log('[searchSymbols]: Method call');
        const symbols = await getAllSymbols();
        const newSymbols = symbols.filter(symbol => {
            const isExchangeValid = exchange === '' || symbol.exchange === exchange;
            const isFullSymbolContainsInput = symbol.full_name
                .toLowerCase()
                .indexOf(userInput.toLowerCase()) !== -1;
            return isExchangeValid && isFullSymbolContainsInput;
        });
        onResultReadyCallback(newSymbols);
    },
    resolveSymbol: async function resolveSymbol(symbolName, onSymbolResolvedCallback, onResolveErrorCallback) {
        console.log('[resolveSymbol]: Method call', symbolName);
        const symbols = await getAllSymbols();
        const symbolItem = symbols.find(({ full_name }) => full_name === symbolName);
        if (!symbolItem) {
            console.log('[resolveSymbol]: Cannot resolve symbol', symbolName);
            onResolveErrorCallback('cannot resolve symbol');
            return;
        }
        const symbolInfo = {
            ticker: symbolItem.full_name,
            name: symbolItem.symbol,
            description: symbolItem.description,
            type: symbolItem.type,
            session: '24x7',
            timezone: 'Etc/UTC',
            exchange: symbolItem.exchange,
            minmov: 1,
            pricescale: 100,
            has_intraday: true,
            has_no_volume: true,
            has_weekly_and_monthly: false,
            supported_resolutions: configurationData.supported_resolutions,
            volume_precision: 2,
            data_status: 'streaming',
        };

        console.log('[resolveSymbol]: Symbol resolved', symbolName);
        onSymbolResolvedCallback(symbolInfo);
    },
    getBars: async function getBars(symbolInfo, resolution, periodParams, onHistoryCallback, onErrorCallback) {
        const { from, to, firstDataRequest } = periodParams;
        console.log('[getBars]: Method call', symbolInfo, resolution, from, to);
        const parsedSymbol = parseFullSymbol(symbolInfo.full_name);
        const urlParameters = {
            e: parsedSymbol.exchange,
            fsym: parsedSymbol.fromSymbol,
            tsym: parsedSymbol.toSymbol,
            toTs: to,
            limit: 2000,
        };
        const query = Object.keys(urlParameters)
            .map(name => `${name}=${encodeURIComponent(urlParameters[name])}`)
                .join('&');
        try {
            var data;
            console.log(resolution)
            if (['1', '3', '5', '15', '30'].includes(resolution)) {
                data = await makeApiRequest(`data/histominute?${query}`);
            } else if (['60', '120', '240', '360', '480', '720'].includes(resolution)) {
                data = await makeApiRequest(`data/histohour?${query}`);
            } else {
                data = await makeApiRequest(`data/histoday?${query}`);
            }

            if (data.Response && data.Response === 'Error' || data.Data.length === 0) {
                // "noData" should be set if there is no data in the requested period.
                onHistoryCallback([], { noData: true });
                return;
            }
            let bars = [];
            data.Data.forEach(bar => {
                if (bar.time >= from && bar.time < to) {
                    bars = [...bars, {
                        time: bar.time * 1000,
                        low: bar.low,
                        high: bar.high,
                        open: bar.open,
                        close: bar.close,
                    }];
                }
            });

            if (firstDataRequest) {
                lastBarsCache.set(symbolInfo.full_name, { ...bars[bars.length - 1] });
            }
            console.log(`[getBars]: returned ${bars.length} bar(s)`);
            onHistoryCallback(bars, { noData: false });
        } catch (error) {
            console.log('[getBars]: Get error', error);
            onErrorCallback(error);
        }
    },
    subscribeBars: function subscribeBars(symbolInfo, resolution, onRealtimeCallback, subscribeUID, onResetCacheNeededCallback) {
        console.log('[subscribeBars]: Method call with subscribeUID:', subscribeUID);
        subscribeOnStream(
            symbolInfo,
            resolution,
            onRealtimeCallback,
            subscribeUID,
            onResetCacheNeededCallback,
            lastBarsCache.get(symbolInfo.full_name)
        );
    },
    unsubscribeBars: function unsubscribeBars(subscriberUID) {
        console.log('[unsubscribeBars]: Method call with subscriberUID:', subscriberUID);
        unsubscribeFromStream(subscriberUID);
    }
};

var configurationData = {
    supported_resolutions: ['1', '3', '5', '15', '30', '60', '120', '240', '360', '480', '720', '1D', '3D'],
    exchanges: [
        {
          value: 'Binance',
          name: 'Binance',
          desc: 'Binance'
        },
        {
          value: 'Poloniex',
          name: 'Poloniex',
          desc: 'Poloniex'
        },
        {
            value: 'BitZ',
            name: 'BitZ',
            desc: 'BitZ',
        },
        {
            value: 'ftx',
            name: 'ftx',
            desc: 'ftx',
        },
        {
            value: 'Kucoin',
            name: 'Kucoin',
            desc: 'Kucoin',
        },
        {
            value: 'DigiFinex',
            name: 'DigiFinex',
            desc: 'DigiFinex',
        },
        {
            value: 'bw',
            name: 'bw',
            desc: 'bw',
        },
        {
            value: 'HuobiPro',
            name: 'HuobiPro',
            desc: 'HuobiPro',
        },
        {
            value: 'BitTrex',
            name: 'BitTrex',
            desc: 'BitTrex',
        },
        {
            // `exchange` argument for the `searchSymbols` method, if a user selects this exchange
            value: 'Kraken',
            // filter name
            name: 'Kraken',
            // full exchange name displayed in the filter popup
            desc: 'Kraken bitcoin exchange',
        },
    ],
    symbols_types: [
        {
            name: 'crypto',

            // `symbolType` argument for the `searchSymbols` method, if a user selects this symbol type
            value: 'crypto',
        },
    ],
};

// Make requests to CryptoCompare API
async function makeApiRequest(path) {
    try {
        var response = await fetch("https://min-api.cryptocompare.com/" + path);
        return response.json();
    } catch (error) {
        throw new Error("CryptoCompare request error: " + error.status);
    }
}

// Generate a symbol ID from a pair of the coins
function generateSymbol(exchange, fromSymbol, toSymbol) {
    var short = fromSymbol + "/" + toSymbol;
    return {
        short: short,
        full: exchange + ":" + short
    };
}

async function getAllSymbols() {
    const data = await makeApiRequest('data/v3/all/exchanges');
    let allSymbols = [];

    for (const exchange of configurationData.exchanges) {
        const pairs = data.Data[exchange.value].pairs;

        for (const leftPairPart of Object.keys(pairs)) {
            const symbols = pairs[leftPairPart].map(rightPairPart => {
                const symbol = generateSymbol(exchange.value, leftPairPart, rightPairPart);
                return {
                    symbol: symbol.short,
                    full_name: symbol.full,
                    description: symbol.short,
                    exchange: exchange.value,
                    type: 'crypto',
                };
            });
            allSymbols = [...allSymbols, ...symbols];
        }
    }
    return allSymbols;
}

function parseFullSymbol(fullSymbol) {
    var match = fullSymbol.match(/^(\w+):(\w+)\/(\w+)$/);
    if (!match) {
        return null;
    }

    return { exchange: match[1], fromSymbol: match[2], toSymbol: match[3] };
}