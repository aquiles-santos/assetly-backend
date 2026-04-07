from typing import List, Optional
from app.repositories.asset_repository import AssetRepository


class AssetService:
    @staticmethod
    def list_assets(offset: int = 0, limit: int = 100) -> List[dict]:
        assets = AssetRepository.get_all(offset=offset, limit=limit)
        return [a.to_dict() for a in assets]

    @staticmethod
    def get_asset(asset_id: int) -> Optional[dict]:
        asset = AssetRepository.get_by_id(asset_id)
        return asset.to_dict() if asset else None

    @staticmethod
    def create_asset(data: dict) -> dict:
        asset = AssetRepository.create(data)
        return asset.to_dict()

    @staticmethod
    def update_asset(asset_id: int, data: dict) -> Optional[dict]:
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return None
        updated = AssetRepository.update(asset, data)
        return updated.to_dict()

    @staticmethod
    def delete_asset(asset_id: int) -> bool:
        asset = AssetRepository.get_by_id(asset_id)
        if not asset:
            return False
        AssetRepository.delete(asset)
        return True
