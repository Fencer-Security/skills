# intel

Look up public vulnerability intel from [Fencer Intel](https://intel.fencer.dev) and give a short,
cited answer. The feed merges CVE, GHSA, and OSV records with CISA KEV, EPSS, public exploits, and
the distro advisories the site is allowed to display.

The plugin registers Intel's existing MCP server at `https://intel.fencer.dev/mcp`. That server is
public and needs no API key. This repo does not ship a second MCP server: the hosted one already
applies the public-distro filter and the attribution the site requires. A copy here would drift
from both.

## Skills

- **[`intel-triage`](skills/intel-triage/SKILL.md)** — One CVE, GHSA, or OSV id. Pulls the record,
  KEV, EPSS, severity, exploits, and fixed versions, then a short priority.
- **[`intel-check-deps`](skills/intel-check-deps/SKILL.md)** — A package list, lockfile excerpt, or
  SBOM. Looks up known vulns and fixed versions. This is a feed lookup, not a scanner.
- **[`intel-brief`](skills/intel-brief/SKILL.md)** — Newly published or newly KEV-added vulns over a
  time window, optionally filtered to a stack. Ends with the public feed URL for keeping watch.

There is no scheduled watcher in this repo. `intel-brief` prints the RSS URL that matches the
brief. Slack can subscribe with `/feed subscribe <url>`.

## Install

### Claude Code

```
/plugin marketplace add https://github.com/Fencer-Security/skills
/plugin install fencer-intel@fencer
/reload-plugins
```

The plugin's `.mcp.json` connects `fencer-intel` when the plugin is enabled.

### Codex

```bash
git clone https://github.com/Fencer-Security/skills ~/src/fencer-skills
ln -s ~/src/fencer-skills/plugins/intel ~/.codex/plugins/intel
```

The Codex manifest points `mcpServers` at `.mcp.json`. To add the server without the plugin:

```bash
codex mcp add fencer-intel --url https://intel.fencer.dev/mcp
```

### Other MCP clients

```json
{
  "mcpServers": {
    "fencer-intel": {
      "type": "http",
      "url": "https://intel.fencer.dev/mcp"
    }
  }
}
```

## What gets sent

A dependency check sends the lockfile, SBOM, or package list to `https://intel.fencer.dev`. The
MCP `check_stack` tool returns findings and does not store a public report. `POST /api/v1/stack`
does store one; the skills do that only when you ask.

Installing the plugin connects the agent to `https://intel.fencer.dev/mcp` over HTTPS, with no API
key. That server defines the `fencer-intel` tools and writes the responses the skills quote. CI
checks the tool names this plugin documents against a recorded `tools/list`. A running client uses
the tools the server returns when it connects.

## What this does not do

- It does not scan a network, a registry, or a container image you did not pass in.
- It does not show distro data the public feed excludes (Amazon Linux, Oracle Linux, Wolfi,
  Chainguard, Chainguard Libraries, Echo, MinimOS, Fedora, Photon OS, Red Hat Hummingbird,
  SecureOS). Those sources are not wired up. No admin token and no Access JWT.
- It does not keep a copy of a lockfile. See "What gets sent" above.

## License

[Apache-2.0](../../LICENSE). Feed data stays under the terms named in each skill's Sources
section. "Fencer" is a trademark of Fencer; see [NOTICE](../../NOTICE).
