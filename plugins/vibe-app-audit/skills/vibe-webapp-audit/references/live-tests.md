# Webapp live tests

Read after `$SHARED_DIR/references/live-tests-baseline.md`. The baseline defines the protocol
(target acquisition, safe vs intrusive, production guard, evidence shape, cleanup); this file
defines the webapp-specific probes.

The live target is a deployed URL: `https://app.example.com`. Apply the production guard before any
probe.

## Safe probes (run by default)

### S1 — Security header probe

```bash
curl -sI "$TARGET" | grep -iE \
  "content-security-policy|x-frame-options|x-content-type-options|strict-transport-security|referrer-policy|permissions-policy"
```

Score what's missing. **Severity:**

- Missing `Strict-Transport-Security` on an HTTPS production site: **Medium**.
- Missing `Content-Security-Policy`: **Medium**.
- Missing `X-Frame-Options` (or CSP `frame-ancestors`) on a site that handles auth: **High**
  (clickjacking risk).
- Missing `X-Content-Type-Options: nosniff`: **Low**.
- Missing `Referrer-Policy`: **Low**.

### S2 — Anonymous Supabase reads

Only if Supabase is in the stack and the anon key is present in client code:

```bash
# Extract anon key and project URL from .env or client code, then:
curl -s "https://<project>.supabase.co/rest/v1/<table>?select=*&limit=5" \
  -H "apikey: <ANON_KEY>" \
  -H "Authorization: Bearer <ANON_KEY>"
```

For each table you find in migration files or referenced in client code, hit it as anon. Expected
healthy behavior: `401`/`403`, or `200` with `[]` (RLS denies the rows). Unhealthy: `200` with
actual rows.

**Severity:** Any row returned for a user-data table (users, orders, messages, etc.) by an anonymous
request is **Critical**. Reference/public data tables (catalogs, plans) returning rows is expected —
note as Info.

### S3 — Auth-required endpoint, anonymous request

For each route handler that should require auth (anything under `/api/` that mutates state or
returns user data), send an anonymous GET/POST and confirm `401`/`403`. A `200` with data is a
critical authorization gap.

```bash
curl -s -o /dev/null -w "%{http_code}\n" "$TARGET/api/<endpoint>"
curl -s -X POST -o /dev/null -w "%{http_code}\n" "$TARGET/api/<endpoint>" -d '{}'
```

**Severity:** Anonymous access to a user-data endpoint: **Critical**. Anonymous access to a write
endpoint: **Critical**.

### S4 — Error page introspection

Trigger errors and inspect responses for stack traces, secret leakage, and framework internals:

```bash
# Missing route
curl -s "$TARGET/this-route-does-not-exist-$(date +%s)" | head -100

# Malformed query
curl -s "$TARGET/api/<endpoint>?id=not-a-uuid" | head -100

# Malformed JSON to a known endpoint
curl -s -X POST "$TARGET/api/<endpoint>" -H "Content-Type: application/json" -d '{' | head -100
```

**Severity:**

- Stack trace returned in 5xx response body: **High** (leaks framework version + file paths).
- Secret value (DB connection string, API key) visible in any error page: **Critical**.
- Sentry DSN or other telemetry credentials visible in client error: **Medium**.

### S5 — Mixed-content / HSTS behavior

```bash
# HTTP → HTTPS redirect
curl -sI "http://${TARGET#https://}" | grep -iE "^(HTTP|Location|Strict-Transport)"
```

**Severity:** HTTPS site with no HTTP→HTTPS redirect: **Medium**.

## Intrusive probes (consent required before each batch)

For each of the following, ask explicitly: name the probe, what it does, what side effects are
possible. Default no.

### I1 — IDOR enumeration

If the app exposes resources by ID (UUIDs, slugs, numeric IDs), and the user can provide two test
accounts:

- Sign in as user A, request `/api/orders/<A's-order-id>` — expect 200.
- Sign in as user B, request `/api/orders/<A's-order-id>` — expect 403/404.

If user B gets 200 with A's data: **Critical**.

For numeric IDs, try off-by-one neighbors of a known ID. For UUIDs, you need an actual ID from
another account — don't fuzz random UUIDs.

**Consent prompt**: "Run IDOR enumeration? Sends GET requests with another account's resource IDs as
user B. Read-only, but exercises the app's data path. Proceed? [y/N]"

### I2 — Reflected XSS probe

For each form input and query parameter that ends up rendered:

```bash
curl -s "$TARGET/<path>?q=<script>alert(1)</script>" | grep -c "<script>alert(1)</script>"
```

A non-zero count is a reflected XSS finding: **High**.

**Consent prompt**: "Run reflected-XSS probes? Sends `<script>` payloads to query parameters and
form endpoints. No state changes. Proceed? [y/N]"

### I3 — Basic SQL-injection probe

For each form input that reaches a query, send `' OR 1=1 --` and a boolean-blind variant. Look for:
500 with SQL error in the response, or a response that differs between `' OR 1=1 --` and
`' OR 1=2 --`.

**Severity:** SQL error in response: **High** (information disclosure). Boolean-blind difference
detected: **Critical**.

**Consent prompt**: "Run SQL-injection probes? Sends `' OR 1=1 --` and variants to form inputs.
Mostly read-only but may cause 500s in logs. Proceed? [y/N]"

## What to record

For each probe, follow the evidence shape from the live-tests baseline:

- **Probe**: short name (e.g., "S2 anon read on `orders`").
- **Request**: method, URL, headers (one line), body excerpt.
- **Response**: status, key headers, body excerpt (≤200 chars, PII redacted).
- **Verdict**: pass / fail / inconclusive.

Failed probes promote to severity sections; passed probes stay in the live-tests table.
