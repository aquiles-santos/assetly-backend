import pathlib
import sys
from datetime import datetime

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app, db
from app.integrations.marketdata import YahooFinanceClient
from app.models.asset import Asset


def test_sync_updates_asset_prices_and_snapshot(monkeypatch):
    app = create_app('app.config.config.TestingConfig')

    with app.app_context():
        db.create_all()
        asset = Asset(
            symbol='VALE3.SA',
            name='Vale S.A.',
            asset_type='equity',
            exchange='B3',
            currency='BRL',
            current_price=61.35,
        )
        db.session.add(asset)
        db.session.commit()
        asset_id = asset.id

    captured_at = datetime(2026, 4, 9, 17, 7, 49)

    def fake_fetch_quote(symbol):
        assert symbol == 'VALE3.SA'
        return {
            'symbol': symbol,
            'name': 'Vale S.A.',
            'exchange': 'SAO',
            'currency': 'BRL',
            'current_price': 85.59,
            'open_price': 86.5,
            'close_price': 83.69,
            'day_high': 86.72,
            'day_low': 84.73,
            'volume': 24942400,
            'market_cap': 365427718864.92,
            'pe_ratio': 30.14,
            'dividend_yield': 0.0824,
            'captured_at': captured_at,
            'requested_url': YahooFinanceClient.quote_url(symbol),
        }

    monkeypatch.setattr(YahooFinanceClient, 'fetch_quote', fake_fetch_quote)

    with app.test_client() as client:
        sync_response = client.post(f'/api/assets/{asset_id}/sync')
        assert sync_response.status_code == 200

        payload = sync_response.get_json()
        assert payload['asset']['current_price'] == 85.59
        assert payload['market_snapshot']['price'] == 85.59
        assert payload['last_sync']['status'] == 'success'
        assert payload['last_sync']['provider_name'] == 'yahoo_finance'

        asset_response = client.get(f'/api/assets/{asset_id}')
        assert asset_response.status_code == 200

        asset_payload = asset_response.get_json()
        assert asset_payload['current_price'] == 85.59
        assert asset_payload['open_price'] == 86.5
        assert asset_payload['close_price'] == 83.69
        assert asset_payload['day_high'] == 86.72
        assert asset_payload['day_low'] == 84.73
        assert asset_payload['volume'] == 24942400
        assert asset_payload['market_cap'] == 365427718864.92
        assert asset_payload['pe_ratio'] == 30.14
        assert asset_payload['dividend_yield'] == 0.0824
        assert asset_payload['last_sync']['message'] == 'yahoo_finance_sync_completed'
        assert asset_payload['last_sync']['provider_name'] == 'yahoo_finance'
        assert asset_payload['market_snapshots'][0]['price'] == 85.59

    with app.app_context():
        db.session.remove()
        db.drop_all()