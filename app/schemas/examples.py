DEMO_VALIDATOR_IDENTITY = "Va1idator11111111111111111111111111111111111"
DEMO_VOTE_ACCOUNT = "VoteAcc111111111111111111111111111111111111"
DEMO_STAKER_WITHDRAWER = "Staker1111111111111111111111111111111111111"
DEMO_STAKE_ACCOUNT = "StakeAcc11111111111111111111111111111111111"

DEMO_USERNAME_VALIDATOR = "demo_validator"
DEMO_USERNAME_STAKER = "demo_staker"

DEMO_ALIAS_VALIDATOR = "Demo Validator"
DEMO_ALIAS_STAKER = "Demo Staker"

DEMO_EPOCH = 0

DEMO_PASSWORD = "secret123"

DEMO_MEV_BPS_BACK = 10000
DEMO_BLOCK_REWARDS_BPS_BACK = 5000

DEMO_BLOCK_REWARDS_LAMPORTS = 1000000000
DEMO_MEV_REVENUE_LAMPORTS = 500000000
DEMO_UPTIME_BPS = 10000

SIGNUP_REQUEST_EXAMPLES = {
    "validator": {
        "summary": "Validator signup",
        "value": {
            "username": DEMO_USERNAME_VALIDATOR,
            "password": DEMO_PASSWORD,
            "role": "validator",
            "alias": DEMO_ALIAS_VALIDATOR,
            "validator_identity_pubkey": DEMO_VALIDATOR_IDENTITY,
            "vote_account_pubkey": DEMO_VOTE_ACCOUNT,
            "staker_withdrawer_pubkey": None,
            "is_active": True,
        },
    },
    "staker": {
        "summary": "Staker signup",
        "value": {
            "username": DEMO_USERNAME_STAKER,
            "password": DEMO_PASSWORD,
            "role": "staker",
            "alias": DEMO_ALIAS_STAKER,
            "validator_identity_pubkey": None,
            "vote_account_pubkey": None,
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_active": True,
        },
    },
}

POLICY_REQUEST_EXAMPLES = {
    "default_policy": {
        "summary": "Default policy without epoch limits",
        "value": {
            "staker_withdrawer_pubkey": None,
            "is_default": True,
            "mev_bps_back": DEMO_MEV_BPS_BACK,
            "block_rewards_bps_back": DEMO_BLOCK_REWARDS_BPS_BACK,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
    },
    "individual_policy": {
        "summary": "Individual staker policy without epoch limits",
        "value": {
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_default": False,
            "mev_bps_back": DEMO_MEV_BPS_BACK,
            "block_rewards_bps_back": DEMO_BLOCK_REWARDS_BPS_BACK,
            "valid_from_epoch": None,
            "valid_to_epoch": None,
            "is_active": True,
        },
    },
    "epoch_limited_policy": {
        "summary": "Individual staker policy limited to one epoch",
        "value": {
            "staker_withdrawer_pubkey": DEMO_STAKER_WITHDRAWER,
            "is_default": False,
            "mev_bps_back": DEMO_MEV_BPS_BACK,
            "block_rewards_bps_back": DEMO_BLOCK_REWARDS_BPS_BACK,
            "valid_from_epoch": DEMO_EPOCH,
            "valid_to_epoch": DEMO_EPOCH,
            "is_active": True,
        },
    },
}
