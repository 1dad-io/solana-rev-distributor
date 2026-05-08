from datetime import datetime, timezone

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


def policy_matches_epoch(policy: RewardPolicy, epoch: int) -> bool:
    if policy.valid_from_epoch is not None and epoch < policy.valid_from_epoch:
        return False
    if policy.valid_to_epoch is not None and epoch > policy.valid_to_epoch:
        return False
    return True


def sort_policies_by_recency(policies: list[RewardPolicy]) -> list[RewardPolicy]:
    return sorted(
        policies,
        key=lambda policy: (
            policy.updated_at or datetime.min.replace(tzinfo=timezone.utc),
            policy.id,
        ),
        reverse=True,
    )


def get_matching_active_policies(
    policies: list[RewardPolicy],
    *,
    epoch: int,
) -> list[RewardPolicy]:
    return [
        policy
        for policy in policies
        if policy.is_active and policy_matches_epoch(policy, epoch)
    ]


def get_matching_individual_policies(
    policies: list[RewardPolicy],
    *,
    withdrawer_authority: str | None,
) -> list[RewardPolicy]:
    return [
        policy
        for policy in policies
        if not policy.is_default
        and policy.staker_withdrawer_pubkey == withdrawer_authority
    ]


def get_matching_default_policies(
    policies: list[RewardPolicy],
) -> list[RewardPolicy]:
    return [policy for policy in policies if policy.is_default]


def select_policy_for_staker(
    policies: list[RewardPolicy],
    *,
    withdrawer_authority: str | None,
    epoch: int,
) -> RewardPolicy | None:
    matching_policies = get_matching_active_policies(
        policies,
        epoch=epoch,
    )

    individual_policies = get_matching_individual_policies(
        matching_policies,
        withdrawer_authority=withdrawer_authority,
    )
    if individual_policies:
        return sort_policies_by_recency(individual_policies)[0]

    default_policies = get_matching_default_policies(matching_policies)
    if default_policies:
        return sort_policies_by_recency(default_policies)[0]

    return None
