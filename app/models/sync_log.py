from datetime import datetime
from app import db


class SyncLog(db.Model):
    __tablename__ = 'sync_logs'
    __table_args__ = (
        db.Index('idx_sync_logs_asset_source_synced_at', 'asset_id', 'source_id', 'synced_at'),
        db.Index('idx_sync_logs_status', 'status'),
        db.CheckConstraint("status IN ('pending','success','failed')", name='ck_sync_logs_status'),
    )

    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey('external_api_sources.id'), nullable=False)
    status = db.Column(db.String(32), nullable=False)
    message = db.Column(db.Text, nullable=True)
    requested_url = db.Column(db.String(2048), nullable=True)
    response_time_ms = db.Column(db.Integer, nullable=True)
    synced_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'asset_id': self.asset_id,
            'source_id': self.source_id,
            'status': self.status,
            'message': self.message,
            'requested_url': self.requested_url,
            'response_time_ms': self.response_time_ms,
            'synced_at': self.synced_at.isoformat() if self.synced_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
