"""Command line interface for the sample App."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
import uvicorn

from .config import Settings
from .app_definition import write_manifest


app = typer.Typer(help="Interact with the sample OpenAI App SDK project")


@app.command()
def run_server(
    host: Optional[str] = typer.Option(None, help="Interface for the MCP server"),
    port: Optional[int] = typer.Option(None, help="Port for the MCP server"),
) -> None:
    """Start the FastAPI-based MCP server."""

    settings = Settings.load()
    uvicorn.run(
        "app.mcp_server:api",
        host=host or settings.host,
        port=port or settings.port,
        reload=False,
    )


@app.command()
def generate_manifest(
    output: Path = typer.Option(Path("build/app.json"), help="Where to write the manifest"),
) -> None:
    """Materialize the App manifest that can be imported into ChatGPT."""

    settings = Settings.load()
    manifest_path = write_manifest(output, settings)
    typer.echo(f"Wrote manifest to {manifest_path}")


@app.command()
def env() -> None:
    """Print the environment variables required by CI/CD."""

    settings = Settings.load()
    typer.echo(json.dumps(settings.to_env(), indent=2))
