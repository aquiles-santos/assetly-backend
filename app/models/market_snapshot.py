from datetime import datetime
from app import db


class MarketSnapshot(db.Model):
    __tablename__ = 'market_snapshots'
    __table_args__ = (
        db.Index('idx_market_snapshots_asset_captured_at', 'asset_id', 'captured_at'),
        db.UniqueConstraint('asset_id', 'captured_at', name='uq_market_snapshots_asset_captured_at'),
    )

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    price = db.Column(db.Float, nullable=False)
    open_price = db.Column(db.Float, nullable=True)
    close_price = db.Column(db.Float, nullable=True)
    high_price = db.Column(db.Float, nullable=True)
    low_price = db.Column(db.Float, nullable=True)
    volume = db.Column(db.BigInteger, nullable=True)
    captured_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'price': self.price,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'high_price': self.high_price,
            'low_price': self.low_price,
            'volume': self.volume,
            'captured_at': self.captured_at.isoformat() if self.captured_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
