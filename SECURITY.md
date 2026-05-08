# Security policy

Fencer takes security seriously. If you believe you've found a vulnerability in this marketplace —
its skills, scripts, plugin manifests, CI workflows, or anything else in this repository — please
report it privately so we can fix it before disclosure.

## Reporting a vulnerability

Email **security@fencer.dev** with:

- A description of the issue and where it lives in the repo (file path, line number, or skill name).
- A minimal reproduction or proof-of-concept if you have one.
- Your assessment of impact (what an attacker could do).
- Any suggested fix, if you have one.

We'll acknowledge your report within **two business days**. We aim to confirm or refute the issue
within **seven days**, ship a fix within **30 days** for material issues, and credit you in the
release notes if you'd like.

**Do not open a public GitHub issue for vulnerabilities.** Public issues are for non-security bugs
and feature requests.

## What's in scope

- Skills, scripts, and plugin manifests in this repository that an installed user would execute. The
  most material concern is a skill that a malicious contributor could use to exfiltrate data,
  execute attacker-controlled code, or escalate privileges on the user's machine.
- The `.github/workflows/` configuration — workflow permission misuse, secret exposure, supply-chain
  risks via third-party actions.
- The `scripts/` repo-level tooling.

## What's out of scope

- Findings inside reports _produced by_ a skill (e.g., a SOC 2 review's recommendations, a vibe-app
  audit's severity calls). Those are skill output, not security defects in this repo. If you think a
  skill produces wrong or misleading guidance, open a regular GitHub issue.
- Vulnerabilities in upstream tools the skills shell out to (`semgrep`, `opengrep`, `pip-audit`,
  etc.). Report those to the upstream projects.
- Issues in the Fencer product itself (the platform at https://fencer.dev) — those go to the Fencer
  security team via the same email but are tracked separately from this repo.

## Disclosure

We follow coordinated disclosure. Once a fix is ready, we'll release it, publish a security advisory
on this repository, and credit the reporter unless you ask us not to. We won't disclose details
before a fix ships.
