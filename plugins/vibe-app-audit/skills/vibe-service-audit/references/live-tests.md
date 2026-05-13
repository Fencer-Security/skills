# Service live tests

Read after `$SHARED_DIR/references/live-tests-baseline.md`.

Live target: webhook URL or API base URL. Apply the production guard.

## Safe probes (run by default)

### S1 — Unsigned payload

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" -X POST "$TARGET" \
  -H "Content-Type: application/json" \
  -d '{"test":"unsigned"}'
```

**Expected:** 401 or 403, with no echoed input. **Failure verdict (Critical):** 200 OK, or 2xx with
the input echoed/acted on.

### S2 — Tampered signature

Send a payload with a clearly-wrong signature header (use a placeholder value for whatever the
platform expects: `Stripe-Signature: t=0,v1=00`, `X-Hub-Signature-256: sha256=00`, etc.):

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" -X POST "$TARGET" \
  -H "Content-Type: application/json" \
  -H "<platform-signature-header>: <obviously-invalid>" \
  -d '{"test":"tampered"}'
```

**Expected:** 401 or 403. **Failure verdict (Critical):** 200 OK.

### S3 — Replay (if the user has a valid signed payload from a previous delivery)

Re-send a previously-valid signed payload (same signature, same body, original timestamp):

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" -X POST "$TARGET" \
  -H "Content-Type: application/json" \
  -H "<signature-header>: <valid-signature>" \
  -H "<timestamp-header>: <original-timestamp>" \
  --data-binary @valid-body.json
```

**Expected:** 401/403 (rejected on timestamp window) OR 200 with no duplicate side effect
(idempotency). **Failure verdict (High):** 200 OK with a duplicate side effect observed (charge,
email, row).

If the user can't provide a valid signed payload to replay, skip and record as "S3 inconclusive: no
valid signed payload available."

### S4 — Malformed JSON

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" -X POST "$TARGET" \
  -H "Content-Type: application/json" \
  -d '{'
head -c 500 /tmp/resp
```

**Expected:** 400 with a clean error. **Failure verdict (High):** 500 with a stack trace in the
response body.

### S5 — Verb mismatch

Hit a POST endpoint with GET, a GET endpoint with POST:

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" -X GET "$TARGET"
```

**Expected:** 405 Method Not Allowed. **Failure verdict (Medium):** 200 — handler doesn't gate on
method, may behave unexpectedly.

### S6 — Content-Type mismatch

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" -X POST "$TARGET" \
  -H "Content-Type: text/plain" \
  -d 'not json'
```

**Expected:** 4xx. **Failure verdict (Medium):** 500 with stack trace; or 2xx — handler accepts
wrong content type.

## Intrusive probes (consent required before each batch)

### I1 — Adversarial signed body

If the user has provided a valid signing secret AND consented:

- Oversized field (`"name": "<10MB of x>"`) → expected: bounded handling, not OOM.
- Deeply nested JSON (1000-level nesting) → expected: parser rejects or service handles.
- Unicode edge cases (RTL override, zero-width, normalization-sensitive strings) in user-data fields
  → expected: stored as-is or rejected cleanly, no crash.

**Consent prompt**: "Run adversarial-body probes with a valid signature? Sends large/nested/
unicode-heavy payloads to test parser limits. May trigger 500s. Proceed? [y/N]"

### I2 — Rate-limit probe

Send N (e.g., 100) signed requests in a tight loop and observe response codes. Expected: the service
rate-limits or backpressures; failures should be 429s, not 500s.

**Consent prompt**: "Run rate-limit probe? Sends 100 requests in 10 seconds. Will appear in your
logs and may trigger alerts. Proceed? [y/N]"

## What to record

Follow the evidence shape from the baseline. For each probe: request, response status + key
headers + body excerpt (≤200 chars, redact secrets/PII), verdict.

Cleanup: replay tests against an idempotent endpoint shouldn't leave state, but if the test caused a
charge / email / row-write, name it in the cleanup section of the report.
