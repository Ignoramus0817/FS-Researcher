#!/usr/bin/env bash
# jina_read.sh — fetch a webpage via Jina AI Reader, archive it, echo the body.
#
# Usage:
#   scripts/jina_read.sh "<url>" "<slug>"               # archive + echo body
#   scripts/jina_read.sh "<url>" "<slug>" --no-archive  # only echo body, skip archive
#   scripts/jina_read.sh "<url>" "<slug>" --dir <path>  # override archive dir
#
# Defaults:
#   archive dir = "./knowledge_base/sources"
#   output file = "<archive_dir>/<slug>.md" (created if missing, parents auto-made)
#   written body = YAML frontmatter ({url, title, fetched_at}) + full markdown content
#
# Environment:
#   JINA_API_KEY  (recommended) Bearer token; without it the rate limit is ~20 RPM.
#
# Output (stdout): the full fetched content (markdown). The host agent should
# read this for note-taking; the archive file is the durable record.
#
# Exit codes:
#   0 — success (archive written if enabled, body echoed)
#   1 — Jina request failed (network, HTTP error, empty content)
#   2 — bad arguments

set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "usage: jina_read.sh <url> <slug> [--no-archive] [--dir <archive_dir>]" >&2
  exit 2
fi

URL="$1"
SLUG="$2"
shift 2

ARCHIVE=1
DIR="./knowledge_base/sources"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --no-archive) ARCHIVE=0; shift ;;
    --dir) DIR="$2"; shift 2 ;;
    *) echo "error: unknown arg: $1" >&2; exit 2 ;;
  esac
done

if [[ -z "$URL" || -z "$SLUG" ]]; then
  echo "error: url and slug are both required" >&2
  exit 2
fi

# Normalize slug: lowercase, [a-z0-9-] only.
CLEAN_SLUG=$(printf '%s' "$SLUG" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -E 's/[^a-z0-9-]+/-/g; s/^-+|-+$//g')
if [[ -z "$CLEAN_SLUG" ]]; then
  CLEAN_SLUG="webpage-$(date +%s)"
fi

if [[ -z "${JINA_API_KEY:-}" ]]; then
  echo "warn: JINA_API_KEY is not set; requests will be rate-limited to ~20 RPM" >&2
fi

HDR_AUTH=()
if [[ -n "${JINA_API_KEY:-}" ]]; then
  HDR_AUTH=(-H "Authorization: Bearer ${JINA_API_KEY}")
fi

BODY=$(printf '{"url":%s}' \
  "$(printf '%s' "$URL" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')")

RESP=$(curl -fsS \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'X-Engine: browser' \
  -H 'X-Return-Format: markdown' \
  "${HDR_AUTH[@]}" \
  --data "$BODY" \
  'https://r.jina.ai/') || {
    echo "error: jina read request failed for url: $URL" >&2
    exit 1
  }

# Parse the response to extract title + content (markdown). Jina Reader returns
# either {"code":200,"data":{"title":...,"content":...,...}} or a similar shape.
PARSED=$(python3 - "$RESP" <<'PY'
import json, sys, time
raw = sys.argv[1]
try:
    obj = json.loads(raw)
except Exception:
    # Non-JSON response — treat the whole thing as content, no title.
    print(json.dumps({"title": "", "content": raw, "ok": bool(raw.strip())},
                     ensure_ascii=False))
    sys.exit(0)
data = obj.get("data") if isinstance(obj, dict) else None
if isinstance(data, dict):
    title = data.get("title") or ""
    content = data.get("content") or data.get("text") or ""
elif isinstance(obj, dict):
    title = obj.get("title") or ""
    content = obj.get("content") or obj.get("text") or ""
else:
    title, content = "", ""
ok = bool((content or "").strip())
print(json.dumps({"title": title, "content": content, "ok": ok},
                 ensure_ascii=False))
PY
)

TITLE=$(printf '%s' "$PARSED" | python3 -c 'import json,sys;print(json.load(sys.stdin)["title"])')
CONTENT=$(printf '%s' "$PARSED" | python3 -c 'import json,sys;print(json.load(sys.stdin)["content"])')
OK=$(printf '%s' "$PARSED" | python3 -c 'import json,sys;print(json.load(sys.stdin)["ok"])')

if [[ "$OK" != "True" ]]; then
  echo "error: jina returned empty content for url: $URL" >&2
  exit 1
fi

TS=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

if [[ "$ARCHIVE" == "1" ]]; then
  mkdir -p "$DIR"
  OUT="$DIR/$CLEAN_SLUG.md"
  if [[ -e "$OUT" ]]; then
    # Avoid overwriting a different page that coincidentally shares the slug.
    OUT="$DIR/$CLEAN_SLUG-$(date +%s).md"
  fi
  {
    printf -- '---\n'
    printf 'url: %s\n' "$URL"
    # Replace embedded newlines in title to keep frontmatter valid.
    CLEAN_TITLE=$(printf '%s' "$TITLE" | tr '\n\r' '  ')
    printf 'title: %s\n' "$CLEAN_TITLE"
    printf 'fetched_at: %s\n' "$TS"
    printf -- '---\n\n'
    printf '%s\n' "$CONTENT"
  } > "$OUT"
  echo "archived: $OUT" >&2
fi

printf '%s\n' "$CONTENT"
