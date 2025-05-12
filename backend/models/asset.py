from .base import db, Base
from datetime import datetime

class Asset(Base):
    symbol = db.Column(db.String(20), nullable=False)
    asset_type = db.Column(db.String(20), nullable=False)  # 'indian_stock', 'us_stock', 'crypto'
    quantity = db.Column(db.Float, nullable=False)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)
    last_price = db.Column(db.Float)
    last_price_updated = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'asset_type': self.asset_type,
            'quantity': self.quantity,
            'purchase_price': self.purchase_price,
            'purchase_date': self.purchase_date.isoformat(),
            'last_price': self.last_price,
            'last_price_updated': self.last_price_updated.isoformat() if self.last_price_updated else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            symbol=data['symbol'],
            asset_type=data['asset_type'],
            quantity=float(data['quantity']),
            purchase_price=float(data['purchase_price']),
            purchase_date=datetime.fromisoformat(data['purchase_date'])
        )
