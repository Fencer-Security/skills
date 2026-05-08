#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["jsonschema>=4.23", "pyyaml>=6"]
# ///
"""Validate marketplace + plugin manifests and SKILL.md frontmatter across the repo."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent

MARKETPLACE_SCHEMA: dict = {
    "type": "object",
    "required": ["name", "owner", "plugins"],
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "description": {"type": "string"},
        "owner": {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}, "url": {"type": "string"}},
        },
        "plugins": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "source"],
                "properties": {
                    "name": {"type": "string", "minLength": 1},
                    "source": {"type": ["string", "object"]},
                    "description": {"type": "string"},
                },
            },
        },
    },
}

PLUGIN_SCHEMA: dict = {
    "type": "object",
    "required": ["name", "description", "version"],
    "properties": {
        "name": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
        "description": {"type": "string", "minLength": 1},
        "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+"},
        "author": {"type": "object"},
        "homepage": {"type": "string"},
        "repository": {"type": "string"},
        "license": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
    },
}

SKILL_FRONTMATTER_SCHEMA: dict = {
    "type": "object",
    "required": ["name", "description"],
    "properties": {
        "name": {"type": "string", "pattern": "^[a-z0-9][a-z0-9-]*$"},
        "description": {"type": "string", "minLength": 1, "maxLength": 1024},
        "allowed-tools": {"type": "string"},
        "model": {"type": "string"},
    },
}


def parse_skill_frontmatter(path: Path) -> dict:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing YAML frontmatter")
    end = text.find("\n---", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated YAML frontmatter")
    return yaml.safe_load(text[4:end]) or {}


def _format_error(path: Path, err) -> str:
    location = "/".join(map(str, err.path)) or "<root>"
    return f"{path}: {err.message} (at {location})"


def validate_json(path: Path, schema: dict) -> list[str]:
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        return [f"{path}: invalid JSON: {e}"]
    validator = Draft202012Validator(schema)
    return [_format_error(path, e) for e in validator.iter_errors(data)]


def validate_skill(path: Path) -> list[str]:
    try:
        fm = parse_skill_frontmatter(path)
    except ValueError as e:
        return [str(e)]
    validator = Draft202012Validator(SKILL_FRONTMATTER_SCHEMA)
    return [_format_error(path, e) for e in validator.iter_errors(fm)]


def main() -> int:
    errors: list[str] = []

    marketplace = REPO / ".claude-plugin" / "marketplace.json"
    if marketplace.exists():
        errors += validate_json(marketplace, MARKETPLACE_SCHEMA)
    else:
        errors.append(f"{marketplace}: missing")

    for plugin_json in REPO.glob("plugins/*/.claude-plugin/plugin.json"):
        errors += validate_json(plugin_json, PLUGIN_SCHEMA)
    for plugin_json in REPO.glob("plugins/*/.codex-plugin/plugin.json"):
        errors += validate_json(plugin_json, PLUGIN_SCHEMA)

    for skill_md in REPO.glob("plugins/*/skills/*/SKILL.md"):
        errors += validate_skill(skill_md)

    if errors:
        for err in errors:
            print(f"ERROR  {err}", file=sys.stderr)
        print(f"\n{len(errors)} error(s).", file=sys.stderr)
        return 1

    print("All manifests and skills valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
