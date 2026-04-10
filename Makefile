.PHONY: init init-db seed-db import-csv reset-db run serve test clean setup docs

VENV?=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

init:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt

init-db:
	$(PYTHON) -c "from app import create_app; from app.utils.db_init import init_db; app=create_app(); init_db(app)"

seed-db:
	$(PYTHON) -c "from app import create_app; from app.utils.db_init import seed_db; app=create_app(); seed_db(app)"

import-csv:
	@if [ -z "$(CSV)" ]; then \
		echo "Usage: make import-csv CSV=/path/to/assets.csv [UPDATE=1]"; exit 1; \
	fi
	$(PYTHON) -m app.utils.import_assets_csv $(CSV) $(if $(UPDATE),--update-existing,)

reset-db:
	$(PYTHON) -c "from app import create_app; from app.utils.db_init import init_db; app=create_app(); init_db(app, reset=True)"

run:
	$(PYTHON) run.py

serve:
	gunicorn -w 4 -b 0.0.0.0:5000 'run:app'

test:
	$(PYTHON) -m pytest

setup:
	@echo "Starting project setup (venv, deps, DB)."
	@$(MAKE) init
	@$(MAKE) init-db
	@if [ "${TEST:-0}" = "1" ]; then \
		echo "TEST=1 detected — running integration tests"; \
		$(MAKE) test; \
	else \
		echo "Skipping integration tests. To run them: TEST=1 make setup"; \
	fi
	@echo "Setup complete. Run 'make run' to start the app."

docs:
	@echo "Starting app and exposing Swagger UI at http://127.0.0.1:5000/apidocs"
	@PORT=5000 $(PYTHON) run.py

clean:
	-rm -rf $(VENV) __pycache__ *.pyc .pytest_cache
