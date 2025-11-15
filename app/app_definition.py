"""Generate the App manifest used by ChatGPT."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import json
from typing import Any, Dict, List

from .prompts import APP_INSTRUCTIONS
from .config import Settings


@dataclass
class Tool:
    """Represents a lightweight tool entry in the App manifest."""

    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class Server:
    """Describe the MCP server that powers the App."""

    type: str
    url: str


@dataclass
class AppManifest:
    """Manifest for the sample OpenAI App SDK project."""

    name: str
    description: str
    instructions: str
    model: str
    sample_questions: List[str]
    tools: List[Tool]
    server: Server

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["tools"] = [asdict(tool) for tool in self.tools]
        data["server"] = asdict(self.server)
        return data


def build_manifest(settings: Settings) -> AppManifest:
    """Return the manifest used for both local dev and deployment."""

    return AppManifest(
        name=settings.app_name,
        description=(
            "A demo App SDK project whose logic runs on a standalone MCP server. It "
            "exposes local context without requiring an OpenAI API key."
        ),
        instructions=APP_INSTRUCTIONS,
        model="gpt-4.1-mini",
        sample_questions=[
            "What deployment stages are still in progress?",
            "Summarize the notes about the automation backlog.",
            "How does this app avoid using my API key?",
        ],
        tools=[
            Tool(
                name="project_notes",
                description="Query the knowledge base that backs Simple Context Coach.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "description": "Topic such as onboarding, deployment, or backlog",
                        }
                    },
                    "required": ["topic"],
                },
            ),
            Tool(
                name="roadmap_status",
                description="Summarize the latest deployment and integration states.",
                input_schema={"type": "object", "properties": {}},
            ),
        ],
        server=Server(type="mcp", url=settings.public_url),
    )


def write_manifest(output_path: Path, settings: Settings) -> Path:
    """Persist the manifest to disk."""

    manifest = build_manifest(settings)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest.to_dict(), fh, indent=2)
    return output_path
