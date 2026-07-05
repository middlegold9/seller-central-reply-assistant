"""后端配置（品牌设置 + MCP 端点）。"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

from .types import BrandSettings


class Settings(BrandSettings, BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_prefix="SC_")

    mcp_base_url: str = ""
    mcp_token: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
