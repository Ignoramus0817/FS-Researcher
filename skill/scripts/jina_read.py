"""jina_read.py — Python port of jina_read.sh (cross-platform, requests-based).

Usage:
    python jina_read.py <url> <slug> [--no-archive] [--dir <archive_dir>] [--quiet]

Archives full markdown under "<archive_dir>/<slug>.md" with YAML frontmatter and
(unless --quiet) echoes the body to stdout. Defaults: archive_dir = ./knowledge_base/sources.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import sys
import time

import requests


UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def slugify(slug: str) -> str:
    s = slug.lower()
    s = re.sub(r"[^a-z0-9-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s or f"webpage-{int(time.time())}"


def main() -> int:
    argv = sys.argv[1:]
    if len(argv) < 2:
        print("usage: jina_read.py <url> <slug> [--no-archive] [--dir <archive_dir>] [--quiet]", file=sys.stderr)
        return 2

    url = argv[0]
    slug = argv[1]
    archive = True
    archive_dir = "./knowledge_base/sources"
    quiet = False

    i = 2
    while i < len(argv):
        a = argv[i]
        if a == "--no-archive":
            archive = False
            i += 1
        elif a == "--dir":
            archive_dir = argv[i + 1]
            i += 2
        elif a == "--quiet":
            quiet = True
            i += 1
        else:
            print(f"error: unknown arg: {a}", file=sys.stderr)
            return 2

    if not url or not slug:
        print("error: url and slug are both required", file=sys.stderr)
        return 2

    clean_slug = slugify(slug)
    api_key = os.environ.get("JINA_API_KEY", "")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "X-Engine": "browser",
        "X-Return-Format": "markdown",
        "User-Agent": UA,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {"url": url}
    raw = None
    last_err = ""
    for attempt in range(5):
        try:
            r = requests.post(
                "https://r.jina.ai/",
                json=payload,
                headers=headers,
                timeout=240,
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
        print(f"error: jina read failed for {url}: {last_err}", file=sys.stderr)
        return 1

    try:
        obj = json.loads(raw)
    except Exception:
        title, content = "", raw
    else:
        data = obj.get("data") if isinstance(obj, dict) else None
        if isinstance(data, dict):
            title = data.get("title") or ""
            content = data.get("content") or data.get("text") or ""
        elif isinstance(obj, dict):
            title = obj.get("title") or ""
            content = obj.get("content") or obj.get("text") or ""
        else:
            title, content = "", ""

    if not (content or "").strip():
        print(f"error: jina returned empty content for url: {url}", file=sys.stderr)
        return 1

    ts = _dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    if archive:
        os.makedirs(archive_dir, exist_ok=True)
        out_path = os.path.join(archive_dir, f"{clean_slug}.md")
        if os.path.exists(out_path):
            out_path = os.path.join(archive_dir, f"{clean_slug}-{int(time.time())}.md")
        clean_title = (title or "").replace("\n", " ").replace("\r", " ")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f"url: {url}\n")
            f.write(f"title: {clean_title}\n")
            f.write(f"fetched_at: {ts}\n")
            f.write("---\n\n")
            f.write(content)
            if not content.endswith("\n"):
                f.write("\n")
        print(f"archived: {out_path}", file=sys.stderr)

    if not quiet:
        sys.stdout.write(content)
        if not content.endswith("\n"):
            sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
