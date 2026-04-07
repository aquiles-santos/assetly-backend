def register_routes(app):
    from .asset_routes import bp as assets_bp

    app.register_blueprint(assets_bp, url_prefix='/api')
