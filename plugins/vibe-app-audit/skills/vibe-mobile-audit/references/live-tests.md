# Mobile live tests

Read after `$SHARED_DIR/references/live-tests-baseline.md`.

Mobile live targets are different from web — there isn't a single endpoint to probe. The two
practical things to exercise:

1. **The backend API the app talks to** — probes mirror `vibe-service-audit` against the API base
   URL.
2. **The built artifact** — if the user provides an IPA / APK, extract it and inspect the bundle for
   embedded secrets and config.

Dynamic / on-device probes (running the app under Frida, simulator-based cert pinning bypass,
runtime traffic interception) are out of scope — the user would need a device farm and platform
expertise. Record them as gaps if relevant.

## Setup

```bash
# Inputs from the user:
BACKEND_URL=""   # e.g., https://api.example.com — for API probes
ARTIFACT=""      # e.g., /path/to/app.ipa or app.apk — for bundle inspection

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT
```

## Safe probes (run by default)

### S1 — Backend API: unauthenticated request

If `$BACKEND_URL` is set:

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" "$BACKEND_URL/<endpoint>"
```

For each known API endpoint (extract from the app's source: search for fetch / axios calls), send an
anonymous request. **Expected:** 401 / 403. **Failure verdict (Critical):** 200 with user data.

### S2 — Backend API: malformed body

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" -X POST "$BACKEND_URL/<endpoint>" \
  -H "Content-Type: application/json" \
  -d '{'
head -c 500 /tmp/resp
```

**Expected:** 400, clean. **Failure verdict (High):** 500 with stack trace.

### S3 — Backend API: signature / token spoofing

If the app uses a Bearer token, try an obviously-invalid one:

```bash
curl -s -o /tmp/resp -w "%{http_code}\n" "$BACKEND_URL/<authed-endpoint>" \
  -H "Authorization: Bearer invalid-token-12345"
```

**Expected:** 401. **Failure verdict (Critical):** 200 (token not actually checked).

### S4 — IPA inspection (if `$ARTIFACT` is an `.ipa`)

```bash
unzip -q "$ARTIFACT" -d "$TMPDIR/ipa"
ls "$TMPDIR/ipa/Payload/"  # find <App>.app bundle

APP_DIR=$(ls -d "$TMPDIR/ipa/Payload/"*.app | head -1)

# Read Info.plist (binary plist; use plutil)
plutil -convert xml1 -o - "$APP_DIR/Info.plist" | head -200

# Look for embedded credentials in the executable + JS bundles
strings "$APP_DIR/$(basename "$APP_DIR" .app)" | \
  grep -iE "(sk_live_|sk_test_|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|xox[baprs]-)" | head -10

# JS bundle for React Native / Expo apps
find "$APP_DIR" -name "main.jsbundle" -o -name "*.hbc" -o -name "*.bundle" | head -5
for bundle in $(find "$APP_DIR" -name "main.jsbundle"); do
  strings "$bundle" | grep -iE "(secret|key|token|password)" | head -20
done
```

**Expected:** no production secrets in the bundle. **Failure verdict (Critical):** real secret
values found in the binary or JS bundle.

Also inspect:

- `Info.plist` — `NSAllowsArbitraryLoads`, declared URL schemes, usage descriptions match what the
  app actually does.
- `embedded.mobileprovision` — is this signed with a production cert? Distribution type?
- Frameworks bundled in `Frameworks/` — any unexpected ones (analytics SDKs the user didn't intend,
  fingerprinting libraries)?

### S5 — APK inspection (if `$ARTIFACT` is an `.apk`)

```bash
unzip -q "$ARTIFACT" -d "$TMPDIR/apk"

# Manifest — binary XML, needs aapt to decode
# If aapt isn't installed, fall back to strings on the binary manifest
if command -v aapt2 >/dev/null; then
  aapt2 dump xmltree "$ARTIFACT" --file AndroidManifest.xml | head -200
else
  echo "aapt2 not installed — falling back to strings on binary manifest"
  strings "$TMPDIR/apk/AndroidManifest.xml" | head -100
fi

# Resources
ls "$TMPDIR/apk/res/xml" 2>/dev/null

# Native libraries
ls "$TMPDIR/apk/lib" 2>/dev/null

# DEX files — for embedded strings
strings "$TMPDIR/apk/classes.dex" | grep -iE "(sk_live_|sk_test_|AKIA[0-9A-Z]{16}|api[._]?key)" | head -10

# React Native JS bundle
find "$TMPDIR/apk" -name "index.android.bundle" -o -name "*.hbc" | head -5
```

**Expected:** no production secrets in the DEX, no secrets in the JS bundle. **Failure verdict
(Critical):** secrets found.

If `aapt2` is missing, apply the **install-and-continue protocol**: `aapt2` ships with Android SDK
build-tools and isn't easily installed on its own — skip the manifest decode and proceed with
`strings`-based inspection. Don't offer to install the Android SDK as part of the audit.

## Intrusive probes (consent required)

### I1 — Backend API: IDOR / authorization (with user-supplied test credentials)

If the user provides two test accounts' tokens:

- Token A requests resources `/users/<A-id>` — expect 200.
- Token A requests `/users/<B-id>` — expect 403/404.

**Consent prompt**: "Run IDOR probes against the backend with the two test tokens you provided?
Read-only. Proceed? [y/N]"

### I2 — Deep link probe (manual, requires device)

The skill can't trigger a deep link on a device, but it can:

- Construct a malicious-shaped URL based on the schemes / paths it found in the manifest.
- Print the URL and instructions: "Run `xcrun simctl openurl booted '<url>'` on iOS Simulator, or
  `adb shell am start -a android.intent.action.VIEW -d '<url>'` on Android, and report what the app
  does."

This is observational, not automated. Record as `inconclusive — user verification required` unless
the user confirms behavior.

## What to record

Same evidence shape as the baseline. For bundle-inspection findings, the "request" is the unzip
command + the file inspected; the "response" is the matched content (redact secrets — do not echo
the full secret value in the report; show prefix + length).

Cleanup: the `trap 'rm -rf "$TMPDIR"' EXIT` handles bundle extraction. Confirm the tmpdir is gone
before writing the report.

In "What's next" — if the backend wasn't audited as its own target, recommend running
`vibe-service-audit` against it. The mobile audit catches client-side issues; the backend has its
own full surface to review.
