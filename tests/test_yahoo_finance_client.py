import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.integrations.marketdata.yahoo_finance_client import YahooFinanceClient


class FakeTicker:
    def __init__(self):
        self.fast_info = {
            'lastPrice': 373.07000732421875,
            'previousClose': 374.0,
        }
        self.info = {
            'longName': 'Microsoft Corporation',
            'quoteType': 'EQUITY',
            'currency': 'USD',
            'regularMarketPrice': 373.07000732421875,
            'regularMarketPreviousClose': 374.33,
            'previousClose': 374.33,
        }


def test_fetch_quote_prefers_regular_market_previous_close(monkeypatch):
    monkeypatch.setattr(
        'app.integrations.marketdata.yahoo_finance_client.yf.Ticker',
        lambda symbol: FakeTicker(),
    )

    payload = YahooFinanceClient.fetch_quote('MSFT')

    assert payload['current_price'] == 373.07000732421875
    assert payload['close_price'] == 374.33