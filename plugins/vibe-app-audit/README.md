# vibe-app-audit

Security audit skills for vibe-coded projects — the kind of code Lovable, Bolt, v0, Replit,
Cursor, and Claude Code ship that *looks* secure but isn't. Validation in the browser only. RLS
"enabled" with no policies. Webhook handlers that skip signature checks. MCP servers that hand
the LLM a shell tool with no parameter validation. Scripts that shell out with `; rm -rf`.

This plugin contains a classifier plus five category-specific auditors. Each runs the shared
baseline (secrets, SAST, deps, monitoring) plus category-specific static checks, and — if the
user provides a runtime target — safe live probes against the running thing. Intrusive probes
need explicit consent.

## Skills

- **[`vibe-audit`](skills/vibe-audit/SKILL.md)** — Classifier. Detects what kind of vibe-coded
  thing is in the repo and recommends which category skill to run. Does no auditing itself.
  Triggers on generic phrases like "audit my project" or "what audit should I run."
- **[`vibe-webapp-audit`](skills/vibe-webapp-audit/SKILL.md)** — User-facing web apps.
  Supabase RLS / Postgres app-layer access controls, server-side validation, IDOR, security
  headers. Live: anonymous reads, header probes, error-page leakage.
- **[`vibe-mobile-audit`](skills/vibe-mobile-audit/SKILL.md)** — Mobile apps (Expo, React
  Native, native iOS / Android). Secret storage (Keychain / Keystore vs AsyncStorage), network
  security (ATS, cert pinning), deep links and URL schemes, WebView / JS bridges, permissions,
  backup-included data. Live: backend API probes + IPA/APK bundle inspection for embedded
  secrets.
- **[`vibe-service-audit`](skills/vibe-service-audit/SKILL.md)** — Backend services, webhook
  handlers, ingestion jobs, internal APIs. Signature verification, OAuth / API key handling,
  idempotency, replay protection. Live: unsigned / tampered / replayed / malformed payloads.
- **[`vibe-bot-audit`](skills/vibe-bot-audit/SKILL.md)** — Slack, Discord, GitHub, Teams bots.
  Platform signature verification (HMAC, ed25519), OAuth scope minimization, token storage,
  prompt-injection for LLM-forwarded bots. Live: signature / replay / timestamp rejection.
- **[`vibe-script-audit`](skills/vibe-script-audit/SKILL.md)** — Manual or scheduled
  scripts and CLI tools. Argument handling, subprocess / shell-out, file I/O, credential
  hygiene, blast-radius. Live: path-traversal / shell-metachar / bad-credfile / missing-credfile
  probes in an isolated tmpdir.
- **[`vibe-mcp-agent-audit`](skills/vibe-mcp-agent-audit/SKILL.md)** — MCP servers and AI
  agents. Tool surface, parameter validation, prompt injection (direct and indirect via tool
  outputs), output sanitization, resource limits. Live: tool enumeration, missing-param /
  wrong-type / oversized-input rejection, SSRF probes.

## How the skills load (for cache efficiency)

Each audit follows the same three-layer load order, which keeps stable content stable across
invocations and lets a caching harness (e.g., Anthropic prompt caching) place breakpoints
predictably:

1. **L1 metadata** — `description` fields (~1,200 tokens, always loaded).
2. **L3 shared references** — `shared/references/baseline.md`,
   `live-tests-baseline.md`, `report-template.md` (~5,400 tokens, identical across all audits).
3. **L2 SKILL.md body + L3 category references** — the triggered skill and its conditional
   references (size varies by category and detection).

The shared L3 files contain no per-invocation values (no timestamps, paths, or task-specific
content), so they're cache-stable. A harness can cache the metadata + shared L3 block once and
reuse it across audits within the TTL.

## What this is not

- Not a replacement for a SAST/DAST/SCA platform. It's one-pass auditing that catches the
  common vibe-coded failure modes.
- Not a pen test. Live tests probe specific known failure modes; they don't fuzz the
  application.
- Not a compliance audit. Doesn't map to SOC 2, ISO 27001, or any framework.
- Not a code review. Code quality, performance, and architecture are out of scope.

## Install

```
/plugin marketplace add https://github.com/Fencer-Security/skills
/plugin install vibe-app-audit@fencer
```

## License

[Apache-2.0](../../LICENSE).
