from datetime import datetime
from typing import Optional
from app import db
from app.models.asset import Asset


class AssetRepository:
    @staticmethod
    def _build_filtered_query(
        symbol: str = None,
        name: str = None,
        asset_type: str = None,
        sector: str = None,
        order_by: str = None,
        order_dir: str = 'asc',
    ):
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

        return q

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
        q = AssetRepository._build_filtered_query(
            symbol=symbol,
            name=name,
            asset_type=asset_type,
            sector=sector,
            order_by=order_by,
            order_dir=order_dir,
        )

        total = q.count()

        # If limit is None we should return all results (ignore offset)
        if limit is None:
            items = q.all()
        else:
            # Ensure offset is an int (default 0)
            _offset = offset or 0
            items = q.offset(_offset).limit(limit).all()

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
    def get_by_symbol(symbol: str) -> Optional[Asset]:
        return Asset.query.filter_by(symbol=symbol).first()

    @staticmethod
    def create_sync_log(
        asset_id: int,
        provider_name: str,
        status: str,
        synced_at: datetime,
        message: str = None,
        requested_url: str = None,
        response_time_ms: int = None,
    ):
        from app.models.sync_log import SyncLog

        sync_log = SyncLog(
            asset_id=asset_id,
            provider_name=provider_name,
            status=status,
            message=message,
            requested_url=requested_url,
            response_time_ms=response_time_ms,
            synced_at=synced_at,
        )
        db.session.add(sync_log)

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
        try:
            db.session.delete(asset)
            db.session.commit()
        except Exception:
            db.session.rollback()
            raise
