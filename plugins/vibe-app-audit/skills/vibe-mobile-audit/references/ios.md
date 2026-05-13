# iOS audit reference

Read when an iOS native project (Swift / Objective-C) or an iOS sub-project of a React Native / Expo
app is detected.

## Step 1 — Map the project

```bash
find . -maxdepth 4 -name "*.xcodeproj" -o -name "*.xcworkspace" | head -5
find . -maxdepth 5 -name "Info.plist" | grep -v build | head -10
find . -maxdepth 4 -name "Podfile" -o -name "Package.swift"
```

The main `Info.plist` is in `ios/<ProjectName>/Info.plist` for React Native projects, or
`<ProjectName>/Info.plist` for pure-native projects. Read it — it's where most of the platform
settings live.

## Before flagging — meta-NEVER for iOS

**NEVER store an auth token, refresh token, or biometric secret in `UserDefaults`** — even
"temporarily" or "just for the prototype." `UserDefaults` is a plist in the app sandbox, readable by
anyone with the device backup, recoverable on jailbroken devices, and synchronized to iCloud if the
user has iCloud backup on. The Keychain exists for exactly this purpose. **Severity: High** when the
stored value is a credential.

**NEVER use `evaluateJavaScript` with a string composed from any data not under your sole control**
(user input, network responses, file contents). It's `eval` for native, exposing the JS context (and
therefore message handlers, and therefore native methods) to whoever influenced the string.
**Severity: Critical**.

## Step 2 — Keychain vs UserDefaults

Tokens, passwords, biometric secrets, and any long-lived credential belong in the Keychain.
`UserDefaults` is for non-sensitive preferences (theme, last-opened tab).

```bash
grep -rE "UserDefaults\.(standard|init)" --include="*.{swift,m}" .
```

For each `UserDefaults` write, look at what's being stored. Flag any of:

- `setValue(token, forKey:)` / `set(_, forKey: "...token...")` — auth token in UserDefaults.
  **High**.
- API key / secret stored similarly. **Medium–High** depending on what it unlocks.
- PII (email, phone) — **Low** alone, **Medium** if combined with persistent identifiers.

For Keychain usage, check the accessibility attribute:

```bash
grep -rE "(kSecAttrAccessible|accessGroup|accessible:)" --include="*.{swift,m}" .
```

- `kSecAttrAccessibleAlways` / `…AfterFirstUnlock`: items survive device-locked state. Fine for
  background-required tokens, suspect for high-value secrets.
- `kSecAttrAccessibleWhenUnlockedThisDeviceOnly`: best for secrets that shouldn't sync to iCloud
  keychain.
- Missing accessibility (default `kSecAttrAccessibleAlways` pre-iOS 9, otherwise framework default):
  note in report.

## Step 3 — App Transport Security (Info.plist)

Look for the `NSAppTransportSecurity` dictionary:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>
```

Severity table:

| Setting                              | Severity                                                       |
| ------------------------------------ | -------------------------------------------------------------- |
| `NSAllowsArbitraryLoads: YES`        | **High** if in production, **Medium** if dev-only and stripped |
| `NSAllowsArbitraryLoadsInWebContent` | **Medium** — WebView allowed cleartext                         |
| `NSAllowsLocalNetworking`            | OK by itself; flag if user data flows here                     |
| `NSExceptionDomains` (per-host)      | **Low** if scoped to one third-party that doesn't support TLS  |

`NSAllowsArbitraryLoads` with no `NSExceptionDomains` means the entire app can talk plain HTTP. For
vibe-coded apps shipped to production, this is **High**.

## Step 4 — URL schemes

```bash
grep -A5 "CFBundleURLSchemes" ios/<project>/Info.plist app.json
```

For each scheme:

- Is the scheme unique enough that another app can't register the same one? `myapp://` is fine;
  `com.example.myapp://` is better.
- Is there a Universal Link (`apple-app-site-association`) replacing or supplementing it? Universal
  Links are platform-verified; URL schemes are not.

For the URL handler (`application(_:open:options:)` or `SceneDelegate.scene(_:openURLContexts:)`),
read the code:

```bash
grep -rE "(application\(_:open:|openURLContexts|onOpenURL)" --include="*.swift" . | head -10
```

Flag:

- Handler reads `URLComponents.queryItems` and signs the user in based on a token in the URL.
  **Critical**.
- Handler performs `delete` / `purchase` / `transfer` actions without a confirmation step. **High**.

## Step 5 — WebView

Modern apps use `WKWebView`. Old apps use `UIWebView` (deprecated, removed in iOS 12+).

```bash
grep -rE "(WKWebView|UIWebView)" --include="*.{swift,m}" .
grep -rE "(addUserScript|addScriptMessageHandler|evaluateJavaScript)" --include="*.{swift,m}" .
```

Flag:

- `evaluateJavaScript` with caller-supplied input. **Critical**.
- `addScriptMessageHandler` exposing a method that does file I/O / network / shell. **High**;
  **Critical** if the WebView loads anything other than bundled `file://` content.
- WebView loading attacker-influenceable URLs. **High**.

## Step 6 — File protection

```bash
grep -rE "(FileProtectionType|NSFileProtection|setAttributes.*Protection)" \
  --include="*.{swift,m}" .
```

- `.complete` / `NSFileProtectionComplete`: file readable only when device unlocked.
- `.completeUntilFirstUserAuthentication` / `NSFileProtectionCompleteUntilFirstUserAuthentication`:
  default for many app data; readable after first unlock until reboot.
- `.none` / `NSFileProtectionNone`: always readable. **Flag for sensitive content**.

## Step 7 — Universal Links

```bash
find . -name "apple-app-site-association"
```

If the app declares universal links (in `Associated Domains` entitlement) but no AASA file is
published at the team's domain, the links won't be verified — another app could register them. Note
as **Medium**.

For the AASA file content, check that `paths` aren't too permissive (`"*"` matches everything,
including admin/internal paths).

## Step 8 — Entitlements

`<Project>.entitlements`:

```bash
find . -name "*.entitlements" | head -5
```

Flag:

- `com.apple.developer.icloud-services` for an app that stores secrets without explicit user
  consent. **Medium** (data may sync via iCloud).
- `keychain-access-groups` shared across an attacker-controlled team (rare but possible if the user
  is collaborating with a published app). **High** if used carelessly.
