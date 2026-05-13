# React Native / Expo audit reference

Read when `react-native`, `expo`, or `@react-native-*` is in `package.json`. Most vibe-coded mobile
apps in 2026 are Expo apps — they share the same JS-bundle threat model as a React webapp, with
mobile-specific surfaces on top.

Also read `ios.md` and `android.md` for the per-platform sub-projects (which Expo manages behind
`expo prebuild`).

## Step 1 — Map the JS surface

```bash
ls package.json app.json app.config.js app.config.ts 2>/dev/null

# Entry points
ls App.tsx App.js index.tsx index.js src/App.tsx app/_layout.tsx 2>/dev/null

# Expo Router (file-system routing)
ls app/ 2>/dev/null | head -20
```

The JS bundle ships to the device — anything in `process.env`, `app.config.*`, or imported modules
is recoverable from the IPA/APK.

## Step 2 — Secrets and config

```bash
# Public env vars (in Expo, anything in process.env at build time ends up in the bundle)
grep -rE "process\.env\.(EXPO_PUBLIC_|REACT_APP_)" --include="*.{ts,tsx,js,jsx}" . | head -20

# Non-public env reads (these only work in server code, not in the app)
grep -rE "process\.env\.[A-Z_]+" --include="*.{ts,tsx,js,jsx}" . | head -20

# Hardcoded URLs / keys
grep -rE "(api\.|\.supabase\.co|sk_live_|sk_test_|firebase)" --include="*.{ts,tsx,js,jsx}" . | head -10

# expo-constants config access
grep -rE "Constants\.(expoConfig|manifest|expoGoConfig)\." --include="*.{ts,tsx,js,jsx}" . | head -10
```

Flag:

- `EXPO_PUBLIC_*` env var holding a server-side secret (Stripe live key, Twilio auth token, database
  password). **Critical** — the `EXPO_PUBLIC_` prefix means "this is in the bundle"; putting secrets
  there is the headline vibe-coded mobile mistake.
- API keys in `extra` of `app.config.js` (also bundled). **Medium–Critical** depending on what they
  unlock.
- Hardcoded Supabase service-role key. **Critical**.

## Step 3 — AsyncStorage vs secure-store

```bash
# AsyncStorage — not encrypted
grep -rE "(AsyncStorage|@react-native-async-storage)" --include="*.{ts,tsx,js,jsx}" .

# Secure alternatives
grep -rE "(react-native-keychain|expo-secure-store|@react-native-community/secure-store)" \
  --include="*.{ts,tsx,js,jsx}" .
```

For each `AsyncStorage.setItem` call, look at the key/value:

- `AsyncStorage.setItem("token", ...)` / `"authToken"` / `"refresh_token"`: **High**.
- `AsyncStorage.setItem("user_id", ...)`: **Low** (identifier, not credential).
- `AsyncStorage.setItem("preferences", ...)`: OK.

`expo-secure-store` writes to iOS Keychain / Android Keystore-backed encrypted storage — this is the
right place for tokens.

## Step 4 — WebView

```bash
grep -rE "(react-native-webview|WebView)" --include="*.{ts,tsx,js,jsx}" .
grep -rE "(onMessage|injectedJavaScript|injectedJavaScriptBeforeContentLoaded|postMessage)" \
  --include="*.{ts,tsx,js,jsx}" .
```

Patterns to flag:

- `WebView source={{ uri: <attacker-influenceable-url> }}` AND `onMessage` handler that acts on the
  message data. **High**.
- `injectedJavaScript` containing user-supplied content. **Critical**.
- `originWhitelist={['*']}` AND a WebView that loads remote content. **High**.

## Step 5 — Deep linking

Expo provides `expo-linking`:

```bash
grep -rE "(Linking\.(addEventListener|getInitialURL|parse)|useURL|createURL)" \
  --include="*.{ts,tsx,js,jsx}" .
```

For each handler, walk the code path: what does it do with the URL parameters?

Flag:

- Handler reads an auth token / session ID from the URL and signs the user in. **Critical**.
- Handler performs destructive action without confirmation. **High**.
- Handler uses `parse(url).queryParams.userId` to set the current user. **Critical**.

Check `app.json` / `app.config.js` for the `scheme`:

```bash
grep -E "scheme|associatedDomains|intentFilters" app.json app.config.js app.config.ts 2>/dev/null
```

- Unique scheme is fine but not verified (any app can register the same scheme).
- Associated domains (universal links) require AASA / assetlinks files at the configured domain.

## Step 6 — Over-the-air (OTA) updates

`expo-updates` lets the app pull new JS bundles from a server without a store update.

```bash
grep -E "expo-updates" package.json 2>/dev/null
grep -A10 "updates" app.json app.config.js 2>/dev/null
```

Flag:

- OTA updates configured to load from a non-EAS, non-Expo, non-self-controlled URL. **High** —
  whoever controls that URL can ship code to the app.
- `updates.codeSigningCertificate` not configured for production. **Medium** — without code signing,
  a network attacker controlling the update channel can swap the bundle.

## Step 7 — Native modules from npm

React Native projects pull native code via npm. Each package can contain native iOS/Android code
that runs at full app privilege.

```bash
grep -hE '"react-native-' package.json | head -30
```

For unfamiliar `react-native-*` packages:

- Is it maintained? (last update > 2 years ago is a flag).
- Does it have many GitHub issues about security or installation problems?

This is a softer check — you're looking for obviously-sketchy packages. Don't flag every unfamiliar
package; flag ones that handle sensitive operations (auth, payments, crypto) and have weak signals.

## Step 8 — Hermes vs JSC

Hermes (Meta's JS engine, default in new RN versions) generates bytecode at build time. JSC ships
source. Hermes makes simple reverse-engineering harder but isn't a security boundary — don't claim
it as a control. Note in the report only if the user asks about app obfuscation.
