import argparse
import csv
from pathlib import Path
from typing import Iterable

from app import create_app
from app.integrations.marketdata import MarketDataError, YahooFinanceClient
from app.repositories.asset_repository import AssetRepository


SYMBOL_COLUMNS = ('symbol', 'ticker', 'code', 'asset')
OVERRIDE_COLUMNS = {
    'name': str,
    'asset_type': str,
    'sector': str,
    'exchange': str,
    'currency': str,
    'notes': str,
}


def parse_args():
    parser = argparse.ArgumentParser(
        description='Import assets from a CSV file using Yahoo Finance metadata.',
    )
    parser.add_argument('csv_path', help='Path to the CSV file containing symbols.')
    parser.add_argument(
        '--update-existing',
        action='store_true',
        help='Update existing assets when the symbol already exists in the database.',
    )
    return parser.parse_args()


def _normalize_cell(value):
    if value is None:
        return None

    normalized = str(value).strip()
    return normalized or None


def _build_record(row, columns, symbol_index):
    if symbol_index >= len(row):
        return None

    symbol = _normalize_cell(row[symbol_index])
    if not symbol:
        return None

    record = {'symbol': symbol.upper()}
    for index, column_name in enumerate(columns):
        if index >= len(row) or column_name not in OVERRIDE_COLUMNS:
            continue

        value = _normalize_cell(row[index])
        if value is not None:
            record[column_name] = OVERRIDE_COLUMNS[column_name](value)

    return record


def load_records_from_rows(rows):
    if not rows:
        return []

    header = [str(cell).strip().lower() for cell in rows[0]]
    symbol_index = next(
        (index for index, name in enumerate(header) if name in SYMBOL_COLUMNS),
        None,
    )

    if symbol_index is not None:
        columns = header
        data_rows = rows[1:]
    else:
        columns = ['symbol']
        symbol_index = 0
        data_rows = rows

    records = []
    seen = set()
    for row in data_rows:
        record = _build_record(row, columns, symbol_index)
        if not record:
            continue

        symbol = record['symbol']
        if symbol in seen:
            continue

        seen.add(symbol)
        records.append(record)

    return records


def load_records(csv_path: Path):
    with csv_path.open('r', encoding='utf-8-sig', newline='') as handle:
        return load_records_from_text(handle.read())


def load_records_from_text(content: str):
    sample = content[:2048]

    try:
        dialect = csv.Sniffer().sniff(sample or 'symbol\nAAPL\n')
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(content.splitlines(), dialect)
    rows = [row for row in reader if any((cell or '').strip() for cell in row)]
    return load_records_from_rows(rows)


def build_asset_payload(record: dict):
    symbol = record['symbol']
    quote = YahooFinanceClient.fetch_quote(symbol)
    currency = quote.get('currency')
    if not currency:
        raise MarketDataError(f'missing_currency: {symbol}')

    payload = {
        'symbol': symbol,
        'name': quote.get('name') or symbol,
        'asset_type': quote.get('asset_type') or 'equity',
        'sector': quote.get('sector'),
        'exchange': quote.get('exchange'),
        'currency': currency,
        'current_price': quote.get('current_price'),
        'open_price': quote.get('open_price'),
        'close_price': quote.get('close_price'),
        'day_high': quote.get('day_high'),
        'day_low': quote.get('day_low'),
        'volume': quote.get('volume'),
        'market_cap': quote.get('market_cap'),
        'pe_ratio': quote.get('pe_ratio'),
        'dividend_yield': quote.get('dividend_yield'),
        'external_api_url': quote.get('requested_url') or YahooFinanceClient.quote_url(symbol),
        'notes': 'Imported from Yahoo Finance CSV import.',
    }

    for key in OVERRIDE_COLUMNS:
        if record.get(key) is not None:
            payload[key] = record[key]

    return payload, quote


def create_initial_snapshot(asset, quote: dict):
    current_price = quote.get('current_price')
    captured_at = quote.get('captured_at')
    if current_price is None or captured_at is None:
        return False

    AssetRepository.create_market_snapshot(
        asset_id=asset.id,
        price=current_price,
        captured_at=captured_at,
        open_price=quote.get('open_price'),
        close_price=quote.get('close_price'),
        high_price=quote.get('day_high'),
        low_price=quote.get('day_low'),
        volume=quote.get('volume'),
    )
    return True


def import_records(records: Iterable[dict], update_existing: bool = False):
    created = 0
    updated = 0
    skipped = 0
    failed = 0
    snapshots = 0

    for record in records:
        symbol = record['symbol']
        try:
            payload, quote = build_asset_payload(record)
            existing = AssetRepository.get_by_symbol(symbol)

            if existing:
                if update_existing:
                    asset = AssetRepository.update(existing, payload)
                    updated += 1
                    print(f'UPDATED {symbol}')
                    if create_initial_snapshot(asset, quote):
                        snapshots += 1
                    continue

                skipped += 1
                print(f'SKIPPED {symbol} (already exists)')
                continue

            asset = AssetRepository.create(payload)
            created += 1
            print(f'CREATED {symbol}')
            if create_initial_snapshot(asset, quote):
                snapshots += 1
        except Exception as exc:
            failed += 1
            print(f'FAILED {symbol}: {exc}')

    print(
        f'Import finished. created={created} updated={updated} '
        f'skipped={skipped} failed={failed} snapshots={snapshots}'
    )

    return {
        'created': created,
        'updated': updated,
        'skipped': skipped,
        'failed': failed,
        'snapshots': snapshots,
    }


def import_assets(csv_path: Path, update_existing: bool = False, app=None):
    records = load_records(csv_path)

    if not records:
        print('No symbols found in CSV.')
        return 0

    owns_app_context = app is None
    app = app or create_app()

    if owns_app_context:
        with app.app_context():
            summary = import_records(records, update_existing=update_existing)
    else:
        summary = import_records(records, update_existing=update_existing)

    return 1 if summary['failed'] else 0


def main():
    args = parse_args()
    csv_path = Path(args.csv_path).expanduser().resolve()
    if not csv_path.exists():
        raise SystemExit(f'CSV file not found: {csv_path}')

    raise SystemExit(import_assets(csv_path, update_existing=args.update_existing))


if __name__ == '__main__':
    main()