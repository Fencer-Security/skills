# vibe-app-audit

Security audit skills for AI-generated web apps — the kind of code Lovable, v0, Bolt, Cursor, and Claude Code ship that *looks* secure but isn't. Validation in the browser only. RLS "enabled" with no policies. The service role key in `NEXT_PUBLIC_*`. Auth checks asking "is the user logged in" instead of "does this user own this row."

## Skills

- **[`vibe-app-audit`](skills/vibe-app-audit/SKILL.md)** — Walks a local repo through eight security categories and writes a severity-tagged markdown report. Triggers automatically when a user asks to "audit," "security-review," or "find the security issues in" an AI-generated app.

The eight categories:

1. Exposed secrets (service role keys in client bundles, `.env` in git history)
2. Database access controls (Supabase RLS, plain Postgres ownership filters)
3. Server-side input validation (vs. browser-only)
4. Authorization checks (IDOR, the canonical AI-coded bug)
5. Security headers (CSP, HSTS, X-Frame-Options)
6. Static analysis (semgrep with security-focused rulesets)
7. Dependency audit (lockfile-detected: `bun audit`, `npm audit`, `pip-audit`, `bundle-audit`, `govulncheck`)
8. Monitoring and logging gaps

## What this is not

- Not a replacement for a SAST/DAST/SCA platform. It's a one-pass audit that catches the common vibe-coding failure modes.
- Not a pen test. Doesn't probe runtime vulns beyond a header check.
- Not a compliance audit. Doesn't map to SOC 2, ISO 27001, or any framework.
- Not a code review. Code quality, performance, and architecture are out of scope.

## Install

```
/plugin marketplace add https://github.com/Fencer-Security/skills
/plugin install vibe-app-audit@fencer
```

## License

[Apache-2.0](../../LICENSE).
