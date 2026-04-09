from datetime import datetime
from typing import Optional, List
from app import db
from app.models.asset import Asset


class AssetRepository:
    @staticmethod
    def get_all(offset: int = 0, limit: int = 100) -> List[Asset]:
        return Asset.query.offset(offset).limit(limit).all()

    @staticmethod
    def get_filtered(
        symbol: str = None,
        name: str = None,
        asset_type: str = None,
        sector: str = None,
        offset: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_dir: str = 'asc',
    ) -> List[Asset]:
        q = Asset.query

        if symbol:
            q = q.filter(Asset.symbol == symbol)
        if name:
            q = q.filter(Asset.name.ilike(f"%{name}%"))
        if asset_type:
            q = q.filter(Asset.asset_type == asset_type)
        if sector:
            q = q.filter(Asset.sector.ilike(f"%{sector}%"))

        cols = {
            'name': Asset.name,
            'symbol': Asset.symbol,
            'current_price': Asset.current_price,
            'updated_at': Asset.updated_at,
        }

        col = cols.get(order_by)
        if col is not None:
            if (order_dir or '').lower() == 'desc':
                q = q.order_by(col.desc())
            else:
                q = q.order_by(col.asc())

        return q.offset(offset).limit(limit).all()

    @staticmethod
    def get_filtered_with_count(
        symbol: str = None,
        name: str = None,
        asset_type: str = None,
        sector: str = None,
        offset: int = 0,
        limit: int = 100,
        order_by: str = None,
        order_dir: str = 'asc',
    ) -> tuple:
        q = Asset.query

        if symbol:
            q = q.filter(Asset.symbol == symbol)
        if name:
            q = q.filter(Asset.name.ilike(f"%{name}%"))
        if asset_type:
            q = q.filter(Asset.asset_type == asset_type)
        if sector:
            q = q.filter(Asset.sector.ilike(f"%{sector}%"))

        cols = {
            'name': Asset.name,
            'symbol': Asset.symbol,
            'current_price': Asset.current_price,
            'updated_at': Asset.updated_at,
        }

        col = cols.get(order_by)
        if col is not None:
            if (order_dir or '').lower() == 'desc':
                q = q.order_by(col.desc())
            else:
                q = q.order_by(col.asc())

        total = q.count()
        items = q.offset(offset).limit(limit).all()
        return items, total

    @staticmethod
    def get_recent_snapshots(asset_id: int, limit: int = 10):
        from app.models.market_snapshot import MarketSnapshot

        return (
            MarketSnapshot.query.filter_by(asset_id=asset_id)
            .order_by(MarketSnapshot.captured_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_last_sync_log(asset_id: int):
        from app.models.sync_log import SyncLog

        return (
            SyncLog.query.filter_by(asset_id=asset_id)
            .order_by(SyncLog.synced_at.desc())
            .first()
        )

    @staticmethod
    def get_by_id(asset_id: int) -> Optional[Asset]:
        return db.session.get(Asset, asset_id)

    @staticmethod
    def get_by_ticker(ticker: str) -> Optional[Asset]:
        return Asset.query.filter_by(ticker=ticker).first()

    @staticmethod
    def get_by_symbol(symbol: str) -> Optional[Asset]:
        return Asset.query.filter_by(symbol=symbol).first()

    @staticmethod
    def get_or_create_sync_source(name: str, base_url: str):
        from app.models.external_api_source import ExternalAPISource

        source = ExternalAPISource.query.filter_by(base_url=base_url).first()
        if source:
            if source.name != name:
                source.name = name
                db.session.commit()
            return source

        source = ExternalAPISource(name=name, base_url=base_url, is_active=True)
        db.session.add(source)
        db.session.commit()
        return source

    @staticmethod
    def create_sync_log(
        asset_id: int,
        source_id: int,
        status: str,
        synced_at: datetime,
        message: str = None,
        requested_url: str = None,
        response_time_ms: int = None,
    ):
        from app.models.external_api_source import ExternalAPISource
        from app.models.sync_log import SyncLog

        sync_log = SyncLog(
            asset_id=asset_id,
            source_id=source_id,
            status=status,
            message=message,
            requested_url=requested_url,
            response_time_ms=response_time_ms,
            synced_at=synced_at,
        )
        db.session.add(sync_log)

        source = db.session.get(ExternalAPISource, source_id)
        if source:
            source.last_sync_at = synced_at

        db.session.commit()
        return sync_log

    @staticmethod
    def create_market_snapshot(
        asset_id: int,
        price: float,
        captured_at: datetime,
        open_price: float = None,
        close_price: float = None,
        high_price: float = None,
        low_price: float = None,
        volume: int = None,
    ):
        from app.models.market_snapshot import MarketSnapshot

        snapshot = MarketSnapshot.query.filter_by(
            asset_id=asset_id,
            captured_at=captured_at,
        ).first()

        if snapshot is None:
            snapshot = MarketSnapshot(
                asset_id=asset_id,
                price=price,
                open_price=open_price,
                close_price=close_price,
                high_price=high_price,
                low_price=low_price,
                volume=volume,
                captured_at=captured_at,
            )
            db.session.add(snapshot)
        else:
            snapshot.price = price
            snapshot.open_price = open_price
            snapshot.close_price = close_price
            snapshot.high_price = high_price
            snapshot.low_price = low_price
            snapshot.volume = volume

        db.session.commit()
        return snapshot

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
        # Prevent deleting an asset while there are pending external syncs
        from app.models.sync_log import SyncLog

        pending_count = SyncLog.query.filter_by(asset_id=asset.id, status='pending').count()
        if pending_count:
            # Caller should handle this condition and return a proper error
            raise RuntimeError('pending_syncs')

        try:
            db.session.delete(asset)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
