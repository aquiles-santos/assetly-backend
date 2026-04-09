from datetime import datetime, timezone

import yfinance as yf


class MarketDataError(Exception):
    pass


class YahooFinanceClient:
    BASE_URL = 'https://finance.yahoo.com'

    ASSET_TYPE_MAP = {
        'EQUITY': 'equity',
        'ETF': 'etf',
        'MUTUALFUND': 'fund',
        'INDEX': 'index',
        'CURRENCY': 'forex',
        'CRYPTOCURRENCY': 'crypto',
    }

    @classmethod
    def quote_url(cls, symbol: str) -> str:
        return f'{cls.BASE_URL}/quote/{symbol}'

    @staticmethod
    def _to_float(value):
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _to_int(value):
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _normalize_dividend_yield(value):
        value = YahooFinanceClient._to_float(value)
        if value is None:
            return None
        return value / 100 if value > 1 else value

    @staticmethod
    def _parse_timestamp(value):
        if value is None:
            return datetime.utcnow()
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc).replace(tzinfo=None)
        return datetime.utcnow()

    @classmethod
    def _normalize_asset_type(cls, value):
        if not value:
            return 'equity'

        normalized = str(value).strip().upper().replace(' ', '')
        return cls.ASSET_TYPE_MAP.get(normalized, str(value).strip().lower())

    @classmethod
    def fetch_quote(cls, symbol: str) -> dict:
        ticker = yf.Ticker(symbol)
        fast_info = dict(ticker.fast_info or {})
        info = dict(ticker.info or {})

        current_price = cls._to_float(
            fast_info.get('lastPrice') or info.get('regularMarketPrice')
        )
        if current_price is None:
            raise MarketDataError(f'quote_unavailable: {symbol}')

        return {
            'symbol': symbol,
            'name': info.get('longName') or info.get('shortName'),
            'asset_type': cls._normalize_asset_type(info.get('quoteType')),
            'sector': info.get('sector') or info.get('category'),
            'exchange': info.get('fullExchangeName') or info.get('exchange') or fast_info.get('exchange'),
            'currency': info.get('currency') or fast_info.get('currency'),
            'current_price': current_price,
            'open_price': cls._to_float(fast_info.get('open') or info.get('regularMarketOpen')),
            'close_price': cls._to_float(
                fast_info.get('previousClose') or info.get('regularMarketPreviousClose')
            ),
            'day_high': cls._to_float(fast_info.get('dayHigh') or info.get('regularMarketDayHigh')),
            'day_low': cls._to_float(fast_info.get('dayLow') or info.get('regularMarketDayLow')),
            'volume': cls._to_int(
                fast_info.get('lastVolume') or info.get('regularMarketVolume') or info.get('volume')
            ),
            'market_cap': cls._to_float(fast_info.get('marketCap') or info.get('marketCap')),
            'pe_ratio': cls._to_float(info.get('trailingPE')),
            'dividend_yield': cls._normalize_dividend_yield(
                info.get('dividendYield') or info.get('trailingAnnualDividendYield')
            ),
            'captured_at': cls._parse_timestamp(
                fast_info.get('regularMarketTime') or info.get('regularMarketTime')
            ),
            'requested_url': cls.quote_url(symbol),
        }