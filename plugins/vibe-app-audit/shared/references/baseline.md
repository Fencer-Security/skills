# Baseline static checks

Read this from every `vibe-*-audit` skill. These four checks apply regardless of category — they
catch failures that show up in webapps, services, bots, scripts, and MCP/agent code alike.

Run them in order. Each is independent; finish one, write findings to a running list, move on.

## Missing tools — install-and-continue protocol

Several checks need an external CLI (`opengrep`, `pip-audit`, `bundle-audit`, `govulncheck`, etc.).
When a required tool is not on `PATH`:

1. **Tell the user what's missing and what it does.** One sentence each.
2. **Show the install command.** Use the canonical one for the user's platform (see the per-tool
   table below). Prefer methods that don't need sudo — `uv tool install`, `pipx`, `go install`,
   `gem install --user-install`, package managers the user already has.
3. **Ask: `Install <tool> with <command> and then run the check? [y/N]`.** Default no.
4. **On yes:** run the install command, verify the binary is now on `PATH`, then run the check. If
   the install fails, record the error in the report and continue without the check (do not retry or
   escalate to sudo).
5. **On no:** skip the check and record in the report's "Gaps in this audit" section:
   `<check> skipped: <tool> not installed and user declined install`.

Never install anything without an explicit yes. Never use `sudo`. Never alter the user's shell init
files — if a binary lands in a directory not on `PATH` (e.g., `~/.local/bin`), tell the user the
absolute path and what to add to their `PATH`, then skip the check this run.

Canonical install commands:

| Tool                | Command                                                                        | Notes                                                  |
| ------------------- | ------------------------------------------------------------------------------ | ------------------------------------------------------ |
| `gitleaks`          | `brew install gitleaks` or `go install github.com/gitleaks/gitleaks/v8@latest` | Purpose-built secret scanner; 100+ rules + git history |
| `opengrep`          | `uv tool install opengrep` (preferred)                                         | LGPL-2.1 OSS fork of semgrep; same ruleset shortcuts   |
| `semgrep`           | `uv tool install semgrep` or `brew install semgrep`                            | Fallback if opengrep unavailable                       |
| `pip-audit`         | `uv tool install pip-audit`                                                    | For Python dep auditing                                |
| `bundle-audit`      | `gem install --user-install bundler-audit`                                     | Ruby                                                   |
| `govulncheck`       | `go install golang.org/x/vuln/cmd/govulncheck@latest`                          | Go; needs Go toolchain                                 |
| `bun`/`pnpm`/`yarn` | Already-present is required — don't install a JS package manager just to audit | Skip the check and note it                             |

If a tool the user uses every day is missing (e.g., they have a Go project but no Go toolchain),
don't offer to install Go — that's beyond the scope of an audit. Skip the check.

## Check A — Exposed secrets

**Before flagging a secret, ask yourself**: is this a _bundled_ secret (will reach every user of the
app) or a _committed-but-server-only_ secret (reached only by attackers with repo access)? The blast
radius is very different. A Stripe live key in `NEXT_PUBLIC_*` is **Critical** every time — it ships
to every browser. The same key in a committed `.env` that's gitignored-but-in- history is **High** —
exposed to whoever pulls history, not to every visitor.

**Run gitleaks** — it's purpose-built for this and dramatically better than hand-rolled grep because
it (a) handles git history, not just the working tree, (b) ships with 100+ validated rules for known
secret formats, (c) has an entropy heuristic for unknown secrets, and (d) knows how to redact in
output.

```bash
if command -v gitleaks >/dev/null; then
  # Working tree + uncommitted (matches files in the audit scope)
  gitleaks detect --source . --no-banner --redact -v --report-format json
  # Git history (catches "we removed it but it's still in the log")
  gitleaks detect --source . --no-banner --redact -v --log-opts="--all"
fi
```

If `gitleaks` isn't installed, apply the **install-and-continue protocol**: ask the user
`Install gitleaks with brew install gitleaks and then run secret detection? [y/N]`. On no, fall back
to the minimal grep set below — but record in the report that secret scanning was done with grep,
not gitleaks, and is best-effort.

### Fallback grep (only if gitleaks declined / unavailable)

```bash
# Public env vars holding non-public-looking values — the dangerous pattern in vibe-coded apps
grep -rE "(NEXT_PUBLIC_|VITE_|REACT_APP_|EXPO_PUBLIC_|PUBLIC_)[A-Z_]*(SECRET|KEY|TOKEN|PASSWORD|SERVICE_ROLE)" \
  --include="*.{ts,tsx,js,jsx}" --include=".env*" .

# Supabase service role key — the headline incident
grep -rE "service_role|SERVICE_ROLE_KEY" --include="*.{ts,tsx,js,jsx,py}" .

# .env committed or in history (catches the case gitleaks would also catch)
git ls-files 2>/dev/null | grep -E "^\.env($|\.)" || echo ".env not tracked"
git log --all --full-history --source -- .env .env.local .env.production 2>/dev/null | head -20
```

The fallback grep is intentionally minimal — it catches the two highest-signal vibe-coded mistakes
(`*_PUBLIC_*_SECRET` and Supabase service role) without competing with gitleaks on broader coverage.
If the user declined gitleaks, the report says so.

