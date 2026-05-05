# solana-rev-distributor

A FastAPI-based service for calculating REV kickback rewards for Solana validator stakers.

## Current MVP scope

The project provides:

- username/password authentication
- Bearer token authorization
- validator self endpoints
- staker self endpoints
- reward policy management
- stake snapshot import from local JSON files or Solana CLI
- epoch reward context import from local JSON files or Jito endpoint
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

Important: stop the API server before running the demo seed script.  
The script recreates the runtime SQLite database file.

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

## Real data import

### Stakes
The application imports stake snapshots in this order:

1. from a local JSON file in `data/<cluster>/stakes/<epoch>.json`
2. if the file is missing, via `solana` CLI using the configured public Solana RPC

### Validator rewards
The application imports validator reward context in this order:

1. from a local JSON file in `data/<cluster>/validator_rewards/<epoch>.json`
2. if the file is missing, from the configured Jito endpoint

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
- Public Solana RPC endpoints are used by default for development and demonstration.
- Production deployments should use private or dedicated RPC providers configured outside the repository.
- The testnet Jito endpoint is configured cluster-wise in `.env.testnet`.
- Swagger UI is the main interface for demonstration.
