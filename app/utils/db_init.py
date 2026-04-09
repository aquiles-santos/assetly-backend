from pathlib import Path

from app import db
from app.models import Asset
from app.utils.import_assets_csv import import_assets


DEFAULT_SEED_CSV_PATH = Path(__file__).resolve().parents[2] / 'data' / 'seed_assets.csv'


def seed_assets(app):
    if not DEFAULT_SEED_CSV_PATH.exists():
        raise FileNotFoundError(f'Seed CSV not found: {DEFAULT_SEED_CSV_PATH}')

    return import_assets(DEFAULT_SEED_CSV_PATH, app=app)


def init_db(app, reset: bool = False):
    with app.app_context():
        import app.models  # noqa: F401

        if reset:
            db.drop_all()

        db.create_all()


def seed_db(app):
    with app.app_context():
        if not Asset.query.first():
            seed_assets(app)
