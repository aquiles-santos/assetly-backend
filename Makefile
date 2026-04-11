.PHONY: init init-db seed-db import-csv reset-db run serve test clean setup docs

VENV?=.venv
BOOTSTRAP_PYTHON?=$(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)
AUTO_INSTALL_SYSTEM_DEPS?=0
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

init:
	@if [ -z "$(BOOTSTRAP_PYTHON)" ]; then \
		echo "Python 3 not found. Install python3 or run 'make init BOOTSTRAP_PYTHON=/path/to/python3'."; exit 127; \
	fi
	@if ! $(BOOTSTRAP_PYTHON) -c "import ensurepip" >/dev/null 2>&1; then \
		echo "Python venv support is missing for $(BOOTSTRAP_PYTHON)."; \
		if command -v apt-get >/dev/null 2>&1; then \
			if [ "$(AUTO_INSTALL_SYSTEM_DEPS)" = "1" ]; then \
				echo "Attempting to install python3-venv via apt-get..."; \
				sudo apt-get update && sudo apt-get install -y python3-venv; \
			elif [ -t 0 ]; then \
				printf "Install python3-venv now with sudo apt-get install -y python3-venv? [y/N] "; \
				read answer; \
				case "$$answer" in \
					y|Y|yes|YES) sudo apt-get update && sudo apt-get install -y python3-venv ;; \
					*) echo "Skipped system dependency installation."; exit 1 ;; \
				esac; \
			else \
				echo "On Debian/Ubuntu, install it with: sudo apt install python3-venv"; \
				echo "Or retry with automatic installation: make init AUTO_INSTALL_SYSTEM_DEPS=1"; \
				echo "If you want the simplest cross-platform setup, use Docker: docker compose up --build"; \
				exit 1; \
			fi; \
			if ! $(BOOTSTRAP_PYTHON) -c "import ensurepip" >/dev/null 2>&1; then \
				echo "python3-venv was not installed successfully or ensurepip is still unavailable."; \
				exit 1; \
			fi; \
		else \
			echo "Install the system package that provides python3 venv support for your OS."; \
			echo "If you want the simplest cross-platform setup, use Docker: docker compose up --build"; \
			exit 1; \
		fi; \
	fi
	$(BOOTSTRAP_PYTHON) -m venv $(VENV)
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
	-rm -rf $(VENV) .pytest_cache
	-find . -type d -name '__pycache__' -exec rm -rf {} +
	-find . -name '*.pyc' -delete
