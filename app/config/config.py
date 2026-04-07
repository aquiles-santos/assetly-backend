import os


class Config:
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///assets.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SWAGGER = {
        'title': 'Assetly API',
        'uiversion': 3,
    }


class ProductionConfig(Config):
    DEBUG = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
