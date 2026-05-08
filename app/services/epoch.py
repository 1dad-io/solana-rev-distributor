import httpx

from app.config import settings

DEMO_USERNAMES = {"demo_validator", "demo_staker"}
DEMO_EPOCH = 0


def get_current_epoch() -> int:
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getEpochInfo",
    }

    with httpx.Client(timeout=settings.http_timeout_seconds) as client:
        response = client.post(settings.rpc_url, json=payload)
        response.raise_for_status()

    data = response.json()
    result = data.get("result")
    if not isinstance(result, dict):
        raise ValueError("Invalid Solana RPC response: missing result object")

    epoch = result.get("epoch")
    if not isinstance(epoch, int):
        raise ValueError("Invalid Solana RPC response: missing epoch value")

    return epoch


def get_default_reward_epoch() -> int:
    current_epoch = get_current_epoch()
    return max(current_epoch - 1, 0)


def resolve_epoch_for_username(epoch: int | None, username: str) -> int:
    if epoch is not None:
        return epoch

    if username in DEMO_USERNAMES:
        return DEMO_EPOCH

    return get_default_reward_epoch()
