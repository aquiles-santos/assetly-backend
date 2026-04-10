import os


def _parse_cors_origins():
    raw_origins = os.environ.get(
        'CORS_ALLOWED_ORIGINS',
        'null,http://localhost:5500,http://127.0.0.1:5500',
    )
    return [origin.strip() for origin in raw_origins.split(',') if origin.strip()]


class Config:
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///assets.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ALLOWED_ORIGINS = _parse_cors_origins()
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization']
    CORS_ALLOW_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
