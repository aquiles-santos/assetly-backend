import os
from typing import Optional
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()
ma = Marshmallow()


def create_app(config_object: Optional[str] = None):
    app = Flask(__name__)

    # load configuration from parameter or environment
    if config_object:
        app.config.from_object(config_object)
    else:
        conf = os.environ.get('APP_CONFIG', 'app.config.config.Config')
        app.config.from_object(conf)

    # init extensions
    db.init_app(app)
    ma.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # register blueprints and error handlers
    with app.app_context():
        from app.routes import register_routes

        register_routes(app)

        @app.errorhandler(HTTPException)
        def handle_http_exception(e):
            response = e.get_response()
            # replace body with JSON
            response.data = jsonify({'error': e.description}).data
            response.content_type = 'application/json'
            return response, e.code

        @app.errorhandler(Exception)
        def handle_unexpected_error(e):
            app.logger.exception(e)
            return jsonify({'error': 'internal_server_error'}), 500

    return app
