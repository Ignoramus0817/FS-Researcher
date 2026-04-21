"""jina_search.py — Python port of jina_search.sh (cross-platform, requests-based).

Usage:
    python jina_search.py "<query>" [num_results=10] [--out <file>]
"""
from __future__ import annotations

import json
import os
import sys
import time

import requests


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1]:
        print("usage: jina_search.py <query> [num_results=10] [--out <file>]", file=sys.stderr)
        return 2

    query = sys.argv[1]
    num = 10
    out_file = None
    i = 2
    while i < len(sys.argv):
        a = sys.argv[i]
        if a == "--out":
            out_file = sys.argv[i + 1]
            i += 2
        else:
            try:
                num = int(a)
            except ValueError:
                pass
            i += 1

    api_key = os.environ.get("JINA_API_KEY", "")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Respond-With": "no-content",
        "User-Agent": UA,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if os.environ.get("JINA_LOCALE"):
        headers["X-Locale"] = os.environ["JINA_LOCALE"]
    if os.environ.get("JINA_COUNTRY"):
        headers["X-Country"] = os.environ["JINA_COUNTRY"]

    payload = {"q": query, "num": num}

    last_err = ""
    raw = None
    for attempt in range(5):
        try:
            r = requests.post(
                "https://s.jina.ai/",
                json=payload,
                headers=headers,
                timeout=180,
            )
            if r.status_code == 200:
                raw = r.text
                break
            last_err = f"HTTP {r.status_code}: {r.text[:300]}"
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(3 * (attempt + 1))
                continue
            break
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
            time.sleep(3 * (attempt + 1))
            continue

    if raw is None:
        print(f"error: jina search failed: {last_err}", file=sys.stderr)
        return 1

    try:
        obj = json.loads(raw)
    except Exception:
        out = raw
    else:
        if isinstance(obj, dict) and isinstance(obj.get("data"), list):
            out = json.dumps(obj["data"], ensure_ascii=False, indent=2)
        else:
            out = json.dumps(obj, ensure_ascii=False, indent=2)

    if out_file:
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"wrote: {out_file}", file=sys.stderr)
    else:
        sys.stdout.write(out + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
