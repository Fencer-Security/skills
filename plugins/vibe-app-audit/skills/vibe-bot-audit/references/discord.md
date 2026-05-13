# Discord bot audit reference

Read when Discord is detected. Discord's signature scheme differs meaningfully from Slack / GitHub:
it uses **ed25519** asymmetric signatures, not HMAC.

## Signature verification — ed25519

**Before flagging a Discord receiver, ask yourself**: did someone implement signature verification
from memory? Discord is the _only_ major platform that signs with ed25519 (asymmetric) instead of
HMAC (symmetric). Code that does `crypto.createHmac(...)` for Discord verification is wrong by
construction — the signature will never validate, so the developer usually disables the check,
leaving the endpoint open.

**NEVER use HMAC for Discord interaction verification — Discord uses ed25519.** If you see
`crypto.createHmac` or `hmac.new` near a Discord handler, that's a critical misimplementation, even
if it appears to "work" because the check is bypassed.

For HTTP interactions (slash commands, components), Discord signs each request with the bot's
ed25519 private key. The receiver must:

1. Read the raw body.
2. Read `X-Signature-Ed25519` and `X-Signature-Timestamp`.
3. Look up the **application public key** (set in the Discord dev portal).
4. Verify `ed25519(timestamp || rawBody)` against the signature with the public key.
5. Reject if the timestamp is too old (Discord doesn't enforce a window — your handler should).

The public key is per-application and not secret. It IS, however, the only thing standing between
your endpoint and arbitrary unauthenticated POSTs.

If using `discord.js` for HTTP interactions, use the official `verifyKey` from
`discord-interactions` — verify it's called BEFORE the body is acted on.

Bugs to flag:

- No verification at all. **Critical**.
- Verification uses HMAC instead of ed25519 (someone implemented it from memory). **Critical**.
- `verifyKey` called but its return value isn't checked. **Critical**.
- No timestamp freshness check. **High**.
- Hardcoded public key that doesn't match the app's actual key (probably leftover from a tutorial).
  **Critical**.

Note: WebSocket-gateway bots (using `discord.js` with `Client` + `login(token)`) don't deal with
inbound HTTP — they pull events from Discord's gateway. Signature verification doesn't apply. But
the bot token is the only secret protecting the gateway connection — see token storage.

## OAuth scopes / permissions

Discord uses a bitfield "permissions integer" baked into the install URL. Common over-broad bits:

| Permission       | Value     | Notes                                                   |
| ---------------- | --------- | ------------------------------------------------------- |
| ADMINISTRATOR    | 8         | Bypasses all permission checks — **High** if requested. |
| MANAGE_GUILD     | 32        | Server settings, including audit log access.            |
| MANAGE_ROLES     | 268435456 | Can self-promote if hierarchy allows.                   |
| MANAGE_CHANNELS  | 16        | Create/delete channels.                                 |
| MANAGE_WEBHOOKS  | 536870912 | Can create webhooks the attacker keeps after eviction.  |
| MENTION_EVERYONE | 131072    | Annoying-vector but not security.                       |

A bot that only replies in slash commands needs `applications.commands` and `SEND_MESSAGES` (2048).
Anything more should be justified.

Flag: a permissions integer with ADMINISTRATOR (8) bit set, when the bot's docs don't justify it.
**High**.

## Bot tokens

Discord bot tokens are long-lived and have format `<base64>.<base64>.<base64>`. They're
extraordinarily sensitive — anyone with the token can impersonate the bot.

Flag:

- Bot token committed to repo. **Critical**.
- Bot token in `NEXT_PUBLIC_*` or any client-bundled env var. **Critical**.
- Bot token logged on bot startup. **High**.

## Command handling

Slash command interactions include:

- `member.user.id`, `member.user.username`, `guild_id`, `channel_id`: set by Discord, trustworthy
  (after signature verification).
- Command options (the typed-in args): UNTRUSTED.

Patterns to flag:

- Command options interpolated into shell / SQL / file paths. **Critical**.
- Authorization decisions based on `username` (mutable) instead of `user.id`. **High**.
- Bot impersonating a user via `member.user.id` lookup that returns sensitive data. Verify the data
  isn't leaked back to the channel.

## Message-content intent

If the bot reads message content (not just slash commands), it needs the `MESSAGE_CONTENT` gateway
intent — a privileged intent. Bots over 100 guilds need verification + approval.

This isn't directly a security issue but is worth noting: a vibe-coded bot scraping message content
is a privacy concern. The audit should call this out in the report if the bot uses `MESSAGE_CONTENT`
and forwards content to third parties or LLMs.
