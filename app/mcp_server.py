"""Minimal MCP-style server backed by local data."""
from __future__ import annotations

from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

api = FastAPI(title="Simple Context Coach", version="0.1.0")

PROJECT_NOTES: Dict[str, str] = {
    "onboarding": (
        "The onboarding checklist covers environment bootstrapping, style guides, "
        "and CI expectations. Encourage makers to run appsdk env and review "
        "README sections before sharing the manifest."
    ),
    "deployment": (
        "Deployment happens via GitHub Actions which lints the project and uploads "
        "build/app.json as an artifact. Import the artifact into ChatGPT to update "
        "the app."
    ),
    "backlog": (
        "Backlog items include capturing screenshots for UI changes and adding more "
        "MCP endpoints that expose internal data sources."
    ),
}

ROADMAP = [
    "✅ Local MCP server boots with `appsdk run-server`.",
    "✅ Manifest generation documents the HTTP endpoints exposed to ChatGPT.",
    "🚧 Next: proxy CRM data through a new tool once the API is available.",
]


class ToolDescription(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, object]


class ToolListResponse(BaseModel):
    tools: Dict[str, ToolDescription]


class ToolInvocation(BaseModel):
    tool: str
    arguments: Dict[str, str] = Field(default_factory=dict)


class ToolResult(BaseModel):
    content: str
    source: str


@api.get("/health")
def health() -> Dict[str, str]:
    """Simple readiness probe."""

    return {"status": "ok"}


@api.get("/mcp/tools")
def list_tools() -> ToolListResponse:
    """Return a catalog of callable tools."""

    tools = {
        "project_notes": ToolDescription(
            name="project_notes",
            description="Look up curated onboarding and deployment notes.",
            input_schema={
                "type": "object",
                "properties": {"topic": {"type": "string", "description": "topic name"}},
                "required": ["topic"],
            },
        ),
        "roadmap_status": ToolDescription(
            name="roadmap_status",
            description="Summarize the next milestones for this automation project.",
            input_schema={"type": "object", "properties": {}},
        ),
    }
    return ToolListResponse(tools=tools)


@api.post("/mcp/tools/invoke")
def invoke_tool(payload: ToolInvocation) -> ToolResult:
    """Execute a tool request coming from ChatGPT."""

    if payload.tool == "project_notes":
        topic = payload.arguments.get("topic", "").lower()
        if topic not in PROJECT_NOTES:
            raise HTTPException(status_code=404, detail="Unknown topic")
        return ToolResult(content=PROJECT_NOTES[topic], source="project_notes")

    if payload.tool == "roadmap_status":
        return ToolResult(content="\n".join(ROADMAP), source="roadmap_status")

    raise HTTPException(status_code=404, detail="Unknown tool")
