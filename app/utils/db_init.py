from app import db
from app.models.asset import Asset


def init_db(app):
    with app.app_context():
        db.create_all()

        # optional sample data
        if not Asset.query.first():
            sample = Asset(ticker='AAPL', name='Apple Inc.', exchange='NASDAQ', currency='USD', price=150.0)
            db.session.add(sample)
            db.session.commit()
