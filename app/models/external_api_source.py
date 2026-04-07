from datetime import datetime
from app import db


class ExternalAPISource(db.Model):
    __tablename__ = 'external_api_sources'
    __table_args__ = (
        db.Index('idx_external_api_sources_name', 'name'),
        db.UniqueConstraint('base_url', name='uq_external_api_sources_base_url'),
    )

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    base_url = db.Column(db.String(1024), nullable=False)
    asset_symbol_pattern = db.Column(db.String(256), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    rate_limit_notes = db.Column(db.Text, nullable=True)
    last_sync_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # relationship to sync logs
    sync_logs = db.relationship('SyncLog', backref='source', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'base_url': self.base_url,
            'asset_symbol_pattern': self.asset_symbol_pattern,
            'is_active': bool(self.is_active),
            'rate_limit_notes': self.rate_limit_notes,
            'last_sync_at': self.last_sync_at.isoformat() if self.last_sync_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
