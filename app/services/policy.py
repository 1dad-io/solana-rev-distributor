from sqlalchemy.orm import Session

from app.models.reward_policy import RewardPolicy


def find_duplicate_policy(
    db: Session,
    *,
    validator_identity_pubkey: str,
    cluster: str,
    staker_withdrawer_pubkey: str | None,
    is_default: bool,
    mev_bps_back: int,
    block_rewards_bps_back: int,
    valid_from_epoch: int | None,
    valid_to_epoch: int | None,
    is_active: bool,
    exclude_policy_id: int | None = None,
) -> RewardPolicy | None:
    query = db.query(RewardPolicy).filter(
        RewardPolicy.validator_identity_pubkey == validator_identity_pubkey,
        RewardPolicy.cluster == cluster,
        RewardPolicy.staker_withdrawer_pubkey == staker_withdrawer_pubkey,
        RewardPolicy.is_default == is_default,
        RewardPolicy.mev_bps_back == mev_bps_back,
        RewardPolicy.block_rewards_bps_back == block_rewards_bps_back,
        RewardPolicy.valid_from_epoch == valid_from_epoch,
        RewardPolicy.valid_to_epoch == valid_to_epoch,
        RewardPolicy.is_active == is_active,
    )

    if exclude_policy_id is not None:
        query = query.filter(RewardPolicy.id != exclude_policy_id)

    return query.first()
