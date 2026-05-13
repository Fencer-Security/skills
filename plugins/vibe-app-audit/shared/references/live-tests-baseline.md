# Live test protocol

Read this from every `vibe-*-audit` skill before running any probe against a running target. This
file defines the rules the skill follows. Each category skill brings its own probe list in its
`references/live-tests.md`.

## 1 — Target acquisition

At the start of every audit, ask the user once for the runtime target appropriate to the category:

- **webapp**: deployed URL (e.g., `https://app.example.com`).
- **mobile**: backend API base URL and/or path to a built `.ipa` / `.apk` artifact.
- **service**: webhook URL or API base URL.
- **bot**: bot endpoint URL (e.g., the Slack `events_url`).
- **script**: command + safe-args invocation (the skill will run it in a tmpdir).
- **mcp-agent**: MCP transport — either `stdio: <command>` or `http: <url>`.

If the user doesn't provide one, **skip live tests entirely** and record this in the report's "Gaps
in this audit" section as: `Live tests skipped: no <category> target provided`. Continue with static
checks.

Never auto-discover the target from repo config (`vercel.json`, `fly.toml`, etc.). The risk of
probing the wrong endpoint is too high.

## 2 — Safe vs. intrusive

Every probe is classified as **safe** or **intrusive**.

**Safe probes** run by default. They are:

- Read-only (GET requests, `tools/list`, `--help`, etc.).
- Signature/authentication checks (sending unsigned/tampered/replayed requests to verify rejection —
  these do not exercise app code if the signature middleware works).
- Malformed-but-not-malicious payloads (invalid JSON, missing fields, wrong types).
- Header introspection (`curl -sI`).
- Anonymous reads against documented public endpoints (e.g., the Supabase anon key against tables,
  which exists precisely to be exercised this way).

**Before asking for intrusive-probe consent, ask yourself**: has the user named a test environment,
or am I about to send adversarial payloads to whatever URL they pasted? If the target's environment
hasn't been confirmed, ask about _that_ first, not about consent for the probe.

**Intrusive probes** require explicit consent before each batch:

- Any request that writes, mutates, or could leave state behind.
- Fuzzing (size, depth, unicode, malformed) of valid-signed requests.
- SQLi / XSS / command-injection probes.
- Rate-limit abuse tests.
- Prompt-injection payloads against LLM-forwarded endpoints.
- Running the script with adversarial arguments against non-empty fixture data.

The consent prompt must be specific: name the probe batch, say what it does, say what side effects
are possible, and ask `Proceed? [y/N]`. The default is no. Record the user's answer verbatim in the
report.

## 3 — Production guard

Before any probe (safe or intrusive), check whether the target looks production-like.
Production-like markers:

- Bare top-level domain (no `staging.`, `dev.`, `preview.`, `localhost`, IP, or platform
  preview-deploy subdomain like `*.vercel.app` / `*.netlify.app` / `*.fly.dev` / `*.ngrok.io`).
- Hostname contains `prod`, `production`, or matches the canonical product domain.

If production-like, ask before any probe:
`Target <url> looks like a production environment. Run safe probes anyway? [y/N]`. Default is no. If
the user declines, skip live tests and record this in the report.

For MCP `stdio:` targets, the production guard is bypassed (stdio means local process). For `http:`
targets, apply the same rule as web targets.

For script targets, the production guard applies if the script is invoked with a non-fixture
argument that points at a real path under `$HOME` or anything outside the tmpdir. Sandbox first; ask
before letting the script touch user data.

## 4 — Evidence shape

Every live finding (pass, fail, or inconclusive) records:

- **Probe**: short name (e.g., "unsigned webhook rejected", "anon read on `users` table").
- **Request**: method, URL or transport, key headers (one line), payload (truncated to 200 chars).
- **Response**: status, key response headers (one line), body excerpt (200 chars, PII redacted).
- **Verdict**: `pass` / `fail` / `inconclusive` and a one-sentence note.

Failed probes promote into the severity-grouped sections of the report under their own finding,
using the same severity rubric as static findings. Passed probes stay in the "Live test results"
section as evidence that the check was run.

## 5 — Cleanup

If a probe creates anything that persists (a test webhook event the receiver acknowledged, a test
tool call that wrote a file, a tmpdir for a script), the skill must clean it up before writing the
report. The report's "Live test results" section names every resource created and confirms cleanup.
If cleanup fails, the report says so loudly.

## 6 — Missing tools

Live probes may need CLIs that aren't on `PATH` (`uvx`, `openssl`, `node`, etc.). Apply the
**install-and-continue protocol** from `$SHARED_DIR/references/baseline.md`: tell the user what's
missing, show the canonical install command, ask before installing, and skip the affected probes
(not the whole audit) on decline. Record skipped probes in the report's "Gaps in this audit"
section.

## 7 — What the skill must not do under any circumstance

- Send probes to a target the user did not explicitly authorize.
- Use real credentials (production API keys, OAuth tokens with non-test scopes) for live probes.
- Probe a third-party service the target depends on. Test the target itself; don't test Stripe or
  Slack on the user's behalf.
- Continue after an intrusive probe is declined — record the decline and move on.
- Run intrusive probes against a production-like target even if the user consents in general;
  re-confirm specifically for production.
