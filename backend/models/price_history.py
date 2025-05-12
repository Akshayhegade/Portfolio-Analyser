from .base import db, Base

class PriceHistory(Base):
    symbol = db.Column(db.String(20), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    __table_args__ = (
        db.Index('idx_symbol_timestamp', 'symbol', 'timestamp'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'asset_type': self.asset_type,
            'price': self.price,
            'timestamp': self.timestamp.isoformat(),
            'created_at': self.created_at.isoformat()
        }
