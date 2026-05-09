from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.config import settings
from app.models.epoch_reward_context import EpochRewardContext
from app.models.reward import Reward
from app.models.reward_policy import RewardPolicy
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot
from app.services.policy import select_policy_for_staker


@dataclass(frozen=True)
class RewardBuildContext:
    validator_identity_pubkey: str
    epoch: int
    validator_total_active_stake_lamports: int
    epoch_context: EpochRewardContext | None = None


@dataclass(frozen=True)
class RewardCalculationInputs:
    stake_accounts: list[StakeAccount]
    policies: list[RewardPolicy]
    calculated_context: RewardBuildContext
    error_context: RewardBuildContext


def _build_error_reward(
    *,
    stake_account: StakeAccount,
    context: RewardBuildContext,
) -> Reward:
    return Reward(
        validator_identity_pubkey=context.validator_identity_pubkey,
        cluster=settings.app_cluster,
        epoch=context.epoch,
        stake_account_id=stake_account.id,
        policy_id_used=None,
        staker_withdrawer_pubkey=stake_account.withdrawer_authority,
        stake_pubkey=stake_account.stake_pubkey,
        withdrawer_authority=stake_account.withdrawer_authority,
        active_stake_lamports=stake_account.active_stake_lamports or 0,
        validator_total_active_stake_lamports=context.validator_total_active_stake_lamports,
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
    stake_account: StakeAccount,
    policy: RewardPolicy,
    context: RewardBuildContext,
) -> Reward:
    if context.epoch_context is None:
        raise ValueError("Epoch reward context is required for calculated rewards")

    active_stake_lamports = stake_account.active_stake_lamports or 0

    gross_mev_reward_lamports = (
        context.epoch_context.mev_revenue_lamports * active_stake_lamports
    ) // context.validator_total_active_stake_lamports
    gross_block_reward_lamports = (
        context.epoch_context.block_rewards_lamports * active_stake_lamports
    ) // context.validator_total_active_stake_lamports

    payable_mev_reward_lamports = (
        gross_mev_reward_lamports * policy.mev_bps_back
    ) // 10000
    payable_block_reward_lamports = (
        gross_block_reward_lamports * policy.block_rewards_bps_back
    ) // 10000

    return Reward(
        validator_identity_pubkey=context.validator_identity_pubkey,
        cluster=settings.app_cluster,
        epoch=context.epoch,
        stake_account_id=stake_account.id,
        policy_id_used=policy.id,
        staker_withdrawer_pubkey=stake_account.withdrawer_authority,
        stake_pubkey=stake_account.stake_pubkey,
        withdrawer_authority=stake_account.withdrawer_authority,
        active_stake_lamports=active_stake_lamports,
        validator_total_active_stake_lamports=context.validator_total_active_stake_lamports,
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


def _get_existing_rewards(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
) -> list[Reward]:
    return (
        db.query(Reward)
        .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .filter(Reward.epoch == epoch)
        .order_by(Reward.id.asc())
        .all()
    )


def _delete_existing_rewards(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
) -> None:
    (
        db.query(Reward)
        .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .filter(Reward.epoch == epoch)
        .delete()
    )
    db.commit()


def _get_stake_snapshot(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
) -> StakeSnapshot:
    snapshot = (
        db.query(StakeSnapshot)
        .filter(StakeSnapshot.validator_identity_pubkey == validator_identity_pubkey)
        .filter(StakeSnapshot.cluster == settings.app_cluster)
        .filter(StakeSnapshot.epoch == epoch)
        .first()
    )
    if snapshot is None:
        raise ValueError("Stake snapshot not found")
    return snapshot


def _get_epoch_reward_context(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
) -> EpochRewardContext:
    epoch_context = (
        db.query(EpochRewardContext)
        .filter(EpochRewardContext.validator_identity_pubkey == validator_identity_pubkey)
        .filter(EpochRewardContext.cluster == settings.app_cluster)
        .filter(EpochRewardContext.epoch == epoch)
        .first()
    )
    if epoch_context is None:
        raise ValueError("Epoch reward context not found")
    return epoch_context


def _get_active_stake_accounts(
    db: Session,
    *,
    snapshot_id: int,
) -> list[StakeAccount]:
    stake_accounts = (
        db.query(StakeAccount)
        .filter(StakeAccount.snapshot_id == snapshot_id)
        .filter(StakeAccount.active_stake_lamports.is_not(None))
        .filter(StakeAccount.active_stake_lamports > 0)
        .order_by(StakeAccount.id.asc())
        .all()
    )
    if not stake_accounts:
        raise ValueError("No active stake accounts found in snapshot")
    return stake_accounts


def _get_reward_policies(
    db: Session,
    *,
    validator_identity_pubkey: str,
) -> list[RewardPolicy]:
    return (
        db.query(RewardPolicy)
        .filter(RewardPolicy.validator_identity_pubkey == validator_identity_pubkey)
        .filter(RewardPolicy.cluster == settings.app_cluster)
        .all()
    )


def _get_validator_total_active_stake_lamports(
    stake_accounts: list[StakeAccount],
) -> int:
    validator_total_active_stake_lamports = sum(
        stake_account.active_stake_lamports or 0 for stake_account in stake_accounts
    )
    if validator_total_active_stake_lamports <= 0:
        raise ValueError("Validator total active stake must be greater than zero")
    return validator_total_active_stake_lamports


def _build_reward_contexts(
    *,
    validator_identity_pubkey: str,
    epoch: int,
    epoch_context: EpochRewardContext,
    stake_accounts: list[StakeAccount],
) -> tuple[RewardBuildContext, RewardBuildContext]:
    validator_total_active_stake_lamports = _get_validator_total_active_stake_lamports(
        stake_accounts
    )

    calculated_context = RewardBuildContext(
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
        validator_total_active_stake_lamports=validator_total_active_stake_lamports,
        epoch_context=epoch_context,
    )
    error_context = RewardBuildContext(
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
        validator_total_active_stake_lamports=validator_total_active_stake_lamports,
    )

    return calculated_context, error_context


def _load_reward_calculation_inputs(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
) -> RewardCalculationInputs:
    snapshot = _get_stake_snapshot(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
    )
    epoch_context = _get_epoch_reward_context(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
    )
    stake_accounts = _get_active_stake_accounts(
        db,
        snapshot_id=snapshot.id,
    )
    policies = _get_reward_policies(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
    )
    calculated_context, error_context = _build_reward_contexts(
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
        epoch_context=epoch_context,
        stake_accounts=stake_accounts,
    )

    return RewardCalculationInputs(
        stake_accounts=stake_accounts,
        policies=policies,
        calculated_context=calculated_context,
        error_context=error_context,
    )


def _build_reward_for_stake_account(
    *,
    stake_account: StakeAccount,
    policies: list[RewardPolicy],
    calculated_context: RewardBuildContext,
    error_context: RewardBuildContext,
) -> Reward:
    selected_policy = select_policy_for_staker(
        policies,
        withdrawer_authority=stake_account.withdrawer_authority,
        epoch=calculated_context.epoch,
    )

    if selected_policy is None:
        return _build_error_reward(
            stake_account=stake_account,
            context=error_context,
        )

    return _build_calculated_reward(
        stake_account=stake_account,
        policy=selected_policy,
        context=calculated_context,
    )


def _build_rewards(
    *,
    inputs: RewardCalculationInputs,
) -> list[Reward]:
    return [
        _build_reward_for_stake_account(
            stake_account=stake_account,
            policies=inputs.policies,
            calculated_context=inputs.calculated_context,
            error_context=inputs.error_context,
        )
        for stake_account in inputs.stake_accounts
    ]


def calculate_rewards_for_epoch(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
    force_recalculate: bool = False,
) -> list[Reward]:
    existing_rewards = _get_existing_rewards(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
    )
    if existing_rewards and not force_recalculate:
        return existing_rewards

    if existing_rewards and force_recalculate:
        _delete_existing_rewards(
            db,
            validator_identity_pubkey=validator_identity_pubkey,
            epoch=epoch,
        )

    inputs = _load_reward_calculation_inputs(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
    )
    rewards_to_create = _build_rewards(inputs=inputs)

    db.add_all(rewards_to_create)
    db.commit()

    for reward in rewards_to_create:
        db.refresh(reward)

    return rewards_to_create
