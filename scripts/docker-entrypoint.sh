#!/bin/sh
set -e

python -c "from app import create_app; from app.utils.db_init import init_db; app=create_app(); init_db(app)"

if [ "${AUTO_SEED_DB:-1}" = "1" ]; then
	python -c "from app import create_app; from app.utils.db_init import seed_db; app=create_app(); seed_db(app)"
fi

exec "$@"