# Assetly Backend (MVP)

Flask backend for asset management (SQLite). Use `APP_CONFIG` env var to change config.

Run locally:

```bash
python run.py
```

## Development & testing

Prerequisites

- Python 3.8+ installed
- Node/npm (optional, for OpenAPI linting with Spectral)

Quickstart (virtualenv)

```bash
# create virtualenv and install dependencies
make init

# initialize database schema
make init-db

# optionally populate static development data
make seed-db

# reset database schema
make reset-db

# run the app
make run
```

`make init-db` creates the schema only.
`make seed-db` populates the database with 6 static assets only when it is empty.
`make reset-db` drops the current SQLite schema and recreates it without loading seed data.

## Integration tests (end-to-end)

There is an integration script that starts the app, runs endpoint checks (list → create → get → update → sync → delete), removes compiled Python files, and stops the app.

Run it via Make:

```bash
make test
```

This target executes `scripts/test_and_cleanup.sh` and will print HTTP status codes for each step. A temporary log is kept under `/tmp/assetly_test.*.log` for inspection.

## Open the interactive API docs (Swagger UI)

To start the app and open the browser pointing to the Swagger UI:

```bash
make docs
```

Notes:

- `make docs` starts the app on port 5000 and opens `http://127.0.0.1:5000/apidocs` in your default browser. Logs are in `/tmp/assetly_docs.log`.
- If you don't have a GUI (headless server), the server will run and you can open the URL from another machine.

## OpenAPI validation (CI)

We provide a `ci-validate` Make target that lints `docs/openapi.yaml` with Spectral. Install Spectral globally:

```bash
npm install -g @stoplight/spectral-cli
```

Then run:

```bash
make ci-validate
```

## Repository housekeeping

- Compiled files (`*.pyc` and `__pycache__`) are ignored by `.gitignore`. If you need to remove them locally, the test script already deletes them; otherwise:

```bash
find . -name '*.pyc' -delete
find . -type d -name '__pycache__' -exec rm -rf {} +
```

If you want, I can add a `Makefile` target to automatically install Spectral locally (npm devDependency) and a GitHub Actions workflow that runs `make ci-validate` on PRs.

## One-shot setup

To prepare the project in one command (create virtualenv, install deps, initialize DB), run:

```bash
make setup
```

If you want the setup to also run the integration checks (the same as `make test`), run:

```bash
TEST=1 make setup
```

This is intended to be run once on a developer machine to get the project ready to run.
