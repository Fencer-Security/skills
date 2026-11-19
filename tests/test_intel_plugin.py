"""The intel plugin stays on the public Fencer Intel MCP server.

No live network. The tool list in tests/fixtures is a recording of tools/list.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "intel"

# Paths and credentials the public plugin must not wire up.
FORBIDDEN = (
    "/app/v1",
    "/admin",
    "ADMIN_TOKEN",
    "ACCESS_AUD",
    "CF-Access",
    "workers.dev",
    "packages.wolfi.dev",
    "packages.cgr.dev",
    "advisory.echohq.com",
    "packages.mini.dev",
)


def _plugin_texts() -> list[tuple[Path, str]]:
    texts: list[tuple[Path, str]] = []
    for path in PLUGIN.rglob("*"):
        if path.is_file() and path.suffix in {".md", ".json"}:
            texts.append((path, path.read_text()))
    return texts


def test_mcp_config_is_public_and_unauthenticated() -> None:
    data = json.loads((PLUGIN / ".mcp.json").read_text())
    servers = data["mcpServers"]
    assert list(servers) == ["fencer-intel"]
    assert servers["fencer-intel"] == {"type": "http", "url": "https://intel.fencer.dev/mcp"}


def test_manifests_match_and_point_at_mcp_json() -> None:
    claude = (PLUGIN / ".claude-plugin" / "plugin.json").read_text()
    codex = (PLUGIN / ".codex-plugin" / "plugin.json").read_text()
    assert claude == codex
    manifest = json.loads(claude)
    assert manifest["name"] == "fencer-intel"
    assert manifest["license"] == "Apache-2.0"
    assert manifest["mcpServers"] == "./.mcp.json"
    assert manifest["version"] == "0.1.0"


def test_marketplace_and_readme_list_the_plugin() -> None:
    market = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    entry = next(plugin for plugin in market["plugins"] if plugin["name"] == "fencer-intel")
    assert entry["source"] == "./plugins/intel"
    assert "plugins/intel/" in (ROOT / "README.md").read_text()


def test_skills_stay_on_the_public_surface() -> None:
    texts = _plugin_texts()
    blob = "\n".join(text for _, text in texts)
    for token in FORBIDDEN:
        assert token not in blob, token

    reference = (PLUGIN / "shared" / "references" / "using-intel.md").read_text()
    assert "https://intel.fencer.dev/mcp" in reference
    assert "CC BY-SA 4.0" in reference
    assert "not endorsed or certified by the NVD" in reference
    assert "never retrieve or display" in reference.lower() or "Never retrieve or display" in reference

    skills = sorted((PLUGIN / "skills").glob("*/SKILL.md"))
    assert [path.parent.name for path in skills] == [
        "intel-brief",
        "intel-check-deps",
        "intel-triage",
    ]
    for skill in skills:
        text = skill.read_text()
        assert text.startswith("---\n")
        end = text.find("\n---", 4)
        frontmatter = yaml.safe_load(text[4:end])
        assert frontmatter["name"] == skill.parent.name
        assert 1 <= len(frontmatter["description"]) <= 1024
        assert "intel.fencer.dev" in text
        assert "using-intel.md" in text
        assert "Sources" in text
        assert frontmatter["allowed-tools"] == "Read"


def test_recorded_tool_contract_is_documented() -> None:
    recorded = json.loads((ROOT / "tests" / "fixtures" / "fencer-intel-tools.json").read_text())
    reference = (PLUGIN / "shared" / "references" / "using-intel.md").read_text()
    assert recorded["url"] == "https://intel.fencer.dev/mcp"
    assert recorded["source"].startswith("POST https://intel.fencer.dev/mcp")
    names = [tool["name"] for tool in recorded["tools"]]
    assert names == ["search", "get_vulnerability", "list_feed", "check_stack"]
    for tool in recorded["tools"]:
        assert tool["name"] in reference
        for argument in tool["arguments"]:
            assert f"`{argument}`" in reference, argument
