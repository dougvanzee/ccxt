# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import BadSymbol
from ccxt.base.errors import NotSupported
from ccxt.base.precise import Precise


class bitstamp1(Exchange):

    def describe(self):
        return self.deep_extend(super(bitstamp1, self).describe(), {
            'id': 'bitstamp1',
            'name': 'Bitstamp',
            'countries': ['GB'],
            'rateLimit': 1000,
            'version': 'v1',
            'has': {
                'cancelOrder': True,
                'CORS': True,
                'createOrder': True,
                'fetchBalance': True,
                'fetchMyTrades': True,
                'fetchOrder': False,
                'fetchOrderBook': True,
                'fetchTicker': True,
                'fetchTrades': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27786377-8c8ab57e-5fe9-11e7-8ea4-2b05b6bcceec.jpg',
                'api': 'https://www.bitstamp.net/api',
                'www': 'https://www.bitstamp.net',
                'doc': 'https://www.bitstamp.net/api',
            },
            'requiredCredentials': {
                'apiKey': True,
                'secret': True,
                'uid': True,
            },
            'api': {
                'public': {
                    'get': [
                        'ticker',
                        'ticker_hour',
                        'order_book',
                        'transactions',
                        'eur_usd',
                    ],
                },
                'private': {
                    'post': [
                        'balance',
                        'user_transactions',
                        'open_orders',
                        'order_status',
                        'cancel_order',
                        'cancel_all_orders',
                        'buy',
                        'sell',
                        'bitcoin_deposit_address',
                        'unconfirmed_btc',
                        'ripple_withdrawal',
                        'ripple_address',
                        'withdrawal_requests',
                        'bitcoin_withdrawal',
                    ],
                },
            },
            'markets': {
                'BTC/USD': {'id': 'btcusd', 'symbol': 'BTC/USD', 'base': 'BTC', 'quote': 'USD', 'baseId': 'btc', 'quoteId': 'usd', 'maker': 0.005, 'taker': 0.005},
                'BTC/EUR': {'id': 'btceur', 'symbol': 'BTC/EUR', 'base': 'BTC', 'quote': 'EUR', 'baseId': 'btc', 'quoteId': 'eur', 'maker': 0.005, 'taker': 0.005},
                'EUR/USD': {'id': 'eurusd', 'symbol': 'EUR/USD', 'base': 'EUR', 'quote': 'USD', 'baseId': 'eur', 'quoteId': 'usd', 'maker': 0.005, 'taker': 0.005},
                'XRP/USD': {'id': 'xrpusd', 'symbol': 'XRP/USD', 'base': 'XRP', 'quote': 'USD', 'baseId': 'xrp', 'quoteId': 'usd', 'maker': 0.005, 'taker': 0.005},
                'XRP/EUR': {'id': 'xrpeur', 'symbol': 'XRP/EUR', 'base': 'XRP', 'quote': 'EUR', 'baseId': 'xrp', 'quoteId': 'eur', 'maker': 0.005, 'taker': 0.005},
                'XRP/BTC': {'id': 'xrpbtc', 'symbol': 'XRP/BTC', 'base': 'XRP', 'quote': 'BTC', 'baseId': 'xrp', 'quoteId': 'btc', 'maker': 0.005, 'taker': 0.005},
                'LTC/USD': {'id': 'ltcusd', 'symbol': 'LTC/USD', 'base': 'LTC', 'quote': 'USD', 'baseId': 'ltc', 'quoteId': 'usd', 'maker': 0.005, 'taker': 0.005},
                'LTC/EUR': {'id': 'ltceur', 'symbol': 'LTC/EUR', 'base': 'LTC', 'quote': 'EUR', 'baseId': 'ltc', 'quoteId': 'eur', 'maker': 0.005, 'taker': 0.005},
                'LTC/BTC': {'id': 'ltcbtc', 'symbol': 'LTC/BTC', 'base': 'LTC', 'quote': 'BTC', 'baseId': 'ltc', 'quoteId': 'btc', 'maker': 0.005, 'taker': 0.005},
                'ETH/USD': {'id': 'ethusd', 'symbol': 'ETH/USD', 'base': 'ETH', 'quote': 'USD', 'baseId': 'eth', 'quoteId': 'usd', 'maker': 0.005, 'taker': 0.005},
                'ETH/EUR': {'id': 'etheur', 'symbol': 'ETH/EUR', 'base': 'ETH', 'quote': 'EUR', 'baseId': 'eth', 'quoteId': 'eur', 'maker': 0.005, 'taker': 0.005},
                'ETH/BTC': {'id': 'ethbtc', 'symbol': 'ETH/BTC', 'base': 'ETH', 'quote': 'BTC', 'baseId': 'eth', 'quoteId': 'btc', 'maker': 0.005, 'taker': 0.005},
            },
        })

    async def fetch_order_book(self, symbol, limit=None, params={}):
        if symbol != 'BTC/USD':
            raise ExchangeError(self.id + ' ' + self.version + " fetchOrderBook doesn't support " + symbol + ', use it for BTC/USD only')
        await self.load_markets()
        orderbook = await self.publicGetOrderBook(params)
        timestamp = self.safe_timestamp(orderbook, 'timestamp')
        return self.parse_order_book(orderbook, timestamp)

    async def fetch_ticker(self, symbol, params={}):
        if symbol != 'BTC/USD':
            raise ExchangeError(self.id + ' ' + self.version + " fetchTicker doesn't support " + symbol + ', use it for BTC/USD only')
        await self.load_markets()
        ticker = await self.publicGetTicker(params)
        timestamp = self.safe_timestamp(ticker, 'timestamp')
        vwap = self.safe_number(ticker, 'vwap')
        baseVolume = self.safe_number(ticker, 'volume')
        quoteVolume = None
        if baseVolume is not None and vwap is not None:
            quoteVolume = baseVolume * vwap
        last = self.safe_number(ticker, 'last')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': self.safe_number(ticker, 'high'),
            'low': self.safe_number(ticker, 'low'),
            'bid': self.safe_number(ticker, 'bid'),
            'bidVolume': None,
            'ask': self.safe_number(ticker, 'ask'),
            'askVolume': None,
            'vwap': vwap,
            'open': self.safe_number(ticker, 'open'),
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': None,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    def parse_trade(self, trade, market=None):
        timestamp = self.safe_timestamp_2(trade, 'date', 'datetime')
        side = 'buy' if (trade['type'] == 0) else 'sell'
        orderId = self.safe_string(trade, 'order_id')
        if 'currency_pair' in trade:
            if trade['currency_pair'] in self.markets_by_id:
                market = self.markets_by_id[trade['currency_pair']]
        id = self.safe_string(trade, 'tid')
        priceString = self.safe_string(trade, 'price')
        amountString = self.safe_string(trade, 'amount')
        price = self.parse_number(priceString)
        amount = self.parse_number(amountString)
        cost = self.parse_number(Precise.string_mul(priceString, amountString))
        symbol = None
        if market is not None:
            symbol = market['symbol']
        return {
            'id': id,
            'info': trade,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': orderId,
            'type': None,
            'side': side,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': cost,
            'fee': None,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        if symbol != 'BTC/USD':
            raise BadSymbol(self.id + ' ' + self.version + " fetchTrades doesn't support " + symbol + ', use it for BTC/USD only')
        await self.load_markets()
        market = self.market(symbol)
        request = {
            'time': 'minute',
        }
        response = await self.publicGetTransactions(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    async def fetch_balance(self, params={}):
        balance = await self.privatePostBalance(params)
        result = {'info': balance}
        codes = list(self.currencies.keys())
        for i in range(0, len(codes)):
            code = codes[i]
            currency = self.currency(code)
            currencyId = currency['id']
            account = self.account()
            account['free'] = self.safe_string(balance, currencyId + '_available')
            account['used'] = self.safe_string(balance, currencyId + '_reserved')
            account['total'] = self.safe_string(balance, currencyId + '_balance')
            result[code] = account
        return self.parse_balance(result, False)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        if type != 'limit':
            raise ExchangeError(self.id + ' ' + self.version + ' accepts limit orders only')
        if symbol != 'BTC/USD':
            raise ExchangeError(self.id + ' v1 supports BTC/USD orders only')
        await self.load_markets()
        method = 'privatePost' + self.capitalize(side)
        request = {
            'amount': amount,
            'price': price,
        }
        response = await getattr(self, method)(self.extend(request, params))
        id = self.safe_string(response, 'id')
        return {
            'info': response,
            'id': id,
        }

    async def cancel_order(self, id, symbol=None, params={}):
        return await self.privatePostCancelOrder({'id': id})

    def parse_order_status(self, status):
        statuses = {
            'In Queue': 'open',
            'Open': 'open',
            'Finished': 'closed',
            'Canceled': 'canceled',
        }
        return self.safe_string(statuses, status, status)

    async def fetch_order_status(self, id, symbol=None, params={}):
        await self.load_markets()
        request = {
            'id': id,
        }
        response = await self.privatePostOrderStatus(self.extend(request, params))
        return self.parse_order_status(response)

    async def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        market = None
        if symbol is not None:
            market = self.market(symbol)
        pair = market['id'] if market else 'all'
        request = {
            'id': pair,
        }
        response = await self.privatePostOpenOrdersId(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    async def fetch_order(self, id, symbol=None, params={}):
        raise NotSupported(self.id + ' fetchOrder is not implemented yet')

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        query = self.omit(params, self.extract_params(path))
        if api == 'public':
            if query:
                url += '?' + self.urlencode(query)
        else:
            self.check_required_credentials()
            nonce = str(self.nonce())
            auth = nonce + self.uid + self.apiKey
            signature = self.encode(self.hmac(self.encode(auth), self.encode(self.secret)))
            query = self.extend({
                'key': self.apiKey,
                'signature': signature.upper(),
                'nonce': nonce,
            }, query)
            body = self.urlencode(query)
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def request(self, path, api='public', method='GET', params={}, headers=None, body=None):
        response = await self.fetch2(path, api, method, params, headers, body)
        if 'status' in response:
            if response['status'] == 'error':
                raise ExchangeError(self.id + ' ' + self.json(response))
        return response
