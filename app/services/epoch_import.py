import hashlib
import json
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.epoch_reward_context import EpochRewardContext


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _build_rewards_source_path(epoch: int) -> Path:
    return Path(settings.validator_rewards_dir) / f"{epoch}.json"


def _extract_mev_fields(
    payload: object,
    vote_account_pubkey: str,
    epoch: int,
) -> tuple[int, int]:
    if isinstance(payload, dict):
        rewards = payload.get("rewards")
        if isinstance(rewards, list):
            for item in rewards:
                if not isinstance(item, dict):
                    continue
                if (
                    item.get("vote_account") == vote_account_pubkey
                    and item.get("epoch") == epoch
                ):
                    return (
                        int(item.get("mev_revenue") or 0),
                        int(item.get("mev_commission") or 0),
                    )

        mev_revenue = payload.get("mev_revenue_lamports")
        mev_commission_bps = payload.get("mev_commission_bps")
        if mev_revenue is not None or mev_commission_bps is not None:
            return int(mev_revenue or 0), int(mev_commission_bps or 0)

    raise ValueError(
        "Validator rewards payload does not contain matching vote_account/epoch data"
    )


def _fetch_jito_validator_rewards(
    source_path: Path,
    vote_account_pubkey: str,
    epoch: int,
) -> None:
    source_path.parent.mkdir(parents=True, exist_ok=True)

    with httpx.Client(timeout=settings.http_timeout_seconds) as client:
        response = client.get(
            settings.rpc_url_jito,
            params={
                "vote_account": vote_account_pubkey,
                "epoch": epoch,
                "limit": 100,
                "sort_order": "desc",
            },
        )
        response.raise_for_status()

    source_path.write_text(response.text, encoding="utf-8")


def _ensure_rewards_source_file(
    source_path: Path,
    *,
    vote_account_pubkey: str,
    epoch: int,
) -> None:
    if source_path.exists():
        return

    _fetch_jito_validator_rewards(
        source_path=source_path,
        vote_account_pubkey=vote_account_pubkey,
        epoch=epoch,
    )


def _load_rewards_payload(source_path: Path) -> tuple[object, str]:
    raw_text = source_path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)
    return payload, raw_text


def _get_existing_epoch_reward_context(
    db: Session,
    *,
    validator_identity_pubkey: str,
    epoch: int,
) -> EpochRewardContext | None:
    return (
        db.query(EpochRewardContext)
        .filter(
            EpochRewardContext.validator_identity_pubkey
            == validator_identity_pubkey
        )
        .filter(EpochRewardContext.cluster == settings.app_cluster)
        .filter(EpochRewardContext.epoch == epoch)
        .first()
    )


def _delete_existing_epoch_reward_context(
    db: Session,
    *,
    context_id: int,
) -> None:
    db.query(EpochRewardContext).filter(
        EpochRewardContext.id == context_id
    ).delete()
    db.commit()


def _build_epoch_reward_context(
    *,
    validator_identity_pubkey: str,
    epoch: int,
    mev_revenue_lamports: int,
    mev_commission_bps: int,
    block_rewards_lamports: int,
    uptime_bps: int,
    source_path: Path,
    raw_text: str,
) -> EpochRewardContext:
    return EpochRewardContext(
        validator_identity_pubkey=validator_identity_pubkey,
        cluster=settings.app_cluster,
        epoch=epoch,
        mev_revenue_lamports=mev_revenue_lamports,
        mev_commission_bps=mev_commission_bps,
        block_rewards_lamports=block_rewards_lamports,
        uptime_bps=uptime_bps,
        source_path=str(source_path),
        source_hash=_sha256_text(raw_text),
    )


def _create_epoch_reward_context(
    db: Session,
    *,
    context: EpochRewardContext,
) -> EpochRewardContext:
    db.add(context)
    db.commit()
    db.refresh(context)
    return context


# pylint: disable=too-many-arguments,too-many-positional-arguments
def import_epoch_reward_context(
    db: Session,
    validator_identity_pubkey: str,
    vote_account_pubkey: str,
    epoch: int,
    block_rewards_lamports: int,
    uptime_bps: int,
) -> EpochRewardContext:
    source_path = _build_rewards_source_path(epoch)

    _ensure_rewards_source_file(
        source_path,
        vote_account_pubkey=vote_account_pubkey,
        epoch=epoch,
    )

    payload, raw_text = _load_rewards_payload(source_path)

    mev_revenue_lamports, mev_commission_bps = _extract_mev_fields(
        payload=payload,
        vote_account_pubkey=vote_account_pubkey,
        epoch=epoch,
    )

    existing_context = _get_existing_epoch_reward_context(
        db,
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
    )
    if existing_context is not None:
        _delete_existing_epoch_reward_context(
            db,
            context_id=existing_context.id,
        )

    context = _build_epoch_reward_context(
        validator_identity_pubkey=validator_identity_pubkey,
        epoch=epoch,
        mev_revenue_lamports=mev_revenue_lamports,
        mev_commission_bps=mev_commission_bps,
        block_rewards_lamports=block_rewards_lamports,
        uptime_bps=uptime_bps,
        source_path=source_path,
        raw_text=raw_text,
    )
    return _create_epoch_reward_context(db, context=context)
