import hashlib
import json
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.epoch_reward_context import EpochRewardContext


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


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
                if item.get("vote_account") == vote_account_pubkey and item.get("epoch") == epoch:
                    return int(item.get("mev_revenue") or 0), int(item.get("mev_commission") or 0)

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


def import_epoch_reward_context(
    db: Session,
    validator_identity_pubkey: str,
    vote_account_pubkey: str,
    epoch: int,
    block_rewards_lamports: int,
    uptime_bps: int,
) -> EpochRewardContext:
    source_path = Path(settings.validator_rewards_dir) / f"{epoch}.json"

    if not source_path.exists():
        _fetch_jito_validator_rewards(
            source_path=source_path,
            vote_account_pubkey=vote_account_pubkey,
            epoch=epoch,
        )

    raw_text = source_path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)

    mev_revenue_lamports, mev_commission_bps = _extract_mev_fields(
        payload=payload,
        vote_account_pubkey=vote_account_pubkey,
        epoch=epoch,
    )

    existing_context = (
        db.query(EpochRewardContext)
        .filter(EpochRewardContext.validator_identity_pubkey == validator_identity_pubkey)
        .filter(EpochRewardContext.cluster == settings.app_cluster)
        .filter(EpochRewardContext.epoch == epoch)
        .first()
    )

    if existing_context:
        db.delete(existing_context)
        db.commit()

    context = EpochRewardContext(
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

    db.add(context)
    db.commit()
    db.refresh(context)
    return context
