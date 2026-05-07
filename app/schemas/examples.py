from app.demo import (
    DEMO_ALIAS_STAKER,
    DEMO_ALIAS_VALIDATOR,
    DEMO_BLOCK_REWARDS_BPS_BACK,
    DEMO_EPOCH,
    DEMO_MEV_BPS_BACK,
    DEMO_PASSWORD,
    DEMO_STAKER_WITHDRAWER,
    DEMO_USERNAME_STAKER,
    DEMO_USERNAME_VALIDATOR,
    DEMO_VALIDATOR_IDENTITY,
    DEMO_VOTE_ACCOUNT,
)

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
