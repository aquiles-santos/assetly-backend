import os
import pathlib
from typing import Optional
from flask import Flask, jsonify, render_template_string, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()


def create_app(config_object: Optional[str] = None):
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False
    app.json.sort_keys = False
    
    if config_object:
        app.config.from_object(config_object)
    else:
        conf = os.environ.get('APP_CONFIG', 'app.config.config.Config')
        app.config.from_object(conf)

    db.init_app(app)
    CORS(
        app,
        resources={
            r"/*": {
                "origins": app.config['CORS_ALLOWED_ORIGINS'],
                "allow_headers": app.config['CORS_ALLOW_HEADERS'],
                "methods": app.config['CORS_ALLOW_METHODS'],
            }
        },
    )

    @app.route('/apidocs')
    def apidocs():
        return render_template_string(
            """
            <!doctype html>
            <html lang="en">
              <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Assetly API Docs</title>
                <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css" />
                <style>
                  body { margin: 0; background: #f5f5f5; }
                  #swagger-ui { max-width: 1200px; margin: 0 auto; }
                </style>
              </head>
              <body>
                <div id="swagger-ui"></div>
                <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
                <script>
                  window.onload = function () {
                    SwaggerUIBundle({
                      url: window.location.origin + '/openapi.yaml',
                      dom_id: '#swagger-ui'
                    });
                  };
                </script>
              </body>
            </html>
            """
        )

    @app.route('/openapi.yaml')
    def openapi_yaml():
        docs_dir = pathlib.Path(app.root_path).parent / 'docs'
        return send_from_directory(str(docs_dir), 'openapi.yaml')

    with app.app_context():
        from app.routes import register_routes

        register_routes(app)

        @app.errorhandler(HTTPException)
        def handle_http_exception(e):
          response = e.get_response()
          response.data = jsonify({'error': e.description}).data
          response.content_type = 'application/json'
          return response, e.code

        @app.errorhandler(Exception)
        def handle_unexpected_error(e):
            app.logger.exception(e)
            return jsonify({'error': 'internal_server_error'}), 500

    return app
