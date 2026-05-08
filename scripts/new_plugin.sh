#!/usr/bin/env bash
# Scaffold a new plugin under plugins/<name>/ with both Claude and Codex manifests.
# Usage: scripts/new_plugin.sh <plugin-name> "<description>"

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <plugin-name> \"<description>\"" >&2
  exit 2
fi

NAME="$1"
DESCRIPTION="$2"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_DIR="$REPO_ROOT/plugins/$NAME"

if [[ -e "$PLUGIN_DIR" ]]; then
  echo "ERROR: $PLUGIN_DIR already exists" >&2
  exit 1
fi

if [[ ! "$NAME" =~ ^[a-z0-9][a-z0-9-]*$ ]]; then
  echo "ERROR: plugin name must match ^[a-z0-9][a-z0-9-]*$" >&2
  exit 1
fi

mkdir -p \
  "$PLUGIN_DIR/.claude-plugin" \
  "$PLUGIN_DIR/.codex-plugin" \
  "$PLUGIN_DIR/skills"

MANIFEST=$(cat <<JSON
{
  "name": "$NAME",
  "description": "$DESCRIPTION",
  "version": "0.1.0",
  "author": {
    "name": "Fencer",
    "url": "https://fencer.dev"
  },
  "homepage": "https://github.com/Fencer-Security/skills/tree/main/plugins/$NAME",
  "license": "Apache-2.0"
}
JSON
)

printf '%s\n' "$MANIFEST" > "$PLUGIN_DIR/.claude-plugin/plugin.json"
printf '%s\n' "$MANIFEST" > "$PLUGIN_DIR/.codex-plugin/plugin.json"

cat > "$PLUGIN_DIR/README.md" <<MD
# $NAME

$DESCRIPTION

## Skills

_(Add skills under \`skills/<skill-name>/SKILL.md\`.)_

## Install

\`\`\`
/plugin marketplace add https://github.com/Fencer-Security/skills
/plugin install $NAME@fencer
\`\`\`
MD

echo "Created plugin at $PLUGIN_DIR"
echo "Next:"
echo "  - Add skills under $PLUGIN_DIR/skills/<skill-name>/SKILL.md"
echo "  - Add an entry for '$NAME' to .claude-plugin/marketplace.json"
echo "  - Run scripts/validate_manifests.py"
