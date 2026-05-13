# Android audit reference

Read when an Android project (Kotlin / Java) or an Android sub-project of a React Native / Expo app
is detected.

## Step 1 — Map the project

```bash
find . -maxdepth 5 -name "AndroidManifest.xml" | grep -v build | head -10
find . -maxdepth 4 -name "build.gradle" -o -name "build.gradle.kts" | head -10
find . -maxdepth 5 -name "network_security_config.xml" | head -5
```

For React Native, the manifest is at `android/app/src/main/AndroidManifest.xml`. For pure Android
projects, it's at `app/src/main/AndroidManifest.xml`.

## Step 2 — Secret storage

Modern Android: use `EncryptedSharedPreferences` (from the Jetpack Security library) or `Keystore`
directly. Plain `SharedPreferences` writes to a world-readable-within-app-UID file — fine if no one
else can read it, but old Android, rooted devices, and backup files defeat this.

```bash
grep -rE "(SharedPreferences|getDefaultSharedPreferences|getSharedPreferences)" \
  --include="*.{kt,java}" .

grep -rE "(EncryptedSharedPreferences|MasterKey|KeyGenParameterSpec)" \
  --include="*.{kt,java}" .
```

Severity:

- Auth token in plain `SharedPreferences`: **High**.
- API key in plain `SharedPreferences`: **Medium**.
- Sensitive data in `EncryptedSharedPreferences` with `MasterKey` properly configured: OK.
- KeyStore usage but the key is unprotected (`setUserAuthenticationRequired(false)`): OK for
  background work; flag if it's used for high-value operations (banking, payments).

## Step 3 — Network security config

API 28+ requires HTTPS by default. Cleartext exceptions go in `res/xml/network_security_config.xml`:

```xml
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">api.example.com</domain>
    </domain-config>
</network-security-config>
```

Read the file:

```bash
cat android/app/src/main/res/xml/network_security_config.xml 2>/dev/null
```

Severity:

- `cleartextTrafficPermitted="true"` in `<base-config>` (global): **High** in production.
- Cleartext domain-config for a third-party that doesn't support TLS: **Low**, but verify the domain
  doesn't carry sensitive data.
- No `network_security_config.xml` referenced AND `usesCleartextTraffic="true"` in `<application>`:
  **High**.
- No `network_security_config.xml` AND no `usesCleartextTraffic` attribute: relies on defaults — OK
  on API 28+ (cleartext blocked by default).

## Step 4 — Manifest review

Read `AndroidManifest.xml` fully. Key things:

### `allowBackup`

```xml
<application android:allowBackup="true" ...>
```

- `true` (default on older SDKs): app data is included in cloud backup. Combined with secrets in
  `SharedPreferences`, this exposes them to anyone with the backup.
- For an app handling auth tokens / PII, set to `false` or define a `<full-backup-content>` /
  `<data-extraction-rules>` that excludes the sensitive data.

Severity: **Medium** if `allowBackup="true"` AND there's any sensitive data in app-private storage.

### Exported components

For each `<activity>`, `<service>`, `<receiver>`, `<provider>`:

- `android:exported="true"` (or implicit-true with an intent filter) means another app can invoke
  it.
- API 31+ requires `android:exported` to be set explicitly.

For each exported component, check the handler:

- Does it perform a state-changing action? Reads parameters from the Intent? **High** if it doesn't
  verify the caller's identity (`getCallingPackage()`, signature check).
- Is it a deep-link entry? Same concerns as iOS deep links — flag a handler that signs the user in
  or performs destructive actions based on intent extras. **Critical** for auth bypass.

### Permissions

```bash
grep -A1 "<uses-permission" android/app/src/main/AndroidManifest.xml
```

Flag:

- `QUERY_ALL_PACKAGES` without justification (Play Store policy concern + privacy). **Medium**.
- `SYSTEM_ALERT_WINDOW` (draw over other apps) for a non-overlay app. **Medium**.
- `WRITE_EXTERNAL_STORAGE` on API 30+ (deprecated; should use scoped storage). **Low**.
- `READ_PHONE_STATE` / `READ_PHONE_NUMBERS` for an app that doesn't need them. **Medium**.
- Any permission with no obvious code-path usage. **Low** (note as cleanup, not a vuln).

## Step 5 — Intent filters and deep links

```bash
grep -B2 -A15 "<intent-filter" android/app/src/main/AndroidManifest.xml | head -50
```

For each intent filter:

- `<action android:name="android.intent.action.VIEW">` + `<data>` defines a deep link.
- Without `android:autoVerify="true"` on App Links, any app can register the same scheme/host.

Find the handler:

```bash
grep -rE "(getIntent\(\)|onNewIntent|Linking\.|expo-linking)" --include="*.{kt,java,ts,tsx,js,jsx}" . | head -20
```

For each handler, apply the same severity rubric as iOS URL handlers — auth tokens in the intent
data are **Critical**, destructive actions without re-auth are **High**.

## Step 6 — WebView

```bash
grep -rE "(WebView|addJavascriptInterface|setJavaScriptEnabled|loadUrl)" \
  --include="*.{kt,java}" .
```

Flag:

- `addJavascriptInterface` exposing a class to JS, AND the WebView loads anything other than
  packaged app HTML. **Critical** — JS can call any public method of the exposed class.
- `setJavaScriptEnabled(true)` + `loadUrl` with a caller-supplied URL. **High** — XSS-equivalent.
- `setAllowFileAccessFromFileURLs(true)` / `setAllowUniversalAccessFromFileURLs(true)`. **High**
  (cross-origin file access from WebView).

## Step 7 — Signing and ProGuard / R8

```bash
grep -E "(signingConfig|signingConfigs|minifyEnabled|shrinkResources)" \
  android/app/build.gradle android/app/build.gradle.kts 2>/dev/null
```

Flag:

- Release builds without `minifyEnabled true` (no obfuscation). **Low** (not a vuln; makes reverse
  engineering easier).
- Signing config with passwords / keystore paths checked into the repo. **Critical** if the keystore
  is the production one.

## Step 8 — Tapjacking / overlay

If the app handles sensitive actions and `filterTouchesWhenObscured` isn't set on those views, an
attacker overlay can capture taps. **Low** for most apps, **Medium** for payments / 2FA UIs.

```bash
grep -rE "filterTouchesWhenObscured" --include="*.{kt,java,xml}" .
```
