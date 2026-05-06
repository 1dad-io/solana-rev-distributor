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

## Reward Policies

A validator can create reward policies that define how MEV revenue and block rewards are shared with stakers.

Policy fields:
- `staker_withdrawer_pubkey` — staker withdrawer pubkey for an individual policy; `null` for a default policy
- `is_default` — whether the policy is the validator fallback policy for unmatched stakers
- `mev_bps_back` — MEV share returned to the staker in basis points
- `block_rewards_bps_back` — block rewards share returned to the staker in basis points
- `valid_from_epoch` — optional lower bound epoch; `null` means no lower limit
- `valid_to_epoch` — optional upper bound epoch; `null` means no upper limit
- `is_active` — whether the policy can be used in reward calculation

The API does not allow creating or updating a policy into a full duplicate of another policy of the same validator. In that case the API returns `409 Conflict`.

## Reward Calculation Policy Selection

When rewards are calculated for a validator and epoch, policy selection is deterministic:

1. Only policies with `is_active = true` are considered.
2. The policy must match the reward epoch:
   - if `valid_from_epoch` is set, the reward epoch must be greater than or equal to it
   - if `valid_to_epoch` is set, the reward epoch must be less than or equal to it
3. An individual policy for the staker takes priority over a default policy.
4. If multiple matching policies of the same class exist, the most recently updated policy is selected.
5. If `updated_at` is equal, the policy with the greater `id` is selected.

If no matching policy exists for a stake account, reward calculation still creates a reward row, but with:

- `policy_id_used = null`
- `status = "error_no_policy"`

## Reward Calculation Flow

Typical validator flow:

1. Create validator and staker users
2. Create reward policies
3. Import validator stake snapshot for an epoch
4. Import epoch reward context
5. Calculate rewards for the epoch

Typical staker flow:

1. Authenticate as a staker
2. Read calculated rewards for the selected epoch
3. Read aggregated reward statistics

## Notes

- All reward values are stored in lamports.
- Public Solana RPC endpoints are used by default for development and demonstration.
- Production deployments should use private or dedicated RPC providers configured outside the repository.
- The testnet Jito endpoint is configured cluster-wise in `.env.testnet`.
- Swagger UI is the main interface for demonstration.
