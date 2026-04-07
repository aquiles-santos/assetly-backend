import os
from app import create_app


CONFIG = os.environ.get('APP_CONFIG', 'app.config.config.Config')


app = create_app(CONFIG)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=app.config.get('DEBUG', False))
