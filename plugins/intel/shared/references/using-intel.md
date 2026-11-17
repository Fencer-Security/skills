# Using Fencer Intel

Read this before calling the feed. It is the contract for every skill in this plugin.

Fencer Intel (https://intel.fencer.dev) is a public vulnerability feed. It merges the CVE List,
GitHub advisories, maintainer repository advisories, OSV, NVD, CISA KEV, ENISA EUVD, FIRST EPSS,
Exploit-DB, Metasploit, Anchore NVD corrections, public distro advisories, and CISA / Red Hat CSAF
into one entry per vulnerability. No account and no API key.

The plugin connects to the feed's existing MCP server. It does not ship a second server.

## MCP server

Name: `fencer-intel`. URL: `https://intel.fencer.dev/mcp`. Transport: Streamable HTTP. No headers,
no token.

Tools, and the arguments recorded from `tools/list` on 2026-11-17:

- `search` — `q`, `severity`, `kev`, `exploited`, `tech`, `ecosystem`, `vendor`, `package`,
  `published`, `type`, `limit`
- `get_vulnerability` — `id`
- `list_feed` — `filter`, `tech`, `ecosystem`, `vendor`, `limit`, `cursor`
- `check_stack` — `lockfile`, `filename`, `packages`

Call those tools. A client may prefix the names (for example `mcp__fencer-intel__search`). Use the
prefixed tool this session actually exposes. Omit arguments you are not setting. `limit` is an
integer (`search` 1 to 50, `list_feed` 1 to 100). `kev` and `exploited` are booleans. `severity` is
`critical`, `high`, `medium`, `low`, or `none`. `type` is `cve`, `ghsa`, or `osv`. Lists may be
arrays. Unknown arguments are errors. Do not call the authenticated app API or the admin API.

`published` on `search` is a publish-date window: `2024`, `2024-05`, `2024-01-01..2024-03-31`,
`>=2024-01-01`, `<2024-01-01`, or `30d`. `filter` on `list_feed` is only `critical` or `kev`.
`critical` means in CISA KEV, or CISA SSVC exploitation `active`, or CVSS 9+ in a listed technology
(WordPress plugins and themes excepted; WordPress itself counts), or CVSS 7+ with EPSS >= 0.1.

Ecosystems: `npm`, `pypi`, `go`, `maven`, `crates.io`, `packagist`, `rubygems`, `hex`, `nuget`,
`github-actions`, `pub`, `swift`, `hackage`, `ghc`, `cran`, `opam`, `julia`, `bitnami`.

`check_stack` reads a lockfile or SBOM (`lockfile` plus `filename`) or exact versions (`packages`:
`ecosystem`, `name`, `version`). It does not store a report. `POST /api/v1/stack` does store a
public unlisted report. Do not POST a lockfile or SBOM there unless the user explicitly wants that
public report.

## If the MCP tools are not available

Stop and tell the user how to connect the server (see the plugin README). Then, only if they still
want the lookup in this session, call the public JSON API with GET:

- `GET https://intel.fencer.dev/api/v1/entries/<id>` — one entry. Follow redirects; aliases move to
  the canonical id.
- `GET https://intel.fencer.dev/api/v1/entries?filter=&tech=&ecosystem=&vendor=&limit=&cursor=`
- `GET https://intel.fencer.dev/api/v1/search?q=&severity=&kev=&exploited=&tech=&ecosystem=&vendor=&package=&published=&type=&limit=&offset=`

```bash
curl -fsSL "https://intel.fencer.dev/api/v1/entries/CVE-2024-3094"
```

A 400 body is `{"error": "..."}`. Pass the message back. Do not retry with extra parameters.

There is no public GET that checks a lockfile. Without `check_stack`, say exact version matching is
unavailable until the MCP server is connected. Do not POST the file to create a stored report unless
the user asks for one.

## Do not invent data

Every id, score, date, package, and fixed version in the answer must come from a tool result in this
session. If `get_vulnerability` errors that Intel has no entry, or a search `total` is 0, say so and
stop. Do not fill the gap from memory, from another site, or from a previous conversation.

`search` may return `broader` suggestions. Those are further queries, not findings. Run one only
when it still answers the user's question, and label it as a broader query.

No matches means the feed found none. It does not mean the packages are safe.

## Flags to keep

- `maintainerAdvisory.unreviewed` or a finding `unreviewed: true` — GitHub has not reviewed the
  maintainers' advisory. Say the affected versions are the maintainers' word.
- `inferredPackages`, or a finding `inferred: true` — no advisory lists the package. Say "probably"
  and that the match is low confidence. An `unchecked` item with reason `inferred`, `maintainer`, or
  `cve` may be affected; the feed could not decide the version.
- `withdrawn` — the record is withdrawn or rejected. Say that, and do not recommend a patch as if
  the vulnerability is live.
- Arch OS rows with `possible: true` — Arch's tracker has no introduced version. Say "may be
  affected".
- `unchecked` reason `derivative` — an Arch derivative (Manjaro, EndeavourOS, Garuda) was not
  matched. Say it was not checked.
- `eol` — endoflife.date says the version is out of support. That is not, by itself, a
  vulnerability.

## Distros the public feed does not publish

These advisories are stored for scanning only and are excluded from the public API, feeds, and MCP
tools. Never retrieve or display them, and never ask the user for an admin token or an Access JWT to
reach them:

Amazon Linux, Oracle Linux, Wolfi, Chainguard, Chainguard Libraries, Echo, MinimOS, Fedora, Photon
OS, Red Hat Hummingbird, SecureOS.

Public OS matching covers Debian, Ubuntu, Red Hat, SUSE, openSUSE, AlmaLinux, Rocky Linux, Alpine,
Azure Linux, and Arch Linux, and only from an SBOM passed to `check_stack` (deb, apk, rpm, and Arch
alpm package URLs). A release with no advisories on file comes back unchecked. Do not guess.

Nuclei templates and GitHub proof-of-concept repositories are not in the public feed. Do not add
them.

## Links

Every vulnerability you name is a markdown link to its `url` field, or to
`https://intel.fencer.dev/<id>` using the canonical `id` from the response. Also link the feed when
you tell the user how to keep watching: `https://intel.fencer.dev/feed` with the same `filter`,
`tech`, `ecosystem`, and `vendor` values.

## Attribution

The public site requires this whenever you state facts from the feed. End the answer with the
Sources paragraph. Copy it unchanged:

```text
Data from the CVE Program, GitHub, OSV, NIST NVD, CISA, ENISA, FIRST, OffSec, Rapid7, ProjectDiscovery, the Haskell, R Consortium, OCaml and Julia security advisory databases, Bitnami, Anchore, Debian, Red Hat (CC BY 4.0), SUSE, openSUSE, AlmaLinux, Rocky Linux, Canonical (Ubuntu), Alpine Linux, Microsoft (Azure Linux, MIT), the Arch Linux security team, CISA's ICS and IT advisories and Red Hat VEX (CC BY 4.0) under their respective terms; Ubuntu and Alpine fixes are CC BY-SA 4.0. This product uses data from the NVD API but is not endorsed or certified by the NVD. ATT&CK technique mappings by the MITRE Center for Threat-Informed Defense (Apache-2.0); © 2026 The MITRE Corporation, reproduced and distributed with the permission of The MITRE Corporation; ATT&CK® is a registered trademark of The MITRE Corporation. Ransomware groups from the Ransomware Vulnerability Matrix by BushidoUK, CC BY 4.0, reformatted per CVE. Maintainers' repository security advisories from GitHub: facts and a link only, the advisories stay with their authors on GitHub. Zero-day listings from Google Project Zero's 0day In-the-Wild tracker. End-of-life data from endoflife.date (MIT).
```

When the result includes these objects, copy `name`, `url`, and `attribution` verbatim next to the
data they cover. Do not paraphrase them.

- `attack.credit` next to ATT&CK techniques
- `ransomware.credit` next to ransomware groups
- each `vendorAdvisories[].credit` next to that advisory
- `fixes.distros[].license` next to that distro's fixes

`check_stack` does not return those objects. When you show Ubuntu, Alpine, or Azure Linux fixes from
a stack result, still attach the license line. Prefer `fixes.distros[].license` from
`get_vulnerability` when you fetch that entry. If you do not have the object, use these lines, which
are the ones the feed attaches:

- Ubuntu (CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/): Ubuntu security data ©
  Canonical Ltd., from https://github.com/canonical/ubuntu-security-notices via OSV; changed:
  normalised to fixed package versions per release.
- Alpine (CC BY-SA 4.0, https://creativecommons.org/licenses/by-sa/4.0/): Alpine secdb © Alpine
  Linux, from https://secdb.alpinelinux.org via OSV; changed: normalised to fixed package versions
  per release.
- Azure Linux (MIT, https://github.com/microsoft/AzureLinuxVulnerabilityData/blob/main/LICENSE):
  Azure Linux vulnerability data, Copyright (c) Microsoft Corporation, from
  https://github.com/microsoft/AzureLinuxVulnerabilityData via OSV, under the MIT licence; changed:
  normalised to fixed package versions per release.

Mention Fencer's paid product only when the user asks about ongoing monitoring of their
repositories. The feed attribution above is required either way.
