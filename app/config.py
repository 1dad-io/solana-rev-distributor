from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "solana-rev-distributor"
    app_cluster: str = "testnet"
    database_url: str = "sqlite:///./data/testnet/app.db"
    data_dir: str = "./data/testnet"
    stakes_dir: str = "./data/testnet/stakes"
    validator_rewards_dir: str = "./data/testnet/validator_rewards"
    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
