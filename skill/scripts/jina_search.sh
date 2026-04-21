#!/usr/bin/env bash
# jina_search.sh — search the web via Jina AI and emit LLM-friendly JSON.
#
# Usage:
#   scripts/jina_search.sh "<query>"              # default: 10 results, JSON
#   scripts/jina_search.sh "<query>" <num>        # custom result count (1..20)
#
# Environment:
#   JINA_API_KEY  (recommended) Bearer token; without it the rate limit is ~20 RPM.
#   JINA_LOCALE   (optional)    e.g. "zh-CN", "en-US". Biases the search locale.
#   JINA_COUNTRY  (optional)    ISO country code, e.g. "cn", "us".
#
# Output (stdout): JSON array, each item has keys: title, url, content, description.
# Errors: non-zero exit, message to stderr.
#
# Notes:
# - Endpoint: https://s.jina.ai/
# - "Every request costs a fixed number of tokens" — design queries deliberately.
# - Prefer 2-5 complementary queries in parallel (agents should batch tool calls),
#   not 20 near-duplicate queries.

set -euo pipefail

if [[ $# -lt 1 || -z "${1:-}" ]]; then
  echo "usage: jina_search.sh <query> [num_results=10]" >&2
  exit 2
fi

QUERY="$1"
NUM="${2:-10}"

if [[ -z "${JINA_API_KEY:-}" ]]; then
  echo "warn: JINA_API_KEY is not set; requests will be rate-limited to ~20 RPM" >&2
fi

HDR_AUTH=()
if [[ -n "${JINA_API_KEY:-}" ]]; then
  HDR_AUTH=(-H "Authorization: Bearer ${JINA_API_KEY}")
fi

HDR_LOCALE=()
if [[ -n "${JINA_LOCALE:-}" ]]; then
  HDR_LOCALE=(-H "X-Locale: ${JINA_LOCALE}")
fi

HDR_COUNTRY=()
if [[ -n "${JINA_COUNTRY:-}" ]]; then
  HDR_COUNTRY=(-H "X-Country: ${JINA_COUNTRY}")
fi

BODY=$(printf '{"q":%s,"num":%s}' \
  "$(printf '%s' "$QUERY" | python3 -c 'import json,sys;print(json.dumps(sys.stdin.read()))')" \
  "$NUM")

RESP=$(curl -fsS \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json' \
  -H 'X-Respond-With: no-content' \
  "${HDR_AUTH[@]}" \
  "${HDR_LOCALE[@]}" \
  "${HDR_COUNTRY[@]}" \
  --data "$BODY" \
  'https://s.jina.ai/') || {
    echo "error: jina search request failed for query: $QUERY" >&2
    exit 1
  }

# Extract the "data" array (list of {title,url,description,content,...}).
# Fall back to raw response if the shape is unexpected.
python3 - "$RESP" <<'PY'
import json, sys
raw = sys.argv[1]
try:
    obj = json.loads(raw)
except Exception:
    print(raw)
    sys.exit(0)
if isinstance(obj, dict) and "data" in obj and isinstance(obj["data"], list):
    print(json.dumps(obj["data"], ensure_ascii=False, indent=2))
else:
    print(json.dumps(obj, ensure_ascii=False, indent=2))
PY
