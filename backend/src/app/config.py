from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CARECOMPASS_", env_file=".env", extra="ignore"
    )

    app_name: str = "Care Compass"
    support_contacts_path: Path = (
        Path(__file__).resolve().parents[2] / "config/support_contacts.json"
    )
    chat_engine: Literal["echo", "langgraph"] = "echo"
    prompt_path: Path = Path(__file__).resolve().parents[2] / "prompts/assistant.md"
    foundry_base_url: str | None = None
    foundry_deployment: str | None = None
    foundry_api_key: SecretStr | None = None
    agent_timeout_seconds: float = Field(default=15, gt=0, le=120)
    agent_max_steps: int = Field(default=6, ge=2, le=20)
    agent_max_output_tokens: int = Field(default=600, ge=64, le=4096)
    catalog_path: Path = (
        Path(__file__).resolve().parents[3] / "data/processed/services.sample.json"
    )
