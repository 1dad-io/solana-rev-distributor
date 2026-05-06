from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.epoch_reward_context import EpochRewardContext
from app.models.reward import Reward
from app.models.reward_policy import RewardPolicy
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot


def _policy_matches_epoch(policy: RewardPolicy, epoch: int) -> bool:
    if policy.valid_from_epoch is not None and epoch < policy.valid_from_epoch:
        return False
    if policy.valid_to_epoch is not None and epoch > policy.valid_to_epoch:
        return False
    return True


def _sort_policies_by_recency(policies: list[RewardPolicy]) -> list[RewardPolicy]:
    return sorted(
        policies,
        key=lambda policy: (
            policy.updated_at or datetime.min.replace(tzinfo=timezone.utc),
            policy.id,
        ),
        reverse=True,
    )


def _select_policy_for_staker(
    policies: list[RewardPolicy],
    *,
    withdrawer_authority: str | None,
    epoch: int,
) -> RewardPolicy | None:
    matching_policies = [
        policy
        for policy in policies
        if policy.is_active and _policy_matches_epoch(policy, epoch)
    ]

    individual_policies = [
        policy
        for policy in matching_policies
        if not policy.is_default
        and policy.staker_withdrawer_pubkey == withdrawer_authority
    ]
    if individual_policies:
        return _sort_policies_by_recency(individual_policies)[0]

    default_policies = [policy for policy in matching_policies if policy.is_default]
    if default_policies:
        return _sort_policies_by_recency(default_policies)[0]

    return None


def _build_error_reward(
    *,
    validator_identity_pubkey: str,
    epoch: int,
    stake_account: StakeAccount,
    validator_total_active_stake_lamports: int,
) -> Reward:
    return Reward(
        validator_identity_pubkey=validator_identity_pubkey,
        cluster=settings.app_cluster,
        epoch=epoch,
        stake_account_id=stake_account.id,
        policy_id_used=None,
        staker_withdrawer_pubkey=stake_account.withdrawer_authority,
        stake_pubkey=stake_account.stake_pubkey,
        withdrawer_authority=stake_account.withdrawer_authority,
        active_stake_lamports=stake_account.active_stake_lamports or 0,
        validator_total_active_stake_lamports=validator_total_active_stake_lamports,
        mev_bps_back_used=None,
        block_rewards_bps_back_used=None,
        gross_mev_reward_lamports=0,
        gross_block_reward_lamports=0,
        gross_reward_lamports=0,
        payable_reward_lamports=0,
        status="error_no_policy",
        calculated_at=datetime.now(timezone.utc),
    )


def _build_calculated_reward(
    *,
    validator_identity_pubkey: str,
    epoch: int,
    stake_account: StakeAccount,
    validator_total_active_stake_lamports: int,
    epoch_context: EpochRewardContext,
    policy: RewardPolicy,
) -> Reward:
    active_stake_lamports = stake_account.active_stake_lamports or 0

    gross_mev_reward_lamports = (
        epoch_context.mev_revenue_lamports * active_stake_lamports
    ) // validator_total_active_stake_lamports
    gross_block_reward_lamports = (
        epoch_context.block_rewards_lamports * active_stake_lamports
    ) // validator_total_active_stake_lamports

    payable_mev_reward_lamports = (
        gross_mev_reward_lamports * policy.mev_bps_back
    ) // 10000
    payable_block_reward_lamports = (
        gross_block_reward_lamports * policy.block_rewards_bps_back
    ) // 10000

    return Reward(
        validator_identity_pubkey=validator_identity_pubkey,
        cluster=settings.app_cluster,
        epoch=epoch,
        stake_account_id=stake_account.id,
        policy_id_used=policy.id,
        staker_withdrawer_pubkey=stake_account.withdrawer_authority,
        stake_pubkey=stake_account.stake_pubkey,
        withdrawer_authority=stake_account.withdrawer_authority,
        active_stake_lamports=active_stake_lamports,
        validator_total_active_stake_lamports=validator_total_active_stake_lamports,
        mev_bps_back_used=policy.mev_bps_back,
        block_rewards_bps_back_used=policy.block_rewards_bps_back,
        gross_mev_reward_lamports=gross_mev_reward_lamports,
        gross_block_reward_lamports=gross_block_reward_lamports,
        gross_reward_lamports=(
            gross_mev_reward_lamports + gross_block_reward_lamports
        ),
        payable_reward_lamports=(
            payable_mev_reward_lamports + payable_block_reward_lamports
        ),
        status="calculated",
        calculated_at=datetime.now(timezone.utc),
    )


