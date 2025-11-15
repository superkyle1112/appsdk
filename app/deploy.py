"""Deployment helper executed by CI/CD."""
from __future__ import annotations

from pathlib import Path

from .config import Settings
from .app_definition import write_manifest


BUILD_DIR = Path("build")


def main() -> None:
    settings = Settings.load()
    manifest_path = write_manifest(BUILD_DIR / "app.json", settings)
    print(f"Manifest ready: {manifest_path}")
    print("Upload the manifest via the ChatGPT UI by importing the generated file.")


if __name__ == "__main__":  # pragma: no cover - module is script entry point
    main()
