from app import db
from app.models import Asset


SEED_ASSETS = [
    {
        'symbol': 'AAPL',
        'name': 'Apple Inc.',
        'asset_type': 'equity',
        'sector': 'Technology',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'current_price': 198.11,
        'open_price': 197.42,
        'close_price': 196.98,
        'day_high': 199.05,
        'day_low': 196.74,
        'volume': 55234112,
        'market_cap': 3050000000000.0,
        'pe_ratio': 30.85,
        'dividend_yield': 0.46,
        'external_api_url': 'https://finance.yahoo.com/quote/AAPL',
        'notes': 'Development seed with static reference values for a real listed asset.',
    },
    {
        'symbol': 'MSFT',
        'name': 'Microsoft Corporation',
        'asset_type': 'equity',
        'sector': 'Technology',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'current_price': 425.37,
        'open_price': 423.9,
        'close_price': 422.84,
        'day_high': 427.18,
        'day_low': 422.25,
        'volume': 21450781,
        'market_cap': 3160000000000.0,
        'pe_ratio': 36.42,
        'dividend_yield': 0.68,
        'external_api_url': 'https://finance.yahoo.com/quote/MSFT',
        'notes': 'Development seed with static reference values for a real listed asset.',
    },
    {
        'symbol': 'GOOGL',
        'name': 'Alphabet Inc. Class A',
        'asset_type': 'equity',
        'sector': 'Communication Services',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'current_price': 157.84,
        'open_price': 156.92,
        'close_price': 156.37,
        'day_high': 158.22,
        'day_low': 155.88,
        'volume': 28744103,
        'market_cap': 1960000000000.0,
        'pe_ratio': 26.14,
        'dividend_yield': None,
        'external_api_url': 'https://finance.yahoo.com/quote/GOOGL',
        'notes': 'Development seed with static reference values for a real listed asset.',
    },
    {
        'symbol': 'AMZN',
        'name': 'Amazon.com, Inc.',
        'asset_type': 'equity',
        'sector': 'Consumer Discretionary',
        'exchange': 'NASDAQ',
        'currency': 'USD',
        'current_price': 184.76,
        'open_price': 183.55,
        'close_price': 183.11,
        'day_high': 185.44,
        'day_low': 182.7,
        'volume': 40127895,
        'market_cap': 1920000000000.0,
        'pe_ratio': 50.27,
        'dividend_yield': None,
        'external_api_url': 'https://finance.yahoo.com/quote/AMZN',
        'notes': 'Development seed with static reference values for a real listed asset.',
    },
    {
        'symbol': 'PETR4.SA',
        'name': 'Petroleo Brasileiro S.A. - Petrobras PN',
        'asset_type': 'equity',
        'sector': 'Energy',
        'exchange': 'B3',
        'currency': 'BRL',
        'current_price': 38.42,
        'open_price': 38.21,
        'close_price': 38.08,
        'day_high': 38.67,
        'day_low': 37.95,
        'volume': 46218700,
        'market_cap': 501000000000.0,
        'pe_ratio': 4.81,
        'dividend_yield': 0.142,
        'external_api_url': 'https://finance.yahoo.com/quote/PETR4.SA',
        'notes': 'Development seed with static reference values for a real listed asset.',
    },
    {
        'symbol': 'VALE3.SA',
        'name': 'Vale S.A.',
        'asset_type': 'equity',
        'sector': 'Materials',
        'exchange': 'B3',
        'currency': 'BRL',
        'current_price': 61.35,
        'open_price': 60.92,
        'close_price': 60.88,
        'day_high': 61.58,
        'day_low': 60.41,
        'volume': 28113400,
        'market_cap': 278000000000.0,
        'pe_ratio': 6.73,
        'dividend_yield': 0.091,
        'external_api_url': 'https://finance.yahoo.com/quote/VALE3.SA',
        'notes': 'Development seed with static reference values for a real listed asset.',
    },
]


def seed_assets():
    db.session.add_all(Asset(**asset_data) for asset_data in SEED_ASSETS)
    db.session.commit()


def init_db(app, reset: bool = False):
    with app.app_context():
        import app.models  # noqa: F401

        if reset:
            db.drop_all()

        db.create_all()


def seed_db(app):
    with app.app_context():
        if not Asset.query.first():
            seed_assets()