def calculate_rewards_for_epoch(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
    force_recalculate: bool = False,
) -> list[Reward]:
    existing_rewards = (
        db.query(Reward)
        .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .filter(Reward.epoch == epoch)
        .order_by(Reward.id.asc())
        .all()
    )
    if existing_rewards and not force_recalculate:
        return existing_rewards

    if existing_rewards and force_recalculate:
        (
            db.query(Reward)
            .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
            .filter(Reward.cluster == settings.app_cluster)
            .filter(Reward.epoch == epoch)
            .delete()
        )
        db.commit()

    snapshot = (
        db.query(StakeSnapshot)
        .filter(StakeSnapshot.validator_identity_pubkey == validator_identity_pubkey)
        .filter(StakeSnapshot.cluster == settings.app_cluster)
        .filter(StakeSnapshot.epoch == epoch)
        .first()
    )
    if snapshot is None:
        raise ValueError("Stake snapshot not found")

    epoch_context = (
        db.query(EpochRewardContext)
        .filter(EpochRewardContext.validator_identity_pubkey == validator_identity_pubkey)
        .filter(EpochRewardContext.cluster == settings.app_cluster)
        .filter(EpochRewardContext.epoch == epoch)
        .first()
    )
    if epoch_context is None:
        raise ValueError("Epoch reward context not found")

    stake_accounts = (
        db.query(StakeAccount)
        .filter(StakeAccount.snapshot_id == snapshot.id)
        .filter(StakeAccount.active_stake_lamports.is_not(None))
        .filter(StakeAccount.active_stake_lamports > 0)
        .order_by(StakeAccount.id.asc())
        .all()
    )
    if not stake_accounts:
        raise ValueError("No active stake accounts found in snapshot")

    policies = (
        db.query(RewardPolicy)
        .filter(RewardPolicy.validator_identity_pubkey == validator_identity_pubkey)
        .filter(RewardPolicy.cluster == settings.app_cluster)
        .all()
    )

    validator_total_active_stake_lamports = sum(
        stake_account.active_stake_lamports or 0 for stake_account in stake_accounts
    )
    if validator_total_active_stake_lamports <= 0:
        raise ValueError("Validator total active stake must be greater than zero")

    rewards_to_create: list[Reward] = []

    for stake_account in stake_accounts:
        selected_policy = _select_policy_for_staker(
            policies,
            withdrawer_authority=stake_account.withdrawer_authority,
            epoch=epoch,
        )

        if selected_policy is None:
            reward = _build_error_reward(
                validator_identity_pubkey=validator_identity_pubkey,
                epoch=epoch,
                stake_account=stake_account,
                validator_total_active_stake_lamports=validator_total_active_stake_lamports,
            )
        else:
            reward = _build_calculated_reward(
                validator_identity_pubkey=validator_identity_pubkey,
                epoch=epoch,
                stake_account=stake_account,
                validator_total_active_stake_lamports=validator_total_active_stake_lamports,
                epoch_context=epoch_context,
                policy=selected_policy,
            )

        rewards_to_create.append(reward)

    db.add_all(rewards_to_create)
    db.commit()

    for reward in rewards_to_create:
        db.refresh(reward)

    return rewards_to_create
