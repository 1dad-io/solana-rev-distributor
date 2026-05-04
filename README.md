# solana-rev-distributor

A FastAPI-based service for calculating REV kickback rewards for Solana stakers.

## Current MVP scope

The project provides:

- username/password authentication
- Bearer token authorization
- validator self endpoints
- staker self endpoints
- reward policy management
- stake snapshot import from local JSON files
- epoch reward context import from local JSON files
- reward calculation in lamports
- validator reward views
- staker reward views and basic stats
- Swagger UI for demonstration

## Stack

- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT auth
- Pytest

## Environment setup

Create or activate a virtual environment, then install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
```

Select the target environment:

```bash
ln -sf .env.testnet .env
```

## Running tests

```bash
pytest
```

Tests use an isolated SQLite database and do not modify the runtime application database.

## Preparing demo data

To prepare a clean demo runtime database with preloaded users, policies, stake snapshot, epoch reward context, and calculated rewards, run:

```bash
python3 -m scripts.seed_demo
```

This command recreates the runtime SQLite database configured in `.env` and writes demo JSON files for the demo epoch.

## Running the application

Start the API server:

```bash
uvicorn app.main:app --reload
```

Open Swagger UI in the browser:

```text
http://127.0.0.1:8000/docs
```

## Demo users

After running the demo seed script, the application contains these users:

### Validator
- username: `demo_validator`
- password: `secret123`

### Staker
- username: `demo_staker`
- password: `secret123`

## Demo dataset

The demo seed prepares:

- epoch: `0`
- runtime database:
  - `data/testnet/app.db`
- stake snapshot file:
  - `data/testnet/stakes/0.json`
- validator rewards file:
  - `data/testnet/validator_rewards/0.json`

## Demo API flow

### Validator flow
- log in
- open `/validators/me`
- view policies
- view imported stake snapshots
- view imported epoch reward context
- calculate rewards
- view validator rewards

### Staker flow
- log in
- open `/stakers/me`
- view rewards
- view stats

## Notes

- All reward values are stored in lamports.
- The current MVP imports stake and validator reward source data from local JSON files.
- The project is designed so external data fetching can be added later without breaking the API structure.
- Swagger UI is the main interface for demonstration.
