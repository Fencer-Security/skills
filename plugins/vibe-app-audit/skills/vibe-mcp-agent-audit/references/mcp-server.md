# MCP server audit reference

Read when the project is an MCP server (`@modelcontextprotocol/sdk`, Python `mcp` / `fastmcp`). MCP
servers are processes that expose tools, resources, and prompts to MCP clients (Claude Desktop,
Claude Code, Cursor, etc.).

The threat model:

- **Transport**: stdio (local) vs. SSE/HTTP (network). Network MCP servers are services and need
  authentication; stdio servers are local processes that trust whoever runs them.
- **Tool surface**: every tool is a privilege. The server author chose what to expose; the audit
  asks whether those choices are least-privilege.
- **Tool boundary**: each handler validates its inputs. Without validation, the LLM (via the client)
  can call tools with adversarial args.

## Step 1 — Enumerate the tool surface

```bash
# TypeScript SDK
grep -rE "server\.tool\(|server\.registerTool\(|setRequestHandler.*tools" \
  --include="*.{ts,js}" . | head -30

# Python SDK
grep -rE "@mcp\.tool|@server\.list_tools|@server\.call_tool" \
  --include="*.py" . | head -30
```

For each tool, record name, parameter schema, and what the handler does. If there are more than ~10
tools, group them by side-effect class for the report.

## Step 2 — Classify each tool by side effect

| Class                          | Examples                                             | Audit focus                                                        |
| ------------------------------ | ---------------------------------------------------- | ------------------------------------------------------------------ |
| **Pure compute**               | `convert_units`, `format_date`                       | Schema validation; rate / size limits                              |
| **Filesystem read**            | `read_file`, `list_directory`, `search_files`        | Path canonicalization; containment to an allowed root              |
| **Filesystem write**           | `write_file`, `create_directory`, `move_file`        | Containment + write-allowlist; no overwriting code files           |
| **Subprocess**                 | `run_command`, `git_*`, `npm_install`                | Argument vector (not shell=True); allowlist of commands            |
| **Network (outbound)**         | `fetch_url`, `download`, `query_database`            | Scheme/host allowlist; no internal addresses (SSRF)                |
| **Network (inbound triggers)** | Posting to channels, sending emails, opening tickets | Authorization on the receiving end; rate limits                    |
| **Mutating external state**    | `delete_*`, `update_*`, `send_*`                     | Confirmation step on the client side or out-of-band; reversibility |

A server that exposes `read_file` + `write_file` + `run_command` over network transport is, in
effect, a remote shell. Flag this as **Critical** unless authentication and per-client scoping are
in place.

## Step 3 — Validate the tool boundary

For each handler, read the code:

```ts
server.tool(
    {
        name: "read_file",
        inputSchema: {
            type: "object",
            properties: { path: { type: "string" } },
            required: ["path"],
        },
    },
    async (args) => {
        // BUG: args.path used directly
        return await fs.readFile(args.path);
    }
);
```

Patterns to flag:

- Argument used directly without `realpath` / containment check (path tools). **High**.
- Argument concatenated into a shell command (subprocess tools). **Critical**.
- Argument used as URL with no scheme/host allowlist (network tools). **High** (SSRF).
- No size limit on string arguments — LLM can be tricked into sending megabytes. **Medium**.
- No try/catch — exceptions leak to the client as tool errors with stack traces. **Low**.

## Step 4 — Transport

```bash
grep -rE "(StdioServerTransport|SSEServerTransport|StreamableHttpServerTransport)" \
  --include="*.{ts,js,py}" . | head -10
```

**stdio** transport: server runs as a child process of the client. No network exposure. The client
controls the connection. Authorization is moot — the client process is trusted.

**SSE / HTTP** transport: server listens on a port. Anyone who can reach the port can invoke tools.
The audit must verify:

- Is the listener bound to `127.0.0.1` or `0.0.0.0`? Bound to `0.0.0.0` without auth: **Critical**.
- Is there an authentication layer (API key, OAuth)? Missing on network transport with destructive
  tools: **Critical**.
- Is TLS used for non-localhost listeners? Missing: **High**.

## Step 5 — Secrets in tool outputs

```bash
grep -rE "(process\.env|os\.environ).*=.*tool|return.*process\.env" \
  --include="*.{ts,js,py}" . | head -10
```

Flag:

- A tool that reads environment variables and returns them. **Critical** (designed-in leak).
- A tool that reads a credentials file and returns its contents to the LLM. **Critical**.
- A tool that fetches a URL and returns the full response — if the URL is server-controlled (e.g.,
  `http://169.254.169.254/`), this reveals cloud-instance metadata including IAM credentials.
  **High** (SSRF + metadata service).

## Step 6 — Resource / authorization

For multi-client MCP servers (network transport):

- Is there a per-client identity? An "API key" shared across clients doesn't help if leaked.
- Is there rate-limiting? A misbehaving client can hammer expensive tools.
- Is there a tool-allowlist per client? Production tools should not be exposed to development MCP
  clients.

For stdio servers, these don't apply.

## What to put in the report

One finding per tool with a validation bug. If three tools share the same root cause (e.g., all
filesystem tools skip canonicalization), group them: "Three filesystem tools (`read_file`,
`write_file`, `move_file`) accept caller-supplied paths without containment checks."

For the tool-surface findings, summarize at the top: "The server exposes 12 tools spanning
filesystem read/write, subprocess, and outbound HTTP. Exposed over SSE on `0.0.0.0:8080` with no
authentication."
