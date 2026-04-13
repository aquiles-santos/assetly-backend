from datetime import datetime
from app import db


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=False)
    asset_type = db.Column(db.String(64), nullable=False)
    sector = db.Column(db.String(128), nullable=True)
    exchange = db.Column(db.String(64), nullable=True)
    currency = db.Column(db.String(3), nullable=False)
    current_price = db.Column(db.Float, nullable=True)
    open_price = db.Column(db.Float, nullable=True)
    close_price = db.Column(db.Float, nullable=True)
    day_high = db.Column(db.Float, nullable=True)
    day_low = db.Column(db.Float, nullable=True)
    volume = db.Column(db.BigInteger, nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    pe_ratio = db.Column(db.Float, nullable=True)
    dividend_yield = db.Column(db.Float, nullable=True)
    external_api_url = db.Column(db.String(1024), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    market_snapshots = db.relationship(
        'MarketSnapshot', backref='asset', cascade='all, delete-orphan', lazy='dynamic'
    )
    sync_logs = db.relationship(
        'SyncLog', backref='asset', cascade='all, delete-orphan', lazy='dynamic'
    )

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'asset_type': self.asset_type,
            'currency': self.currency,
            'exchange': self.exchange,
            'sector': self.sector,
            'current_price': self.current_price,
            'open_price': self.open_price,
            'close_price': self.close_price,
            'day_high': self.day_high,
            'day_low': self.day_low,
            'volume': self.volume,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'dividend_yield': self.dividend_yield,
            'external_api_url': self.external_api_url,
            'notes': self.notes,
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