**Severity guide** (applies to either source — gitleaks finding or grep hit):

- Production API key (Stripe live, AWS, etc.) committed to repo or in history: **Critical**.
- Service role key in any client-bundled file (`NEXT_PUBLIC_*`, imported into a client component,
  anything in `pages/`/`app/` that isn't `'use server'` / API route): **Critical**.
- Bot token, OAuth client secret, or signing secret in a committed file: **Critical**.
- Test keys committed: **Medium** (still bad practice, lower blast radius).
- `.env` in git history but currently gitignored: **High** — secrets need rotation, gitignore alone
  doesn't help.

A `NEXT_PUBLIC_SUPABASE_ANON_KEY` is _expected_ and not a finding by itself — the anon key is meant
to be public. The finding is when the _service role_ key has been exposed, or when RLS isn't enabled
to make the anon key safe to expose (that's a category-specific check).

When reporting gitleaks output: don't dump the JSON. Group by rule (e.g., "Stripe live key, 3
findings") and list file:line for each.

## Check B — Static analysis (SAST)

Run a SAST scan if a scanner is available. Prefer [`opengrep`](https://github.com/opengrep/opengrep)
(LGPL-2.1, the OSS fork of semgrep maintained by ex-Semgrep contributors); fall back to `semgrep` CE
if opengrep isn't installed. Both accept the same ruleset shorthands. Lead with the security-focused
rulesets — `--config=auto` includes a lot of code-quality rules that aren't security findings and
dilute the report:

```bash
if command -v opengrep >/dev/null; then
  SCANNER=opengrep
elif command -v semgrep >/dev/null; then
  SCANNER=semgrep
else
  SCANNER=
fi

if [ -n "$SCANNER" ]; then
  "$SCANNER" --config=p/security-audit --config=p/owasp-top-ten --json --quiet .
  # Fallback if those rulesets fail to fetch (offline, etc.):
  # "$SCANNER" --config=auto --json --quiet . | head -200
fi
```

If neither `opengrep` nor `semgrep` is installed, apply the **install-and-continue protocol**: ask
the user `Install opengrep with `uv tool install opengrep` and then run static analysis? [y/N]`. On
yes, install and re-run the scan. On no, record in the report's "Gaps in this audit" section and
continue. Don't try to recreate a SAST scanner with grep.

If results are returned, group findings by rule and severity. Don't dump raw scanner JSON into the
report — pick the highest-severity 5–10 findings and summarize them.

## Check C — Dependency audit

Detect the lockfile and pick one tool — running `npm audit` against a non-npm lockfile produces
noise:

```bash
# Node — the lockfile picks the tool
if   [ -f bun.lock ];          then bun audit --json
elif [ -f pnpm-lock.yaml ];    then pnpm audit --json
elif [ -f yarn.lock ];         then yarn npm audit --json
elif [ -f package-lock.json ]; then npm audit --json
fi

# Python
[ -f requirements.txt ] && pip-audit -r requirements.txt --format json
[ -f pyproject.toml ] && [ ! -f requirements.txt ] && pip-audit --format json

# Ruby
[ -f Gemfile.lock ] && bundle-audit check --update

# Go
[ -f go.mod ] && govulncheck ./...
```

Report counts by severity from the audit tool's own classification. Highlight any **Critical** or
**High** with a known exploit (audit tools usually note this). Don't list every Low — just count
them.

If the detected-stack audit tool is missing (e.g., `pip-audit`, `bundle-audit`, `govulncheck`),
apply the **install-and-continue protocol** — ask the user with the canonical install command from
the table above, install on yes, skip and record on no.

For Node projects, the package manager (`bun`/`pnpm`/`yarn`/`npm`) is whatever the project already
uses; if it's missing on the user's machine, skip and note — don't offer to install a JS package
manager just to run an audit.

## Check D — Monitoring and logging

Mostly observational — most vibe-coded apps have nothing here, and "nothing here" is itself the
finding.

```bash
# Logging libraries (manifest absence is expected; suppress only that)
grep -hE '"(winston|pino|bunyan|sentry|datadog|loglevel)"' package.json 2>/dev/null
grep -hE "(sentry-sdk|loguru|structlog)" requirements.txt pyproject.toml 2>/dev/null

# Error tracking
grep -rE "Sentry\.(init|captureException)" --include="*.{ts,js,py}" . | head -5

# Auth event logging
grep -rE "log.*(login|signin|signup|auth|failed)" --include="*.{ts,js,py}" . | head -10
```

**Severity guide:**

- No error tracking _and_ the app handles user data: **Medium** — you won't find out about breaches
  until users complain.
- No logging of authentication events (logins, failures, password changes): **Medium**.
- Logging exists but logs raw request bodies / tokens / passwords: **High** — logs become a
  secondary leak vector.
- Console-only logging in production: **Low** (but worth flagging).

This check is necessarily heuristic — absence of monitoring code doesn't mean absence of monitoring
(could be at the platform layer, e.g., Vercel logs). Note this caveat in the report.
