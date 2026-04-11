from datetime import datetime
from math import ceil
from time import perf_counter
from typing import Optional

from app.integrations.marketdata import MarketDataError, YahooFinanceClient
from app.repositories.asset_repository import AssetRepository


class AssetService:
    MARKET_DATA_PROVIDER = 'yahoo_finance'

    class ValidationError(Exception):
        pass

    class DuplicateError(Exception):
        pass

    class SyncError(Exception):
        pass

    @staticmethod
    def list_assets(
        page: int = 1,
        offset: int = 0,
        limit: int = 100,
        search: str = None,
        symbol: str = None,
        name: str = None,
        exchange: str = None,
        asset_type: str = None,
        sector: str = None,
        order_by: str = None,
        order_dir: str = 'asc',
    ) -> dict:
        items, total = AssetRepository.get_filtered_with_count(
            search=search,
            symbol=symbol,
            name=name,
            exchange=exchange,
            asset_type=asset_type,
            sector=sector,
            offset=offset,
            limit=limit,
            order_by=order_by,
            order_dir=order_dir,
        )

        total_pages = 1 if limit is None else ceil(total / limit) if total else 0
        return {
            'total': total,
            'page': page,
            'pages': total_pages,
            'offset': offset,
            'limit': limit,
            'data': [a.to_dict() for a in items],
        }

    @staticmethod
    def get_asset(asset_id: int) -> Optional[dict]:
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return None

        result = asset.to_dict()

        # recent market snapshots
        snapshots = AssetRepository.get_recent_snapshots(asset_id, limit=10)
        result['market_snapshots'] = [s.to_dict() for s in snapshots]

        # last external sync metadata
        last_sync = AssetRepository.get_last_sync_log(asset_id)
        result['last_sync'] = last_sync.to_dict() if last_sync else None

        return result

    @staticmethod
    def create_asset(data: dict) -> dict:
        # required fields
        required = ['symbol', 'name', 'asset_type', 'currency']
        missing = [f for f in required if not data.get(f)]
        if missing:
            raise AssetService.ValidationError(f"missing_fields: {', '.join(missing)}")

        symbol = data.get('symbol')
        # check duplicate symbol
        exists = AssetRepository.get_by_symbol(symbol)
        if exists:
            raise AssetService.DuplicateError(f"symbol_already_exists: {symbol}")

        asset = AssetRepository.create(data)
        return asset.to_dict()

    @staticmethod
    def update_asset(asset_id: int, data: dict) -> Optional[dict]:
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return None

        # For a full update (PUT) follow REST semantics: require required fields
        required = ['symbol', 'name', 'asset_type', 'currency']
        missing = [f for f in required if not data.get(f)]
        if missing:
            raise AssetService.ValidationError(f"missing_fields: {', '.join(missing)}")

        # if symbol is changing, ensure no duplicate symbol for another asset
        new_symbol = data.get('symbol')
        if new_symbol and new_symbol != asset.symbol:
            exists = AssetRepository.get_by_symbol(new_symbol)
            if exists and exists.id != asset.id:
                raise AssetService.DuplicateError(f"symbol_already_exists: {new_symbol}")

        # explicitly update `updated_at`
        data['updated_at'] = datetime.utcnow()

        updated = AssetRepository.update(asset, data)
        return updated.to_dict()

    @staticmethod
    def patch_asset(asset_id: int, data: dict) -> Optional[dict]:
        """Partial update: only apply provided fields. Do not require all required fields."""
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return None

        # If symbol provided and changing, ensure uniqueness
        new_symbol = data.get('symbol')
        if new_symbol and new_symbol != asset.symbol:
            exists = AssetRepository.get_by_symbol(new_symbol)
            if exists and exists.id != asset.id:
                raise AssetService.DuplicateError(f"symbol_already_exists: {new_symbol}")

        # Update timestamp
        data['updated_at'] = datetime.utcnow()

        updated = AssetRepository.update(asset, data)
        return updated.to_dict()

    @staticmethod
    def delete_asset(asset_id: int) -> bool:
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return False
        AssetRepository.delete(asset)
        return True

    @staticmethod
    def sync_asset(asset_id: int) -> Optional[dict]:
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return None

        requested_url = YahooFinanceClient.quote_url(asset.symbol)
        started_at = perf_counter()

        try:
            quote = YahooFinanceClient.fetch_quote(asset.symbol)
            quote_captured_at = quote['captured_at']
            synced_at = datetime.utcnow()
            asset_update = {
                'current_price': quote['current_price'],
                'open_price': quote['open_price'],
                'close_price': quote['close_price'],
                'day_high': quote['day_high'],
                'day_low': quote['day_low'],
                'volume': quote['volume'],
                'market_cap': quote['market_cap'],
                'pe_ratio': quote['pe_ratio'],
                'dividend_yield': quote['dividend_yield'],
                'updated_at': synced_at,
            }

            if quote.get('currency'):
                asset_update['currency'] = quote['currency']
            if quote.get('name'):
                asset_update['name'] = quote['name']

            updated_asset = AssetRepository.update(asset, asset_update)
            snapshot = AssetRepository.create_market_snapshot(
                asset_id=asset.id,
                price=quote['current_price'],
                captured_at=quote_captured_at,
                open_price=quote['open_price'],
                close_price=quote['close_price'],
                high_price=quote['day_high'],
                low_price=quote['day_low'],
                volume=quote['volume'],
            )
            response_time_ms = int((perf_counter() - started_at) * 1000)
            sync_log = AssetRepository.create_sync_log(
                asset_id=asset.id,
                provider_name=AssetService.MARKET_DATA_PROVIDER,
                status='success',
                synced_at=synced_at,
                message='yahoo_finance_sync_completed',
                requested_url=quote.get('requested_url', requested_url),
                response_time_ms=response_time_ms,
            )
        except MarketDataError as e:
            response_time_ms = int((perf_counter() - started_at) * 1000)
            AssetRepository.create_sync_log(
                asset_id=asset.id,
                provider_name=AssetService.MARKET_DATA_PROVIDER,
                status='failed',
                synced_at=datetime.utcnow(),
                message=str(e),
                requested_url=requested_url,
                response_time_ms=response_time_ms,
            )
            raise AssetService.SyncError(str(e)) from e
        except Exception as e:
            response_time_ms = int((perf_counter() - started_at) * 1000)
            AssetRepository.create_sync_log(
                asset_id=asset.id,
                provider_name=AssetService.MARKET_DATA_PROVIDER,
                status='failed',
                synced_at=datetime.utcnow(),
                message=f'unexpected_sync_error: {e}',
                requested_url=requested_url,
                response_time_ms=response_time_ms,
            )
            raise AssetService.SyncError('market_data_provider_error') from e

        return {
            'message': 'sync_completed',
            'asset_id': updated_asset.id,
            'asset': updated_asset.to_dict(),
            'market_snapshot': snapshot.to_dict(),
            'last_sync': sync_log.to_dict(),
        }
