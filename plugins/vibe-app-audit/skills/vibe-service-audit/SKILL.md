---
name: vibe-service-audit
description: Audit a vibe-coded backend service, integration, ingestion job, or webhook handler against a category-specific security checklist and produce a markdown report with severity-tagged findings. Use when the user wants to security-review a non-user-facing service — a Stripe/GitHub/Shopify webhook handler, a data-ingestion job, a scheduled cron, an internal API, an API-to-API integration. Phrases like "audit my Stripe webhook handler," "review my ingestion job," "is my integration secure," "check this webhook receiver," or "audit this Lambda" all qualify. Covers webhook signature verification, API key / OAuth token handling, outbound-call safety, data egress, idempotency / replay protection, and job authentication, on top of the shared baseline (secrets, SAST, deps, monitoring). Runs safe live probes against a webhook or API base URL (unsigned / tampered / replayed / malformed payloads) and asks before any intrusive probe.
allowed-tools: Read Grep Glob Bash(grep:*) Bash(find:*) Bash(git ls-files:*) Bash(git log:*) Bash(ls:*) Bash(cat:*) Bash(head:*) Bash(curl:*) Bash(opengrep:*) Bash(semgrep:*) Bash(bun:*) Bash(npm:*) Bash(pnpm:*) Bash(yarn:*) Bash(pip-audit:*) Bash(bundle-audit:*) Bash(govulncheck:*) Bash(openssl:*) Bash(python3:*) Bash(node:*) Bash(uv tool install opengrep) Bash(uv tool install semgrep) Bash(uv tool install pip-audit) Bash(gem install --user-install bundler-audit) Bash(go install golang.org/x/vuln/cmd/govulncheck@latest) Bash(brew install opengrep) Bash(brew install semgrep) Bash(command -v:*) Bash(which:*)
---

# Vibe-coded backend service security audit

This skill audits a backend service / integration / webhook handler — the kind of repo people
vibe-code when they want to glue Stripe to their database, run a daily ingestion job, or stand up
a webhook receiver. No UI, no browser threat model. The dominant failure modes are different
from a webapp: missing or wrong signature verification, replay attacks, secret handling in
outbound calls, and error messages that leak internals.

## When to use this skill

Use this when the user wants to security-review a service with no user-facing UI. Examples:

- Stripe / Shopify / GitHub webhook receivers.
- Data ingestion jobs (cron, scheduled GitHub Actions, Vercel cron, Lambda).
- API-to-API glue (Salesforce → Postgres, HubSpot → Segment, etc.).
- Internal APIs called by other services, not by browsers.

Don't use this for: user-facing web apps (use `vibe-webapp-audit`), chat bots that handle
platform events (use `vibe-bot-audit`), manual scripts (use `vibe-script-audit`), or MCP servers
/ AI agents (use `vibe-mcp-agent-audit`).

## Inputs the skill expects

- A path to a local repo (the working directory by default).
- Optionally, a **webhook URL or API base URL** — required for live probes (signature checks,
  replay rejection, malformed payloads).
- Optionally, sample valid request signatures or shared secrets, if the user wants the live
  tests to also exercise the _signed_ path.

Ask the user for the runtime target at the start. If they don't provide one, skip live tests
and note this in the report.

## Workflow

```bash
SKILL_DIR="${CLAUDE_SKILL_DIR:-${SKILL_DIR}}"
SHARED_DIR="$SKILL_DIR/../../shared"
# Always reads:
#   $SHARED_DIR/references/baseline.md
#   $SHARED_DIR/references/live-tests-baseline.md
#   $SHARED_DIR/references/report-template.md
# Conditionally:
#   $SKILL_DIR/references/webhook-verification.md  (if any webhook endpoint found)
#   $SKILL_DIR/references/live-tests.md            (if a live target is provided)
```

1. **Detect the stack and runtime shape** (~30s — see below).
2. **Ask for the live target** (webhook URL, API base URL). Record what the user gave you.
3. **Run the baseline** (`$SHARED_DIR/references/baseline.md`, checks A–D).
4. **Run the category-specific static checks** (sections 1–6 below).
5. **Run live tests** if a target was provided. Read `$SHARED_DIR/references/live-tests-baseline.md`
   then `$SKILL_DIR/references/live-tests.md`.
6. **Render the report** using `$SHARED_DIR/references/report-template.md`.

### Detect the runtime shape

```bash
ls package.json pyproject.toml requirements.txt Gemfile go.mod 2>/dev/null
[ -f package.json ] && head -50 package.json

# Server frameworks
grep -hE "(express|fastify|hono|koa|next|fastapi|flask|django|sanic)" \
  package.json pyproject.toml requirements.txt 2>/dev/null

# Webhook endpoints
find . -path ./node_modules -prune -o \
  \( -path "*/webhooks/*" -o -path "*/webhook/*" -o -name "*webhook*" \) \
  -print | head -20

# Scheduled jobs
ls .github/workflows vercel.json fly.toml render.yaml 2>/dev/null
grep -lE "schedule:|crons|cron:" .github/workflows/*.yml vercel.json 2>/dev/null

# Outbound HTTP clients
grep -hE "(axios|got|node-fetch|undici|requests|httpx|aiohttp)" \
  package.json pyproject.toml requirements.txt 2>/dev/null
```

