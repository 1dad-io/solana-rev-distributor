# solana-rev-distributor

A FastAPI-based MVP service for Solana validator REV distribution workflows.

## Current phase

This repository currently contains the initial application skeleton:
- FastAPI app bootstrap
- environment-based configuration
- SQLite initialization
- automatic data directory creation
- health endpoints
- basic tests

## Runtime model

One running application instance works with a single cluster at a time.
Select the runtime cluster by linking one of the provided environment files to `.env`.

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ln -sf .env.testnet .env
uvicorn app.main:app --reload
```

Open Swagger at:

```text
http://127.0.0.1:8000/docs
```

## Health checks

- `GET /`
- `GET /health`
