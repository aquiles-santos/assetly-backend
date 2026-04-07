from typing import Optional, List
from app import db
from app.models.asset import Asset


class AssetRepository:
    @staticmethod
    def get_all(offset: int = 0, limit: int = 100) -> List[Asset]:
        return Asset.query.offset(offset).limit(limit).all()

    @staticmethod
    def get_by_id(asset_id: int) -> Optional[Asset]:
        return Asset.query.get(asset_id)

    @staticmethod
    def get_by_ticker(ticker: str) -> Optional[Asset]:
        return Asset.query.filter_by(ticker=ticker).first()

    @staticmethod
    def create(data: dict) -> Asset:
        asset = Asset(**data)
        db.session.add(asset)
        db.session.commit()
        return asset

    @staticmethod
    def update(asset: Asset, data: dict) -> Asset:
        for key, value in data.items():
            setattr(asset, key, value)
        db.session.commit()
        return asset

    @staticmethod
    def delete(asset: Asset) -> None:
        db.session.delete(asset)
        db.session.commit()