## 1 — Webhook signature verification

For every webhook endpoint, the handler MUST verify a signature header before reading the body.
Read `$SKILL_DIR/references/webhook-verification.md` for HMAC, JWS, and platform-specific
patterns (Stripe, GitHub, Shopify, Square, etc.).

Failure modes to flag:

- No signature check at all. **Critical**.
- Signature checked AFTER the body is parsed and acted on. **Critical** (the signature only
  helps if it gates the action).
- Signature check uses a non-constant-time comparison (`===` instead of `crypto.timingSafeEqual`
  / `hmac.compare_digest`). **High** (timing oracle).
- Signature secret is hardcoded or in `NEXT_PUBLIC_*` / similar. **Critical**.
- Custom signature scheme (rolling your own HMAC framing). **High** unless reviewed carefully.
- No timestamp check → infinite replay window. **High**.
- Timestamp check window > 15 min. **Medium**.

## 2 — API key and OAuth token handling

```bash
# Where are API keys read from?
grep -rE "process\.env\.|os\.environ\." --include="*.{ts,js,py}" . | head -30

# Tokens written to the filesystem
grep -rE "(writeFile|fs\.write|open\(.*['\"]w)" --include="*.{ts,js,py}" . | grep -iE "token|key|secret" | head -10

# OAuth token refresh logic
grep -rE "refresh_token|refreshToken" --include="*.{ts,js,py}" . | head -10
```

Flag:

- API keys read from a non-environment source (hardcoded, JSON config in repo, fetched
  unauthenticated from a URL). **Critical**.
- Tokens written to a world-readable file. **High**.
- OAuth refresh tokens stored alongside access tokens with no rotation logic. **Medium**.
- OAuth scopes broader than the service needs. **Medium**.

## 3 — Outbound calls

```bash
# TLS verification disabled
grep -rE "(rejectUnauthorized: false|verify=False|ssl=False|InsecureSkipVerify)" \
  --include="*.{ts,js,py,go}" . | head -10

# HTTP (not HTTPS) base URLs in code or env
grep -rE "http://(?!localhost|127\.)" --include="*.{ts,js,py,env*}" . | head -10
```

Flag:

- TLS verification disabled in production-path code. **Critical**.
- Cleartext HTTP for any third-party API. **High**.
- Error messages from outbound calls echoed verbatim to logs or response bodies (these often
  contain the API key or full request). **High**.

## 4 — Data egress

What data leaves the service, and where does it go?

```bash
# Logging of request/response bodies
grep -rE "(console\.log|logger\.(info|debug)|print\().*\b(body|payload|data|request|response)\b" \
  --include="*.{ts,js,py}" . | head -20

# PII fields in outbound calls
grep -rE "(email|phone|ssn|password|token|api_key)" --include="*.{ts,js,py}" . | head -20
```

Flag:

- Raw request body logged in production. **High** — logs become a secondary leak vector.
- PII forwarded to a third-party (analytics, error trackers, AI) without a data-flow comment
  or DPA reference. **Medium**.

## 5 — Idempotency and replay safety

Webhook receivers and event handlers must be safe to receive the same event twice.

- Look for an idempotency-key lookup before performing the action.
- Look for a check on a unique event/delivery ID (Stripe `event.id`, GitHub `X-GitHub-Delivery`).
- Flag handlers that perform side effects (charge a card, send an email) before recording the
  delivery ID.

**Severity:** Handler with side effects and no idempotency: **High**. Critical if the side
effect is a payment, an email to a user, or a row-write that can't be rolled back.

## 6 — Job and scheduled-trigger authentication

For cron jobs / scheduled tasks (GitHub Actions, Vercel cron, Render cron, Lambda+EventBridge):

- If the scheduled endpoint is reachable from the public internet, it must check a shared secret
  or signed header from the scheduler.
- A scheduled route that's also a public POST endpoint with no auth is a backdoor: anyone can
  trigger the job.

Look for `CRON_SECRET`, `Authorization: Bearer <token>`, or platform-specific scheduler headers
in the handler. Missing: **High**.

## Producing the report

Read `$SHARED_DIR/references/report-template.md`. Save the report to the working directory as
`vibe-service-audit-<YYYY-MM-DD>-<HHMM>.md`. Tell the user the exact path.

## What this skill is NOT

- Not a replacement for SAST/DAST/SCA tooling. It catches the common vibe-coded-service failure
  modes.
- Not a pen test. The live tests probe specific known failure modes (signature, replay,
  malformed); they don't fuzz the application.
- Not a code review. Code quality, performance, and architecture issues are out of scope.
