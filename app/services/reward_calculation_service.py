from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.config import settings
from app.models.epoch_reward_context import EpochRewardContext
from app.models.reward import Reward
from app.models.reward_policy import RewardPolicy
from app.models.stake_account import StakeAccount
from app.models.stake_snapshot import StakeSnapshot
from app.models.user import User


def calculate_rewards_for_epoch(
    db: Session,
    validator_identity_pubkey: str,
    epoch: int,
    force_recalculate: bool = False,
) -> list[Reward]:
    if force_recalculate:
        (
            db.query(Reward)
            .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
            .filter(Reward.cluster == settings.app_cluster)
            .filter(Reward.epoch == epoch)
            .delete()
        )
        db.commit()

    existing_rewards = (
        db.query(Reward)
        .filter(Reward.validator_identity_pubkey == validator_identity_pubkey)
        .filter(Reward.cluster == settings.app_cluster)
        .filter(Reward.epoch == epoch)
        .all()
    )
    if existing_rewards and not force_recalculate:
        return existing_rewards

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
        .all()
    )

    total_active_stake = sum(account.active_stake_lamports or 0 for account in stake_accounts)
    if total_active_stake <= 0:
        return []

    created_rewards: list[Reward] = []

    for account in stake_accounts:
        withdrawer = account.withdrawer_authority
        if not withdrawer:
            continue

        user = (
            db.query(User)
            .filter(User.role == "staker")
            .filter(User.staker_withdrawer_pubkey == withdrawer)
            .first()
        )
        if user is None:
            continue

        epoch_compatible_filters = (
            or_(RewardPolicy.valid_from_epoch.is_(None), RewardPolicy.valid_from_epoch <= epoch),
            or_(RewardPolicy.valid_to_epoch.is_(None), RewardPolicy.valid_to_epoch >= epoch),
        )

        policy = (
            db.query(RewardPolicy)
            .filter(RewardPolicy.validator_identity_pubkey == validator_identity_pubkey)
            .filter(RewardPolicy.cluster == settings.app_cluster)
            .filter(RewardPolicy.is_active.is_(True))
            .filter(RewardPolicy.staker_withdrawer_pubkey == withdrawer)
            .filter(*epoch_compatible_filters)
            .order_by(RewardPolicy.created_at.desc())
            .first()
        )

        if policy is None:
            policy = (
                db.query(RewardPolicy)
                .filter(RewardPolicy.validator_identity_pubkey == validator_identity_pubkey)
                .filter(RewardPolicy.cluster == settings.app_cluster)
                .filter(RewardPolicy.is_active.is_(True))
                .filter(RewardPolicy.is_default.is_(True))
                .filter(*epoch_compatible_filters)
                .order_by(RewardPolicy.created_at.desc())
                .first()
            )

        active_stake = account.active_stake_lamports or 0

        gross_mev_reward = (
            epoch_context.mev_revenue_lamports * active_stake // total_active_stake
        )
        gross_block_reward = (
            epoch_context.block_rewards_lamports * active_stake // total_active_stake
        )

        status = "calculated"
        payable_reward = 0
        mev_bps_back_used = None
        block_rewards_bps_back_used = None
        policy_id_used = None

        if policy is None:
            status = "error_no_policy"
            gross_reward = 0
        else:
            mev_bps_back_used = policy.mev_bps_back
            block_rewards_bps_back_used = policy.block_rewards_bps_back
            policy_id_used = policy.id

            gross_mev_reward = gross_mev_reward * policy.mev_bps_back // 10000
            gross_block_reward = (
                gross_block_reward * policy.block_rewards_bps_back // 10000
            )
            gross_reward = gross_mev_reward + gross_block_reward

            if not user.is_active:
                status = "excluded_inactive_user"
                payable_reward = 0
            else:
                payable_reward = gross_reward

        reward = Reward(
            validator_identity_pubkey=validator_identity_pubkey,
            cluster=settings.app_cluster,
            epoch=epoch,
            stake_account_id=account.id,
            policy_id_used=policy_id_used,
            staker_withdrawer_pubkey=withdrawer,
            stake_pubkey=account.stake_pubkey,
            withdrawer_authority=withdrawer,
            active_stake_lamports=active_stake,
            validator_total_active_stake_lamports=total_active_stake,
            mev_bps_back_used=mev_bps_back_used,
            block_rewards_bps_back_used=block_rewards_bps_back_used,
            gross_mev_reward_lamports=gross_mev_reward,
            gross_block_reward_lamports=gross_block_reward,
            gross_reward_lamports=gross_reward,
            payable_reward_lamports=payable_reward,
            status=status,
        )
        db.add(reward)
        created_rewards.append(reward)

    db.commit()

    for reward in created_rewards:
        db.refresh(reward)

    return created_rewards
