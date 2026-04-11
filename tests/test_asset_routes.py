import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app, db
from app.models.asset import Asset


def test_list_assets_supports_pagination_and_filters():
    app = create_app('app.config.config.TestingConfig')

    with app.app_context():
        db.create_all()
        db.session.add_all(
            [
                Asset(
                    symbol='PETR4.SA',
                    name='Petrobras PN',
                    asset_type='stock',
                    exchange='B3',
                    currency='BRL',
                    sector='Energy',
                ),
                Asset(
                    symbol='VALE3.SA',
                    name='Vale ON',
                    asset_type='stock',
                    exchange='B3',
                    currency='BRL',
                    sector='Materials',
                ),
                Asset(
                    symbol='IVVB11.SA',
                    name='ETF S&P 500',
                    asset_type='etf',
                    exchange='B3',
                    currency='BRL',
                    sector='International',
                ),
                Asset(
                    symbol='AAPL',
                    name='Apple Inc.',
                    asset_type='stock',
                    exchange='NASDAQ',
                    currency='USD',
                    sector='Technology',
                ),
            ]
        )
        db.session.commit()

    with app.test_client() as client:
        response = client.get('/api/assets?exchange=B3&type=stock&page=2&limit=1&sort=symbol')

        assert response.status_code == 200

        payload = response.get_json()
        assert payload['total'] == 2
        assert payload['page'] == 2
        assert payload['pages'] == 2
        assert payload['limit'] == 1
        assert payload['offset'] == 1
        assert len(payload['data']) == 1
        assert payload['data'][0]['symbol'] == 'VALE3.SA'
        assert payload['data'][0]['exchange'] == 'B3'
        assert payload['data'][0]['asset_type'] == 'stock'

        sector_response = client.get('/api/assets?sector=mat')

        assert sector_response.status_code == 200

        sector_payload = sector_response.get_json()
        assert sector_payload['total'] == 1
        assert len(sector_payload['data']) == 1
        assert sector_payload['data'][0]['symbol'] == 'VALE3.SA'

        search_response = client.get('/api/assets?search=vale')

        assert search_response.status_code == 200

        search_payload = search_response.get_json()
        assert search_payload['total'] == 1
        assert len(search_payload['data']) == 1
        assert search_payload['data'][0]['symbol'] == 'VALE3.SA'

        alias_response = client.get('/api/assets?q=petr4')

        assert alias_response.status_code == 200

        alias_payload = alias_response.get_json()
        assert alias_payload['total'] == 1
        assert len(alias_payload['data']) == 1
        assert alias_payload['data'][0]['symbol'] == 'PETR4.SA'

    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_list_assets_defaults_invalid_page_and_limit_values():
    app = create_app('app.config.config.TestingConfig')

    with app.app_context():
        db.create_all()
        db.session.add_all(
            [
                Asset(
                    symbol='BBDC4.SA',
                    name='Bradesco PN',
                    asset_type='stock',
                    exchange='B3',
                    currency='BRL',
                ),
                Asset(
                    symbol='ITUB4.SA',
                    name='Itau Unibanco PN',
                    asset_type='stock',
                    exchange='B3',
                    currency='BRL',
                ),
            ]
        )
        db.session.commit()

    with app.test_client() as client:
        response = client.get('/api/assets?page=0&limit=abc&sort=symbol')

        assert response.status_code == 200

        payload = response.get_json()
        assert payload['page'] == 1
        assert payload['limit'] == 50
        assert payload['offset'] == 0
        assert payload['total'] == 2
        assert payload['pages'] == 1
        assert len(payload['data']) == 2

    with app.app_context():
        db.session.remove()
        db.drop_all()