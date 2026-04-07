from datetime import datetime
from app import db


class Asset(db.Model):
    __tablename__ = 'assets'

    id = db.Column(db.Integer, primary_key=True)
    ticker = db.Column(db.String(32), unique=True, nullable=False)
    name = db.Column(db.String(256), nullable=True)
    exchange = db.Column(db.String(64), nullable=True)
    currency = db.Column(db.String(8), nullable=True)
    sector = db.Column(db.String(128), nullable=True)
    price = db.Column(db.Float, nullable=True)
    market_cap = db.Column(db.Float, nullable=True)
    last_price_update = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ticker': self.ticker,
            'name': self.name,
            'exchange': self.exchange,
            'currency': self.currency,
            'sector': self.sector,
            'price': self.price,
            'market_cap': self.market_cap,
            'last_price_update': self.last_price_update.isoformat() if self.last_price_update else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
