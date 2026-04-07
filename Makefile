.PHONY: init init-db run serve test clean

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
	$(PIP) install -r requirements.txt
	$(PYTHON) -m pytest -q

clean:
	-rm -rf $(VENV) __pycache__ *.pyc .pytest_cache
