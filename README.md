# solana-rev-distributor

A FastAPI-based service for calculating REV kickback rewards for Solana validator stakers.

## Phase 3 status

This repository currently includes:

- FastAPI application bootstrap
- SQLite auto-initialization
- `User` and `Validator` SQLAlchemy models
- Isolated SQLite test database setup
- Authentication endpoints
- Basic validator bootstrap endpoints
- Healthcheck and auth tests

## Run locally

```bash
ln -sf .env.testnet .env
python3 -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open Swagger UI at:

```text
http://127.0.0.1:8000/docs
```
