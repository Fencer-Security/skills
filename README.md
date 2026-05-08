# Fencer Skills

Public marketplace of [Claude Code](https://code.claude.com) and [Codex](https://developers.openai.com/codex) plugins from Fencer.

## Plugins

| Plugin | Description |
| --- | --- |
| [`vibe-app-audit`](plugins/vibe-app-audit/) | Security audit skills for AI-generated web apps (Lovable, v0, Bolt, Cursor output). |
| [`compliance`](plugins/compliance/) | SOC 2 vendor diligence and related compliance review skills. |

## Install

### Claude Code

```
/plugin marketplace add https://github.com/Fencer-Security/skills
/plugin install <plugin-name>@fencer
```

### Codex

Codex's marketplace catalog format is still stabilizing. For now, install plugins manually:

```bash
git clone https://github.com/Fencer-Security/skills ~/src/fencer-skills
ln -s ~/src/fencer-skills/plugins/<plugin-name> ~/.codex/plugins/<plugin-name>
```

Or drop individual `SKILL.md` files into `~/.agents/skills/` — they conform to the open [Agent Skills](https://agentskills.io) standard and work in Codex CLI, Claude Code, Gemini CLI, and Copilot.

## License

Licensed under the [Apache License, Version 2.0](LICENSE). See [NOTICE](NOTICE) for attribution and trademark terms — "Fencer" is a trademark and is not licensed for use beyond attribution.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to add a new plugin or skill. See [AGENTS.md](AGENTS.md) for guidance when working on this repo with an agent (Claude Code, Codex, etc.).
