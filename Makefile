.PHONY: init init-db run serve test clean ci-validate docs setup

VENV?=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

init:
	python -m venv $(VENV)
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -r requirements.txt

init-db:
	$(PYTHON) -c "from app import create_app; from app.utils.db_init import init_db; app=create_app(); init_db(app)"

run:
	$(PYTHON) run.py

serve:
	gunicorn -w 4 -b 0.0.0.0:5000 'run:app'

test:
	# ensure test dependencies are available
	# prefer running the integration test-and-cleanup script
	chmod +x scripts/test_and_cleanup.sh && PORT=5001 ./scripts/test_and_cleanup.sh

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
	@echo "Setup complete. Run 'make run' to start the app or 'make docs' to open the docs."

ci-validate:
	@# validate `docs/openapi.yaml` with Spectral (lint + rules)
	@if ! command -v spectral >/dev/null; then \
		echo "spectral not found; install with: npm install -g @stoplight/spectral-cli"; exit 1; \
	fi
	spectral lint docs/openapi.yaml

docs:
	@echo "Starting app on port 5001 and opening Swagger UI..."
	@PORT=5001 $(PYTHON) run.py > /tmp/assetly_docs.log 2>&1 & \
	echo $$! > /tmp/assetly_docs.pid; \
	PID=$$(cat /tmp/assetly_docs.pid); \
	# wait for readiness
	for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30; do \
		if curl -sSf http://127.0.0.1:5001/openapi.yaml >/dev/null 2>&1; then break; fi; \
		sleep 1; \
	done; \
	if ! curl -sSf http://127.0.0.1:5001/openapi.yaml >/dev/null 2>&1; then \
		echo "App didn't become ready; see /tmp/assetly_docs.log"; kill $$PID || true; exit 1; \
	fi; \
	python -m webbrowser http://127.0.0.1:5001/apidocs || xdg-open http://127.0.0.1:5001/apidocs || true; \
	echo "Swagger UI opened in browser. Server PID: $$PID (log: /tmp/assetly_docs.log)"; \
	wait $$PID

clean:
	-rm -rf $(VENV) __pycache__ *.pyc .pytest_cache
