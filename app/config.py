"""Configuration helpers for the OpenAI App SDK sample."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os
from typing import Any, Dict

from dotenv import load_dotenv


@dataclass
class Settings:
    """Application runtime settings for the MCP demo server."""

    host: str
    port: int
    public_url: str
    app_name: str = "Simple Context Coach"

    @classmethod
    def load(cls) -> "Settings":
        """Load settings from environment variables (optionally .env file)."""

        env_path = Path(__file__).resolve().parents[1] / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        else:
            load_dotenv()

        host = os.getenv("APP_HOST", "127.0.0.1")
        port = int(os.getenv("APP_PORT", "8000"))
        public_url = os.getenv("APP_PUBLIC_URL", f"http://{host}:{port}")

        return cls(host=host, port=port, public_url=public_url)

    def to_env(self) -> Dict[str, Any]:
        """Return a mapping that can be injected into GitHub Actions."""
        return {
            "APP_HOST": self.host,
            "APP_PORT": str(self.port),
            "APP_PUBLIC_URL": self.public_url,
        }
