# Script live tests

Read after `$SHARED_DIR/references/live-tests-baseline.md`.

Live target: a safe invocation command provided by the user. All probes run in an isolated
`mktemp -d` working directory; the script must never be exercised against real data.

## Setup

```bash
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
cd "$TMPDIR"
# Copy the script and any required config; create fixture data inside $TMPDIR only.
```

Record the tmpdir path in the report and confirm cleanup at the end.

## Safe probes (run by default)

### S1 — Smoke

```bash
$SCRIPT --help
$SCRIPT --version 2>/dev/null
```

**Expected:** exits 0 with usage / version output. No side effects. **Failure verdict (Low):**
crashes; missing `--help` is a UX issue (note but don't promote).

### S2 — Path-traversal argument

If the script takes a file path argument, send `../../etc/passwd`:

```bash
$SCRIPT --input ../../etc/passwd 2>&1 | head -50
```

**Expected:** rejects with an error message about the path, OR resolves to a path inside the
intended directory and then fails to find / read it. **Failure verdict (High):** reads `/etc/passwd`
and acts on its contents.

### S3 — Shell-metachar argument

If the script takes any string argument that might end up in a shell:

```bash
$SCRIPT --name '; touch /tmp/owned-$$' 2>&1
ls /tmp/owned-* 2>/dev/null && echo "INJECTION SUCCEEDED"
```

**Expected:** no `/tmp/owned-*` file created. **Failure verdict (Critical):** the touch ran —
command injection confirmed.

### S4 — World-readable credfile

If the script reads a credfile, create one with permissive permissions:

```bash
echo "fake-secret" > "$TMPDIR/cred"
chmod 644 "$TMPDIR/cred"
$SCRIPT --cred "$TMPDIR/cred" 2>&1 | head -20
```

**Expected:** the script refuses or warns about permissive permissions. **Failure verdict (Low):**
reads silently. Defense-in-depth, not a vulnerability.

### S5 — Missing credfile

```bash
$SCRIPT --cred "$TMPDIR/does-not-exist" 2>&1 | head -20
echo "exit code: $?"
```

**Expected:** exits non-zero with a clear error. **Failure verdict (High):** exits 0 (script
proceeded without credentials, possibly using something insecure as a fallback).

### S6 — Malformed config

If the script reads YAML/JSON/TOML config, give it an invalid one:

```bash
echo '{invalid json' > "$TMPDIR/config.json"
$SCRIPT --config "$TMPDIR/config.json" 2>&1 | head -20
```

**Expected:** clean parse error. **Failure verdict (Medium):** stack trace exposing internals.

## Intrusive probes (consent required)

### I1 — Main-path execution against fixture data

Set up fixture data inside `$TMPDIR` (a fake database, a fake API URL pointing at a local mock, fake
input files). Run the script's main action.

**Consent prompt**: "Run the script's main action against fixture data in `$TMPDIR`? This will
exercise the destructive code path against test data. Proceed? [y/N]"

Observe: does it produce expected output? Does it write somewhere outside `$TMPDIR`? Does it hit
external URLs?

### I2 — Idempotency

Run the main action twice in a row against the same fixture data.

**Expected:** the second run either no-ops cleanly or produces a clean "already done" message.
**Failure verdict (Medium):** the second run produces duplicates or crashes.

**Consent prompt**: "Run the script twice in a row to check idempotency? Proceed? [y/N]"

### I3 — Concurrent run

Run the main action twice in parallel against the same fixture data.

**Expected:** one succeeds, the other waits or fails cleanly with a lock-already-held message.
**Failure verdict (High):** both proceed and corrupt the fixture data (no locking).

**Consent prompt**: "Run two concurrent instances against fixture data? Tests for locking issues.
Proceed? [y/N]"

## What to record

Same evidence shape as the baseline. For each probe: invocation, exit code, stdout/stderr excerpt,
any files created (verify they're inside `$TMPDIR`), verdict.

Cleanup: the `trap 'rm -rf "$TMPDIR"' EXIT` should handle everything. The report's cleanup section
names the tmpdir and confirms it's gone. If the script wrote outside `$TMPDIR` unexpectedly, name
those files in the report and tell the user.
