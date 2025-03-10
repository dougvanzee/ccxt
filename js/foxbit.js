'use strict';

//  ---------------------------------------------------------------------------

const Exchange = require ('./base/Exchange');
const { ExchangeError } = require ('./base/errors');
const Precise = require ('./base/Precise');

//  ---------------------------------------------------------------------------

module.exports = class foxbit extends Exchange {
    describe () {
        return this.deepExtend (super.describe (), {
            'id': 'foxbit',
            'name': 'FoxBit',
            'countries': [ 'BR' ],
            'has': {
                'cancelOrder': true,
                'CORS': false,
                'createMarketOrder': false,
                'createOrder': true,
                'fetchBalance': true,
                'fetchOrderBook': true,
                'fetchTicker': true,
                'fetchTrades': true,
            },
            'rateLimit': 1000,
            'version': 'v1',
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/51840849/87443320-01c0d080-c5fe-11ea-92e2-4ef56d32b026.jpg',
                'api': {
                    'public': 'https://api.blinktrade.com/api',
                    'private': 'https://api.blinktrade.com/tapi',
                },
                'www': 'https://foxbit.com.br/exchange',
                'doc': 'https://foxbit.com.br/api/',
            },
            'comment': 'Blinktrade API',
            'api': {
                'public': {
                    'get': [
                        '{currency}/ticker',    // ?crypto_currency=BTC
                        '{currency}/orderbook', // ?crypto_currency=BTC
                        '{currency}/trades',    // ?crypto_currency=BTC&since=<TIMESTAMP>&limit=<NUMBER>
                    ],
                },
                'private': {
                    'post': [
                        'D',   // order
                        'F',   // cancel order
                        'U2',  // balance
                        'U4',  // my orders
                        'U6',  // withdraw
                        'U18', // deposit
                        'U24', // confirm withdrawal
                        'U26', // list withdrawals
                        'U30', // list deposits
                        'U34', // ledger
                        'U70', // cancel withdrawal
                    ],
                },
            },
            'markets': {
                'BTC/VEF': { 'id': 'BTCVEF', 'symbol': 'BTC/VEF', 'base': 'BTC', 'quote': 'VEF', 'brokerId': 1, 'broker': 'SurBitcoin' },
                'BTC/VND': { 'id': 'BTCVND', 'symbol': 'BTC/VND', 'base': 'BTC', 'quote': 'VND', 'brokerId': 3, 'broker': 'VBTC' },
                'BTC/BRL': { 'id': 'BTCBRL', 'symbol': 'BTC/BRL', 'base': 'BTC', 'quote': 'BRL', 'brokerId': 4, 'broker': 'FoxBit' },
                'BTC/PKR': { 'id': 'BTCPKR', 'symbol': 'BTC/PKR', 'base': 'BTC', 'quote': 'PKR', 'brokerId': 8, 'broker': 'UrduBit' },
                'BTC/CLP': { 'id': 'BTCCLP', 'symbol': 'BTC/CLP', 'base': 'BTC', 'quote': 'CLP', 'brokerId': 9, 'broker': 'ChileBit' },
            },
            'options': {
                'brokerId': '4', // https://blinktrade.com/docs/#brokers
            },
        });
    }

    async fetchBalance (params = {}) {
        await this.loadMarkets ();
        const request = {
            'BalanceReqID': this.nonce (),
        };
        const response = await this.privatePostU2 (this.extend (request, params));
        const balances = this.safeValue (response['Responses'], this.options['brokerId']);
        const result = { 'info': response };
        if (balances !== undefined) {
            const currencyIds = Object.keys (this.currencies_by_id);
            for (let i = 0; i < currencyIds.length; i++) {
                const currencyId = currencyIds[i];
                const code = this.safeCurrencyCode (currencyId);
                // we only set the balance for the currency if that currency is present in response
                // otherwise we will lose the info if the currency balance has been funded or traded or not
                if (currencyId in balances) {
                    const account = this.account ();
                    let used = this.safeNumber (balances, currencyId + '_locked');
                    if (used !== undefined) {
                        used *= 1e-8;
                    }
                    let total = this.safeNumber (balances, currencyId);
                    if (total !== undefined) {
                        total *= 1e-8;
                    }
                    account['used'] = used;
                    account['total'] = total;
                    result[code] = account;
                }
            }
        }
        return this.parseBalance (result);
    }

    async fetchOrderBook (symbol, limit = undefined, params = {}) {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const request = {
            'currency': market['quote'],
            'crypto_currency': market['base'],
        };
        const response = await this.publicGetCurrencyOrderbook (this.extend (request, params));
        return this.parseOrderBook (response);
    }

    async fetchTicker (symbol, params = {}) {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const request = {
            'currency': market['quote'],
            'crypto_currency': market['base'],
        };
        const ticker = await this.publicGetCurrencyTicker (this.extend (request, params));
        const timestamp = this.milliseconds ();
        const lowercaseQuote = market['quote'].toLowerCase ();
        const quoteVolume = 'vol_' + lowercaseQuote;
        const last = this.safeNumber (ticker, 'last');
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'high': this.safeNumber (ticker, 'high'),
            'low': this.safeNumber (ticker, 'low'),
            'bid': this.safeNumber (ticker, 'buy'),
            'bidVolume': undefined,
            'ask': this.safeNumber (ticker, 'sell'),
            'askVolume': undefined,
            'vwap': undefined,
            'open': undefined,
            'close': last,
            'last': last,
            'previousClose': undefined,
            'change': undefined,
            'percentage': undefined,
            'average': undefined,
            'baseVolume': this.safeNumber (ticker, 'vol'),
            'quoteVolume': this.safeNumber (ticker, quoteVolume),
            'info': ticker,
        };
    }

    parseTrade (trade, market = undefined) {
        const timestamp = this.safeTimestamp (trade, 'date');
        const id = this.safeString (trade, 'tid');
        let symbol = undefined;
        if (market !== undefined) {
            symbol = market['symbol'];
        }
        const side = this.safeString (trade, 'side');
        const priceString = this.safeString (trade, 'price');
        const amountString = this.safeString (trade, 'amount');
        const price = this.parseNumber (priceString);
        const amount = this.parseNumber (amountString);
        const cost = this.parseNumber (Precise.stringMul (priceString, amountString));
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': this.iso8601 (timestamp),
            'symbol': symbol,
            'type': undefined,
            'side': side,
            'order': undefined,
            'takerOrMaker': undefined,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': undefined,
        };
    }

    async fetchTrades (symbol, since = undefined, limit = undefined, params = {}) {
        await this.loadMarkets ();
        const market = this.market (symbol);
        const request = {
            'currency': market['quote'],
            'crypto_currency': market['base'],
        };
        const response = await this.publicGetCurrencyTrades (this.extend (request, params));
        return this.parseTrades (response, market, since, limit);
    }

    async createOrder (symbol, type, side, amount, price = undefined, params = {}) {
        await this.loadMarkets ();
        if (type === 'market') {
            throw new ExchangeError (this.id + ' allows limit orders only');
        }
        const market = this.market (symbol);
        const orderSide = (side === 'buy') ? '1' : '2';
        const request = {
            'ClOrdID': this.nonce (),
            'Symbol': market['id'],
            'Side': orderSide,
            'OrdType': '2',
            'Price': price,
            'OrderQty': amount,
            'BrokerID': market['brokerId'],
        };
        const response = await this.privatePostD (this.extend (request, params));
        const indexed = this.indexBy (response['Responses'], 'MsgType');
        const execution = indexed['8'];
        return {
            'info': response,
            'id': execution['OrderID'],
        };
    }

    async cancelOrder (id, symbol = undefined, params = {}) {
        await this.loadMarkets ();
        return await this.privatePostF (this.extend ({
            'ClOrdID': id,
        }, params));
    }

    sign (path, api = 'public', method = 'GET', params = {}, headers = undefined, body = undefined) {
        let url = this.urls['api'][api] + '/' + this.version + '/' + this.implodeParams (path, params);
        const query = this.omit (params, this.extractParams (path));
        if (api === 'public') {
            if (Object.keys (query).length) {
                url += '?' + this.urlencode (query);
            }
        } else {
            this.checkRequiredCredentials ();
            const nonce = this.nonce ().toString ();
            const request = this.extend ({ 'MsgType': path }, query);
            body = this.json (request);
            headers = {
                'APIKey': this.apiKey,
                'Nonce': nonce,
                'Signature': this.hmac (this.encode (nonce), this.encode (this.secret)),
                'Content-Type': 'application/json',
            };
        }
        return { 'url': url, 'method': method, 'body': body, 'headers': headers };
    }

    async request (path, api = 'public', method = 'GET', params = {}, headers = undefined, body = undefined) {
        const response = await this.fetch2 (path, api, method, params, headers, body);
        if ('Status' in response) {
            if (response['Status'] !== 200) {
                throw new ExchangeError (this.id + ' ' + this.json (response));
            }
        }
        return response;
    }
};
