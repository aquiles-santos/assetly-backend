import os
from typing import Optional
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

db = SQLAlchemy()


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
    # Allow the frontend to run either from file:// (Origin: null) or from a
    # local static server such as python3 -m http.server 5500.
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

    # Serve the OpenAPI spec and a Swagger UI page (using CDN) so docs are browser-accessible
    from flask import render_template_string, send_from_directory
    import pathlib

    @app.route('/apidocs')
    def apidocs():
        html = """
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Assetly API Docs</title>
            <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@4/swagger-ui.css" />
          </head>
          <body>
            <div id="swagger-ui"></div>
            <script src="https://unpkg.com/swagger-ui-dist@4/swagger-ui-bundle.js"></script>
            <script>
              window.onload = function() {
                                SwaggerUIBundle({
                                    url: window.location.origin + '/openapi.yaml',
                                    dom_id: '#swagger-ui',
                                    presets: [
                                        SwaggerUIBundle.presets.apis
                                    ],
                                });
              };
            </script>
          </body>
        </html>
        """
        return render_template_string(html)

    @app.route('/openapi.yaml')
    def openapi_yaml():
        project_root = pathlib.Path.cwd()
        docs_dir = project_root / 'docs'
        return send_from_directory(str(docs_dir), 'openapi.yaml')

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
