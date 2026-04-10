# Assetly Backend

Flask backend for asset management with SQLite. Use `APP_CONFIG` to switch configuration.

## Run locally

```bash
python run.py
```

Swagger UI is available at `http://127.0.0.1:5000/apidocs` when the app is running.

## CORS for the frontend

By default, the API accepts these origins:

- `null` for opening the frontend directly via `file://.../index.html`
- `http://localhost:5500`
- `http://127.0.0.1:5500`

This keeps both frontend flows available: opening the file directly or serving it with `python3 -m http.server 5500`.

To override the default list, set `CORS_ALLOWED_ORIGINS` as a comma-separated env var:

```bash
export CORS_ALLOWED_ORIGINS="null,http://localhost:5500,http://127.0.0.1:5500,http://localhost:3000"
```

## Main flow

- Python 3.8+ installed

Quickstart:

```bash
make init
make init-db
make seed-db
make import-csv CSV=./assets.csv
make run
make test
```

`make init-db` creates the schema only.
`make seed-db` imports the default CSV seed through Yahoo Finance and creates an initial market snapshot for each imported asset when the database is empty.
`make import-csv CSV=./assets.csv` imports assets from Yahoo Finance using a CSV file.
`make reset-db` drops the current SQLite schema and recreates it without loading seed data.

## Import assets from CSV

The importer reads a CSV file with one symbol per line or a header column named `symbol`, `ticker`, `code`, or `asset`.

Optional columns can override the values returned by Yahoo Finance for the same asset:

- `name`
- `asset_type`
- `sector`
- `exchange`
- `currency`
- `notes`

Example:

```csv
symbol,asset_type,notes
AAPL,equity,Imported from NASDAQ watchlist
MSFT,equity,Imported from NASDAQ watchlist
PETR4.SA,equity,Imported from B3 watchlist
VALE3.SA,equity,Imported from B3 watchlist
```

Run the import with:

```bash
make import-csv CSV=./assets.csv
```

To update assets that already exist in the database:

```bash
make import-csv CSV=./assets.csv UPDATE=1
```

The importer fetches metadata from Yahoo Finance and stores the asset if the symbol returns enough data to satisfy the model, especially `currency`. It also creates an initial `market_snapshot` using the quote returned during import.

The default seed used by `make seed-db` is versioned in `data/seed_assets.csv`.

## Useful commands

- `make reset-db`: recreate the SQLite schema from scratch.
- `make test`: run the automated test suite.
- `make setup`: create the virtualenv, install dependencies, and initialize the database.
- `make docs`: start the API and open Swagger at `/apidocs`.
