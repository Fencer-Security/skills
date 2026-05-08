## Summary

<!-- 1–3 bullets. What's changing and why. Link issues with "Closes #N" / "Refs #N". -->

## Test plan

<!-- Checklist of what was verified. Examples:
- [ ] `./scripts/validate_manifests.py` passes
- [ ] `bun run lint`, `bun run format:check` pass
- [ ] Ran the affected skill end-to-end on a representative input; output matches the report template
- [ ] Manual smoke against [scenario]
-->

## Risk and scope

<!-- What could break? What's intentionally out of scope?
     For new skills: list any external tools the skill depends on (semgrep/opengrep, fencer CLI, etc.).
     For changes to existing skills: note whether the SKILL.md description changed (affects auto-invocation triggers). -->

## Checklist

- [ ] Plugin manifests updated where needed (`.claude-plugin/plugin.json`,
      `.codex-plugin/plugin.json`)
- [ ] `marketplace.json` updated if a new plugin is added
- [ ] README plugin table updated if a new plugin is added
- [ ] CI green
