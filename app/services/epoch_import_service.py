import hashlib
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.config import settings
from app.models.epoch_reward_context import EpochRewardContext


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_mev_fields(payload: object) -> tuple[int, int]:
    if isinstance(payload, dict):
        mev_revenue = payload.get("mev_revenue_lamports")
        mev_commission_bps = payload.get("mev_commission_bps")

        if mev_revenue is not None or mev_commission_bps is not None:
            return int(mev_revenue or 0), int(mev_commission_bps or 0)

        for key in ("data", "result", "rewards"):
            nested = payload.get(key)
            if isinstance(nested, dict):
                mev_revenue = nested.get("mev_revenue_lamports")
                mev_commission_bps = nested.get("mev_commission_bps")
                if mev_revenue is not None or mev_commission_bps is not None:
                    return int(mev_revenue or 0), int(mev_commission_bps or 0)

    raise ValueError(
        "Validator rewards file must contain mev_revenue_lamports and mev_commission_bps"
    )


def import_epoch_reward_context(
    db: Session,
    validator_identity_pubkey: str,
    epoch: int,
    block_rewards_lamports: int,
    uptime_bps: int,
) -> EpochRewardContext:
    source_path = Path(settings.validator_rewards_dir) / f"{epoch}.json"
    if not source_path.exists():
        raise FileNotFoundError(str(source_path))

    raw_text = source_path.read_text(encoding="utf-8")
    payload = json.loads(raw_text)

    mev_revenue_lamports, mev_commission_bps = _extract_mev_fields(payload)

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
