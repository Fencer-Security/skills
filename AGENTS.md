# AGENTS.md

Guidance for AI agents (Claude Code, Codex, Gemini, Copilot) and human contributors working **on**
this repository.

## What this repo is

A public marketplace of plugins for Claude Code and Codex. Each plugin contains one or more skills
following the open [Agent Skills](https://agentskills.io) standard (`SKILL.md` with YAML
frontmatter).

## Layout

```
.claude-plugin/marketplace.json   # Claude Code marketplace catalog
plugins/<plugin>/
  .claude-plugin/plugin.json      # Claude Code plugin manifest
  .codex-plugin/plugin.json       # Codex plugin manifest (mirrors Claude manifest)
  README.md
  skills/<skill>/SKILL.md         # the portable artifact (open standard)
  skills/<skill>/scripts/         # optional helpers (Python or TS)
  .mcp.json                       # optional, registers MCP servers
scripts/                          # repo-level dev tooling (NOT shipped in plugins)
.github/workflows/                # CI: validate, lint, test-skills
pyproject.toml                    # uv: dev deps only
package.json                      # bun: dev deps only
```

## Adding a plugin

```bash
./scripts/new_plugin.sh my-plugin "One-line description."
```

Then:

1. Add an entry for `my-plugin` to `.claude-plugin/marketplace.json` under `plugins`.
2. Create skills under `plugins/my-plugin/skills/<skill-name>/SKILL.md`.
3. Run `./scripts/validate_manifests.py`.

## Skill conventions

### Frontmatter (required)

```yaml
---
name: my-skill
description: One-line trigger description in third person, mentions when to use.
allowed-tools: Bash Read Grep
---
```

`description` should read as a trigger — when an agent reads it, they should immediately know
whether this skill applies. Keep it under 1024 chars.

### Script portability

Both Claude Code (`${CLAUDE_SKILL_DIR}`) and Codex (`${SKILL_DIR}`) inject the skill directory as an
env var, but with different names. In `SKILL.md` shell snippets, use:

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${SKILL_DIR}}"
"$SKILL_DIR/scripts/refresh.py" "$@"
```

### Python helpers

Single-file [PEP 723](https://peps.python.org/pep-0723/) scripts. The shebang invokes
`uv run --script`, which resolves dependencies on first run:

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["httpx", "pydantic>=2"]
# ///
"""What this script does."""
...
```

Don't add a `pyproject.toml` per skill. The skill stays self-contained and copy-pasteable.

### TypeScript helpers

`bun run script.ts` runs `.ts` directly with no build step. Add a per-skill `package.json` only if
the helper needs runtime npm deps; otherwise inline imports are enough.

### External CLIs

If a skill drives an external CLI (`fencer`, `gh`, `terraform`, etc.), **check before invoking** and
tell the user how to install if it's missing:

```bash
if ! command -v <tool> >/dev/null; then
  echo "<tool> not found. Install: <project's documented install command>" >&2
  exit 1
fi
```

The Fencer Go CLI is not bundled in this repo — users install it separately.

## Local validation

Toolchain mirrors the [`fencer/app`](../app/) repo: ruff for Python, oxlint + oxfmt for
JS/TS/configs, codespell for spelling, pre-commit to wire it together. `mise` runs the canonical
task names.

```bash
mise run sync-all     # uv sync + bun install + pre-commit install
mise run lint         # ruff + oxlint + oxfmt --check
mise run format       # ruff format + ruff --fix + oxfmt
mise run validate     # marketplace + plugin + SKILL.md frontmatter
mise run pre-commit-all
```

Or directly without mise:

```bash
uv run ruff check .
uv run ruff format --check .
bun run lint                # oxlint
bun run format:check        # oxfmt --check
./scripts/validate_manifests.py
```

## Publishing

Pushing to `main` is enough — Claude Code reads the `marketplace.json` from the default branch. Tag
releases with semver (`v0.1.0`) so plugin `version` fields can pin against tags if needed.

## License

Apache-2.0. All new plugin manifests must declare `"license": "Apache-2.0"`. The repo's
[NOTICE](NOTICE) file holds attribution and trademark notices required by Section 6.
