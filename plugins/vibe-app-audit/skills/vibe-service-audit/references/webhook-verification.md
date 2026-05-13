# Webhook signature verification reference

Read this when the service has any webhook receiver. Covers section 1 of the service audit.

The headline failure mode: **the receiver reads `req.body` and acts on it without verifying that the
request came from the expected sender.** Any HTTPS endpoint on the public internet can be called by
anyone; the signature is what proves the caller is who they say they are.

## Before flagging — the meta-NEVER

**NEVER catch a signature-verification error silently and return 200.** This is the worst possible
state: the sender keeps delivering (no failures from their side), no monitoring fires, and the
attacker's forged requests are processed. A handler that explicitly throws on verification failure
and lets the framework return 4xx is _better_ than one that catches and returns 2xx.

Look for this pattern specifically:

```ts
try {
    verifySignature(req); // throws if bad
    handleEvent(req.body);
} catch (e) {
    res.status(200).send("ok"); // BUG: hides the failure
}
```

Severity: **Critical** — the endpoint is functionally unauthenticated, but appears to "work."

## Step 1 — Find every webhook endpoint

```bash
# Route handlers commonly named "webhook"
find . -path ./node_modules -prune -o \
  \( -path "*/webhook*" -o -name "*webhook*.{ts,js,py,rb}" \) -print | head -20

# Endpoints that read raw bodies (signature verification needs the raw body, not parsed JSON)
grep -rE "(req\.rawBody|getRawBody|express\.raw|bodyParser\.raw|request\.body\.decode)" \
  --include="*.{ts,js,py}" . | head -20

# Direct handlers for the well-known platforms
grep -rlE "(stripe-signature|x-hub-signature|x-shopify-hmac|x-slack-signature|x-square-hmacsha256|x-zoom-signature)" \
  --include="*.{ts,js,py}" . | head -20
```

For each endpoint found, open it and verify:

1. **The signature header is read** (`req.headers['stripe-signature']` or equivalent).
2. **The raw body is used for HMAC** (not the JSON-parsed body — once it's parsed, key order may
   change and the HMAC won't match).
3. **The comparison is constant-time** (`crypto.timingSafeEqual`, `hmac.compare_digest`,
   `subtle.timingSafeEqual`).
4. **The timestamp is checked** (replay window).
5. **Verification happens BEFORE any side effect** (database write, outbound call, etc.).

## Step 2 — Platform-specific patterns

### Stripe

Verify with the Stripe SDK:

```ts
const event = stripe.webhooks.constructEvent(rawBody, sig, endpointSecret);
```

Flag: hand-rolled Stripe HMAC; missing `endpointSecret`; the SDK call wrapped in `try/catch` that
silently continues on failure.

### GitHub

Header: `X-Hub-Signature-256: sha256=<hmac>`. Body: raw.

```ts
const expected = "sha256=" + crypto.createHmac("sha256", secret).update(rawBody).digest("hex");
if (!crypto.timingSafeEqual(Buffer.from(sig), Buffer.from(expected))) throw new Error("bad sig");
```

Flag: using SHA-1 (`X-Hub-Signature` without `-256`) — deprecated; using `===` instead of
`timingSafeEqual`.

### Shopify

Header: `X-Shopify-Hmac-Sha256`, base64-encoded. Body: raw.

### Square

Header: `x-square-hmacsha256-signature`. Body is HMAC'd along with the _request URL_ — easy to get
wrong if a proxy rewrites the URL.

### Twilio

Header: `X-Twilio-Signature`. The signed string includes the URL + sorted POST body params, not the
raw body. Use `twilio.validateRequest` from the SDK.

### Slack

Slack is covered in the `vibe-bot-audit` skill's `references/slack.md`, not here. If this is a Slack
bot, switch to that skill.

### Custom / internal webhooks

If the service implements its own webhook framing (e.g., calls itself with HMAC), the signed
material should include:

- The HTTP method.
- The full path.
- A timestamp (with a check window on receive).
- The raw body.

Anything less leaves replay or substitution attacks.

## Step 3 — Common bugs

**Bug 1 — parsing the body before verifying.** If the framework parses JSON before the handler runs,
the HMAC won't match because the parser may reorder keys, normalize whitespace, etc. Fix: configure
the route to receive raw bytes (Express: `bodyParser.raw({type: 'application/json'})`; FastAPI: read
`await request.body()` before doing anything else).

**Bug 2 — constant-time comparison missing.** `==` and `===` short-circuit on the first mismatch and
leak the position of the first wrong byte via timing. Use `crypto.timingSafeEqual`,
`hmac.compare_digest`, or platform equivalents.

**Bug 3 — verification wrapped in try/catch that returns 200.** A handler that catches the
verification error and returns 200 OK is worse than no verification — the sender keeps delivering,
no monitoring fires, and the attacker is in.

**Bug 4 — replay accepted.** Without a timestamp check, an attacker who captures one valid signed
request can replay it forever. Most platforms include a timestamp in the signed material; the
handler must check that it's recent (e.g., within 5 minutes) and ideally that it hasn't been seen
before (idempotency key on the event ID).

**Bug 5 — wrong secret used.** Webhook secrets are per-endpoint; using the API key instead is a
common mistake. Verify the secret variable name matches the platform's docs (e.g., Stripe's
`STRIPE_WEBHOOK_SECRET`, not `STRIPE_SECRET_KEY`).

## What to put in the report

One finding per endpoint with a verification bug. If three endpoints share the same custom verifier
with the same bug, group them: "Three webhook handlers (`stripe.ts`, `shopify.ts`, `github.ts`) all
use `===` to compare HMACs."
