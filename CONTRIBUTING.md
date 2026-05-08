# Contributing

Thanks for your interest in extending Fencer's skill marketplace.

## Quick start

```bash
# Bootstrap dev tooling (uv, bun, pre-commit)
mise run sync-all

# Scaffold a new plugin
mise run new-plugin my-plugin "What this plugin does, in one line."

# Add an entry for the new plugin to .claude-plugin/marketplace.json
# Then create skills under plugins/my-plugin/skills/<skill-name>/SKILL.md

# Validate + lint before opening a PR
mise run lint
mise run validate
```

## Repo layout

See [AGENTS.md](AGENTS.md) for the full layout and conventions. In brief:

```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json   # Claude Code manifest
├── .codex-plugin/plugin.json    # Codex manifest (same content)
└── skills/<skill-name>/
    ├── SKILL.md                 # the open Agent Skills format
    └── scripts/                 # optional helpers (Python/TS)
```

## Skill authoring rules

1. **`SKILL.md` frontmatter must include `name` and `description`.** Description should read like a
   trigger phrase, third person, and mention when the skill is useful.
2. **Python helpers are PEP-723 single files.** Use `#!/usr/bin/env -S uv run --script` and inline
   `# /// script` metadata for dependencies. No per-skill `pyproject.toml`.
3. **TypeScript helpers run under bun directly.** No build step. Add a per-skill `package.json` only
   if the helper has runtime npm dependencies.
4. **Reference scripts portably.** Use `${CLAUDE_SKILL_DIR:-${SKILL_DIR}}` so the same `SKILL.md`
   works in Claude Code and Codex.
5. **External tools (`fencer`, `gh`, etc.) are checked, not bundled.** A skill should
   `command -v <tool>` and tell the user how to install it if missing.

## License

By contributing, you agree your contributions are licensed under the
[Apache License, Version 2.0](LICENSE).
