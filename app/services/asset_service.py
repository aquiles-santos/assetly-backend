from typing import List, Optional
from app.repositories.asset_repository import AssetRepository
from datetime import datetime


class AssetService:
    class ValidationError(Exception):
        pass

    class DuplicateError(Exception):
        pass
    class DeletionError(Exception):
        pass

    @staticmethod
    def list_assets(
        offset: int = 0,
        limit: int = 100,
        symbol: str = None,
        name: str = None,
        asset_type: str = None,
        sector: str = None,
        order_by: str = None,
        order_dir: str = 'asc',
    ) -> List[dict]:
        assets = AssetRepository.get_filtered(
            symbol=symbol,
            name=name,
            asset_type=asset_type,
            sector=sector,
            offset=offset,
            limit=limit,
            order_by=order_by,
            order_dir=order_dir,
        )
        return [a.to_dict() for a in assets]

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

        # For a full update, require required fields
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
    def delete_asset(asset_id: int) -> bool:
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return False
        try:
            AssetRepository.delete(asset)
        except RuntimeError as e:
            if str(e) == 'pending_syncs':
                raise AssetService.DeletionError('pending_syncs')
            raise
        return True
