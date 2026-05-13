# GitHub bot / App audit reference

Read when GitHub Apps or GitHub-targeted bots are detected (Probot, `@octokit/webhooks`, hand-rolled
receivers).

GitHub has two distinct integration models:

- **GitHub Apps** — installed per-org/repo, get an installation token per install, expire after ~1
  hour. Preferred model.
- **OAuth Apps** — act as a user, long-lived user token. Less granular permissions.

The threat model differs:

- GitHub Apps: installation tokens are short-lived but the App's _private key_ is the master
  credential.
- OAuth Apps: the user token IS the credential. If leaked, the attacker is that user.

## Signature verification

**Before flagging a GitHub receiver, ask yourself**: which secret is being HMAC'd? GitHub Apps have
_two_ per-App secrets — the **webhook secret** (for signature verification) and the **private key**
(.pem, for JWT signing to mint installation tokens). Using the private key for HMAC verification
doesn't work and indicates the developer doesn't understand the model.

**NEVER use the App private key for webhook HMAC verification.** They're separate credentials with
separate purposes. If `crypto.createHmac("sha256", privateKey, ...)` appears in a webhook handler,
the verification is broken (the HMAC won't match real GitHub deliveries) AND the private key is
being misused. **Severity: High** for the misuse; **Critical** if the broken check is wrapped in
try/catch that returns 200.

GitHub signs webhook payloads with HMAC-SHA256 using the per-App webhook secret. Header is
`X-Hub-Signature-256: sha256=<hex>` (the legacy `X-Hub-Signature` with SHA-1 is deprecated).

The receiver must:

1. Read raw body.
2. Read `X-Hub-Signature-256`.
3. Compute `sha256=<hmac>` and compare with `crypto.timingSafeEqual`.

Bugs:

- Using `X-Hub-Signature` (SHA-1) only. **High** — deprecated and shorter.
- `===` comparison. **High**.
- No verification at all. **Critical**.
- Wrong secret: GitHub Apps have a _webhook secret_ separate from the _App private key_; using the
  private key for HMAC won't work and may be a sign of a misunderstanding. Flag the confusion.

Probot handles all of this — verify the receiver isn't bypassed by an unguarded sibling route.

## App private key

The App private key is the keys to the kingdom for a GitHub App. It signs JWTs that are exchanged
for installation tokens.

Flag:

- Private key (`.pem` file) committed to repo. **Critical**.
- Private key in `NEXT_PUBLIC_*` or any env var prefix that ends up client-bundled. **Critical**.
- Private key logged. **Critical**.
- Private key stored as a regular DB column without KMS / envelope encryption. **Medium** for
  internal tools, **High** for multi-tenant SaaS.

## Permissions

GitHub App permissions are granular: `contents:write`, `issues:write`, `pull_requests:write`,
`actions:write`, `secrets:write`, `administration:write`, etc.

Each permission is one of `read` or `write` (and some have `admin`). Review the App manifest or
installation URL.

Flag:

- `administration:write` (org admin). **High** unless justified.
- `secrets:write` (write to org/repo secrets). **High** — secrets writes are also visible to the
  App.
- `contents:write` AND the App auto-merges or auto-commits without human approval. **Medium** —
  auto-write-to-main is a category of risk.
- `actions:write` (modify workflows). **High** — workflow modification can exfiltrate secrets.

A bot that only comments on PRs needs `pull_requests:write` + `issues:write`. Anything more should
be justified.

## Installation token handling

Installation tokens are short-lived (~1h) — refresh logic must be present. Patterns to flag:

- Installation tokens cached without expiry tracking → first request after expiry fails. **Low**
  (correctness, not security, but flag).
- Installation tokens written to a database column in plain text. **Medium** (they're short-lived so
  blast radius is bounded, but they enable impersonation while alive).
- Token refresh on EVERY request (re-signs the JWT, re-requests the token, every time): wastes rate
  limit but isn't a security issue.

## OAuth Apps — user tokens

If the integration is an OAuth App (not a GitHub App), user tokens are the credentials:

- They have the user's full visibility (depending on scopes).
- They don't expire unless revoked.

Flag:

- User tokens stored alongside other user data with no encryption. **High**.
- OAuth scopes broader than the integration needs (`repo` for a bot that only reads issues).
  **High**.

## Webhook event handling

Inside webhook handlers, treat all payload data as untrusted:

- `sender.login` is the username that triggered the event — fine for display, but if used in
  authorization decisions, attackers can change their GitHub username and re-trigger.
- `pull_request.title`, `issue.body`, `comment.body` are user-supplied text. If the bot pipes these
  to an LLM with tool access, that's an indirect prompt-injection vector.
- `head.ref` (branch name) is attacker-controlled in PRs from forks. Don't shell-out with it.

Flag:

- PR/issue body content rendered in HTML emails sent by the bot without escaping. **Medium**
  (cross-site scripting in the email client; depends on client).
- PR title interpolated into a shell command (e.g., `git commit -m "$title"`). **Critical** (RCE).
- Authorization based on mutable fields (`sender.login` rather than `sender.id`). **High**.
