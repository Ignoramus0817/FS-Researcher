"""
Tools for Research Agent Minimal
Includes: search_web, read_webpage, and filesystem tools
"""
import re
import time
import logging
import subprocess
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from .config import (
        JINA_API_KEY,
        SERPER_API_KEY,
    )
except Exception:  # pragma: no cover
    from config import (  # type: ignore
        JINA_API_KEY,
        SERPER_API_KEY,
    )

logger = logging.getLogger(__name__)


# =============================================================================
# Helper Functions
# =============================================================================

def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )


def _safe_tag(tag: str) -> str:
    if not tag:
        return "item"
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", str(tag))
    if safe[0].isdigit():
        safe = "n_" + safe
    return safe


def _to_xml_element(name: str, value, indent: str = "") -> List[str]:
    lines: List[str] = []
    tag = _safe_tag(name)
    next_indent = indent + "  "
    if value is None:
        lines.append(f"{indent}<{tag} nil=\"true\"/>")
        return lines
    if isinstance(value, bool):
        val = "true" if value else "false"
        lines.append(f"{indent}<{tag}>{val}</{tag}>")
        return lines
    if isinstance(value, (int, float)):
        lines.append(f"{indent}<{tag}>{value}</{tag}>")
        return lines
    if isinstance(value, str):
        lines.append(f"{indent}<{tag}>{_xml_escape(value)}</{tag}>")
        return lines
    if isinstance(value, dict):
        lines.append(f"{indent}<{tag}>")
        for k, v in value.items():
            lines.extend(_to_xml_element(str(k), v, next_indent))
        lines.append(f"{indent}</{tag}>")
        return lines
    try:
        iterator = iter(value)
    except TypeError:
        lines.append(f"{indent}<{tag}>{_xml_escape(str(value))}</{tag}>")
        return lines
    else:
        lines.append(f"{indent}<{tag}>")
        for item in iterator:
            lines.extend(_to_xml_element("item", item, next_indent))
        lines.append(f"{indent}</{tag}>")
        return lines


def _to_xml(data, root_name: str = "root") -> str:
    root_tag = _safe_tag(root_name)
    out_lines = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>"]
    out_lines.extend(_to_xml_element(root_tag, data, ""))
    return "\n".join(out_lines) + "\n"


def normalize_url(url: str) -> str:
    """Normalize URL by removing tracking parameters and fragments."""
    if not url:
        return url
    # Remove common tracking parameters
    url = re.sub(r'[?&](utm_\w+|fbclid|gclid|ref)=[^&]*', '', url)
    # Remove trailing ? or &
    url = re.sub(r'[?&]$', '', url)
    return url


# =============================================================================
# Web Search Tool (using Serper.dev API)
# =============================================================================

class WebSearchTool:
    """
    Web search tool using Serper.dev Google Search API.
    """
    
    def __init__(self, api_key: str = None, max_results: int = 10):
        self.api_key = api_key or SERPER_API_KEY
        self.max_results = max_results
        self.endpoint = "https://google.serper.dev/search"
    
    def __call__(self, query: str) -> List[Dict[str, Any]]:
        """Execute search and return results."""
        if not self.api_key:
            logger.warning("SERPER_API_KEY not set, returning empty results")
            return []
        
        try:
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "q": query,
                "num": self.max_results
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("link", ""),
                    "summary": item.get("snippet", ""),
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []


# =============================================================================
# Web Page Reader Tool (using Jina AI Reader)
# =============================================================================

class WebPageReaderTool:
    """
    Web page reader tool using Jina AI Reader API.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or JINA_API_KEY
    
    def __call__(self, url: str) -> Dict[str, Any]:
        """Fetch and read webpage content."""
        try:
            jina_url = f'https://r.jina.ai/{url}'
            headers = {
                "Accept": "application/json",
                'X-Timeout': "60000",
                "X-With-Generated-Alt": "true",
            }
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            response = requests.get(jina_url, headers=headers, timeout=60)
            
            if response.status_code != 200:
                raise Exception(f"Jina AI Reader Failed for {url}: {response.status_code}")
            
            response_dict = response.json()
            
            return {
                'url': response_dict['data']['url'],
                'title': response_dict['data']['title'],
                'description': response_dict['data'].get('description', ''),
                'content': response_dict['data']['content'],
                'publish_time': response_dict['data'].get('publishedTime', 'unknown')
            }
        
        except Exception as e:
            logger.error(f"Failed to read webpage {url}: {e}")
            return {
                'url': url,
                'content': '',
                'error': str(e)
            }

# =============================================================================
# File System Tools
# =============================================================================

def _abs(root_dir: Path, rel: str) -> Path:
    """Resolve a path under root_dir."""
    p = (root_dir / rel).resolve()
    if not str(p).startswith(str(root_dir.resolve())):
        raise ValueError(f"path {rel!r} escapes root_dir")
    return p


def _read_lines(path: Path) -> List[str]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as f:
        return f.read().splitlines(keepends=True)


def _write_lines(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        f.write("".join(lines))


class FileTools:
    """File system tools for workspace operations."""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir).resolve()
        if not self.root_dir.exists():
            self.root_dir.mkdir(parents=True, exist_ok=True)

    def read_file(self, path: str, page: int = 1, page_size: int = 50) -> str:
        """Read paged lines from a file."""
        p = _abs(self.root_dir, path)
        lines = _read_lines(p)
        total = len(lines)
        total_pages = max(1, (total + page_size - 1) // page_size)
        page = max(1, min(page, total_pages))
        start = (page - 1) * page_size
        end = min(total, start + page_size)
        page_lines = "".join([f"{i+1} | {lines[i]}" for i in range(start, end)])
        return _to_xml({
            "lines": page_lines,
            "page": page,
            "total_pages": total_pages,
            "total_lines": total
        }, root_name="read_file")

    def insert_after(self, path: str, text: str, after_line: Optional[int] = None) -> str:
        """Insert lines after a given line (create file if missing)."""
        p = _abs(self.root_dir, path)
        lines = _read_lines(p)
        
        if after_line is None:
            idx = 0
        else:
            idx = max(0, min(len(lines), after_line))

        if isinstance(text, list):
            text = "".join(
                line if line.endswith(("\n", "\r")) else line + "\n"
                for line in text
            )

        added = text.splitlines(keepends=True)
        new_lines = lines[:idx] + added + lines[idx:]
        _write_lines(p, new_lines)
        return _to_xml({
            "applied_after_line": idx,
            "added_lines": len(added),
            "new_total_lines": len(new_lines),
        }, root_name="insert_after")

    def delete_lines(self, path: str, start_line: int, end_line: int) -> str:
        """Delete a range of lines."""
        p = _abs(self.root_dir, path)
        lines = _read_lines(p)
        if not lines:
            raise ValueError("file is empty or does not exist")

        n = len(lines)
        s = max(1, min(start_line, end_line))
        e = min(n, max(start_line, end_line))

        new_lines = lines[:s-1] + lines[e:]
        _write_lines(p, new_lines)
        return _to_xml({
            "deleted_start_line": s,
            "deleted_end_line": e,
            "deleted_lines": e - s + 1,
            "new_total_lines": len(new_lines),
        }, root_name="delete_lines")

    def replace_lines(self, path: str, text: str, start_line: int, end_line: int) -> str:
        """Replace a range of lines."""
        p = _abs(self.root_dir, path)
        lines = _read_lines(p)
        if not lines:
            raise ValueError("file is empty or does not exist")

        n = len(lines)
        s = max(1, min(start_line, end_line))
        e = min(n, max(start_line, end_line))

        added = text.splitlines(keepends=True)
        new_lines = lines[:s-1] + added + lines[e:]
        _write_lines(p, new_lines)
        return _to_xml({
            "replaced_start_line": s,
            "replaced_end_line": e,
            "delta_lines": len(added) - (e - s + 1),
            "new_total_lines": len(new_lines),
        }, root_name="replace_lines")

    def copy_to(self, src_path: str, src_start_line: int, src_end_line: int,
                dst_path: str, dst_at_line: Optional[int] = None,
                mode: str = "insert", dst_end_line: Optional[int] = None) -> str:
        """Copy lines from one file to another."""
        src = _abs(self.root_dir, src_path)
        dst = _abs(self.root_dir, dst_path)

        src_lines = _read_lines(src)
        if not src_lines:
            raise ValueError("source file is empty or does not exist")

        s = max(1, min(src_start_line, src_end_line))
        e = min(len(src_lines), max(src_start_line, src_end_line))
        block = src_lines[s-1:e]

        dst_lines = _read_lines(dst)

        if mode == "insert":
            if dst_at_line is None:
                idx = 0
            else:
                idx = max(0, min(len(dst_lines), dst_at_line - 1))
            new_lines = dst_lines[:idx] + block + dst_lines[idx:]
            _write_lines(dst, new_lines)
            return _to_xml({
                "mode": "insert",
                "inserted_at_line": idx + 1,
                "inserted_lines": len(block),
                "new_total_lines": len(new_lines),
            }, root_name="copy_to")

        if mode == "replace_range":
            if dst_at_line is None or dst_end_line is None:
                raise ValueError("dst_at_line and dst_end_line are required for replace_range")
            n2 = len(dst_lines)
            s2 = max(1, min(dst_at_line, dst_end_line))
            e2 = min(n2, max(dst_at_line, dst_end_line))

            new_lines = dst_lines[:s2-1] + block + dst_lines[e2:]
            _write_lines(dst, new_lines)
            return _to_xml({
                "mode": "replace_range",
                "replaced_start_line": s2,
                "replaced_end_line": e2,
                "inserted_lines": len(block),
                "new_total_lines": len(new_lines),
            }, root_name="copy_to")

        raise ValueError("invalid mode")

    def ls(self, path: Optional[str] = None, recursive: bool = False, 
           max_depth: int = 2, glob_pattern: Optional[str] = None,
           limit: Optional[int] = None) -> str:
        """List files and directories."""
        base = _abs(self.root_dir, path) if path else self.root_dir
        entries = []
        excluded_suffixes = ['.log']

        def add_file(f: Path):
            size = f.stat().st_size
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(f.stat().st_mtime))
            lines_count = None
            try:
                with f.open("r", encoding="utf-8") as fh:
                    lines_count = sum(1 for _ in fh)
            except Exception:
                pass
            entries.append({
                "type": "file",
                "path": str(f.relative_to(self.root_dir)),
                "size": size,
                "mtime": mtime,
                "lines": lines_count
            })

        def add_dir(d: Path):
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(d.stat().st_mtime))
            rel_path = str(d.relative_to(self.root_dir))
            if rel_path != "." and not rel_path.endswith("/"):
                rel_path += "/"
            entries.append({
                "type": "dir",
                "path": rel_path,
                "size": 0,
                "mtime": mtime,
                "lines": None
            })

        if not recursive:
            if not base.exists():
                return _to_xml({"entries": [], "total_entries": 0}, root_name="ls")
            for child in sorted(base.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):
                if child.is_dir():
                    add_dir(child)
                else:
                    if glob_pattern and not child.match(glob_pattern):
                        continue
                    name_l = child.name.lower()
                    if any(name_l.endswith(ext) for ext in excluded_suffixes):
                        continue
                    add_file(child)
        else:
            depth0 = len(base.resolve().parts)
            for root, dirs, files in os.walk(base):
                cur = Path(root)
                depth = len(cur.parts) - depth0
                if depth > max_depth:
                    dirs[:] = []
                    continue
                add_dir(cur)
                for fn in files:
                    f = cur / fn
                    if glob_pattern and not f.match(glob_pattern):
                        continue
                    name_l = f.name.lower()
                    if any(name_l.endswith(ext) for ext in excluded_suffixes):
                        continue
                    add_file(f)
                if limit is not None and len(entries) >= limit:
                    break

        trimmed_entries = entries[:limit] if limit else entries
        return _to_xml({"entries": trimmed_entries, "total_entries": len(entries)}, root_name="ls")

    def grep(self, keyword: str, path: str) -> str:
        """Run grep on a file or directory."""
        target = _abs(self.root_dir, path)

        if target.is_dir():
            cmd = ["grep", "-R", "-n", "-E", "--color=never", keyword, str(target)]
        else:
            cmd = ["grep", "-n", "-E", "--color=never", keyword, str(target)]

        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if proc.returncode == 1 and not proc.stderr:
                stdout = ""
                stderr = ""
            else:
                stdout = proc.stdout
                stderr = proc.stderr
        except FileNotFoundError:
            stdout = ""
            stderr = "grep command not found"
            returncode = 127
        else:
            returncode = proc.returncode

        return _to_xml(
            {
                "keyword": keyword,
                "path": str(target.relative_to(self.root_dir)),
                "returncode": returncode,
                "stdout": stdout,
                "stderr": stderr,
            },
            root_name="grep",
        )

    def file_search(self, path: str, query: str, regex: bool = False,
                    context: int = 60, max_results: int = 20, page: int = 1) -> str:
        """Search for text in a file."""
        import bisect
        
        p = _abs(self.root_dir, path)
        lines = _read_lines(p)
        text = "".join(lines)

        # Build line start offsets
        offs = [0]
        acc = 0
        for ch in text.splitlines(keepends=True):
            acc += len(ch)
            offs.append(acc)

        matches = []
        if regex:
            for m in re.finditer(query, text):
                start, end = m.span()
                li = bisect.bisect_right(offs, start) - 1
                col = start - offs[li]
                preview_start = max(0, start - context)
                preview_end = min(len(text), end + context)
                matches.append({
                    "index": len(matches) + 1,
                    "start_char": start,
                    "end_char": end,
                    "line": li + 1,
                    "col": col + 1,
                    "preview": text[preview_start:preview_end]
                })
        else:
            start = 0
            while True:
                idx = text.find(query, start)
                if idx == -1:
                    break
                end = idx + len(query)
                li = bisect.bisect_right(offs, idx) - 1
                col = idx - offs[li]
                preview_start = max(0, idx - context)
                preview_end = min(len(text), end + context)
                matches.append({
                    "index": len(matches) + 1,
                    "start_char": idx,
                    "end_char": end,
                    "line": li + 1,
                    "col": col + 1,
                    "preview": text[preview_start:preview_end]
                })
                start = idx + 1

        total_matches = len(matches)
        total_pages = max(1, (total_matches + max_results - 1) // max_results)
        page = max(1, min(page, total_pages))
        begin = (page - 1) * max_results
        end = min(total_matches, begin + max_results)

        return _to_xml({
            "matches": matches[begin:end],
            "page": page,
            "total_pages": total_pages,
            "total_matches": total_matches
        }, root_name="file_search")


# =============================================================================
# Tool Definitions for Agent
# =============================================================================

TOOL_DEFINITIONS_STAGE1 = [
    {
        "name": "search_web",
        "description": """Issues a query to a search engine and returns search results.
Use when: You need up-to-date facts, niche details, or information not in training data.
Rules:
1) Source Priority: Official/primary > top-tier publishers/academic > reputable industry > aggregators/blogs.
2) Freshness: Breaking/news ≤72h; product/docs/pricing ≤6–12 months.
3) Cross-check dates and definitions; never report predictions as facts.""",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query to execute."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "read_webpage",
        "description": """Fetches the content of a webpage (via Jina AI Reader).

Behavior:
- Returns webpage title + a chunk of content (paged by page_idx).
- Optionally archives the full raw content into ./knowledge_base/sources/ for later citation.

ALWAYS call this function when:
(1) More detailed information from a site would be helpful
(2) Following up on search_web results
(3) You need to preserve a source for later reference/citation""",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL of the webpage to fetch and read."
                },
                "page_idx": {
                    "type": "integer",
                    "description": "Optional page index for long webpages split into chunks. Default: 1."
                },
                "archive": {
                    "type": "boolean",
                    "description": "Whether to archive the raw source to ./knowledge_base/sources/. Default: true."
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "fs_read_file",
        "description": """Read paged lines from a file under the workspace root.
Use for: previewing files, paginating large files, quick inspections.
Returns line objects with 1-based numbers, current page, and totals.""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Workspace-relative file path, e.g., 'src/app.py'."
                },
                "page": {
                    "type": "integer",
                    "description": "1-based page index. Default: 1."
                },
                "page_size": {
                    "type": "integer",
                    "description": "Lines per page (1..10000). Default: 50."
                }
            },
            "required": ["path"]
        }
    },
    {
        "name": "fs_insert_after",
        "description": """Insert lines into a file, creating it if missing.
Use for: adding content immediately after a specific line number.
Read the file every time before calling this tool.""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Target file path (workspace-relative)."
                },
                "text": {
                    "type": "string",
                    "description": "Text snippet to insert."
                },
                "after_line": {
                    "type": "integer",
                    "description": "Insert after this 1-based line number. Default: top when omitted."
                }
            },
            "required": ["path", "text"]
        }
    },
    {
        "name": "fs_delete_lines",
        "description": """Delete a continuous range of lines from a file.
Read the file every time before calling this tool.""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Target file path (workspace-relative)."
                },
                "start_line": {
                    "type": "integer",
                    "description": "Start line (1-based)."
                },
                "end_line": {
                    "type": "integer",
                    "description": "End line (1-based)."
                }
            },
            "required": ["path", "start_line", "end_line"]
        }
    },
    {
        "name": "fs_replace_lines",
        "description": """Replace a range of lines in a file with new content.
Read the file every time before calling this tool.""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Target file path (workspace-relative)."
                },
                "text": {
                    "type": "string",
                    "description": "Replacement text."
                },
                "start_line": {
                    "type": "integer",
                    "description": "Start line (1-based)."
                },
                "end_line": {
                    "type": "integer",
                    "description": "End line (1-based)."
                }
            },
            "required": ["path", "text", "start_line", "end_line"]
        }
    },
    {
        "name": "fs_copy_to",
        "description": """Copy a block of lines from one file to another.
Use for: duplicating code blocks, templating, or moving snippets across files.""",
        "parameters": {
            "type": "object",
            "properties": {
                "src_path": {"type": "string", "description": "Source file path (workspace-relative)."},
                "src_start_line": {"type": "integer", "description": "1-based start line in source."},
                "src_end_line": {"type": "integer", "description": "1-based end line in source."},
                "dst_path": {"type": "string", "description": "Destination file path (workspace-relative)."},
                "dst_at_line": {"type": "integer", "description": "Insert before this destination line. Default: top when omitted."},
                "mode": {"type": "string", "description": "\"insert\" or \"replace_range\". Default: insert."},
                "dst_end_line": {"type": "integer", "description": "End line for replace_range (when mode=\"replace_range\")."},
            },
            "required": ["src_path", "src_start_line", "src_end_line", "dst_path"]
        }
    },
    {
        "name": "fs_ls",
        "description": """List files and directories under a workspace path with basic metadata.
Use for: discovering project structure, quick file inventory.""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path (workspace-relative). Default: root."
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Recurse into subdirectories. Default: false."
                },
                "max_depth": {
                    "type": "integer",
                    "description": "Max recursion depth. Default: 2."
                }
            },
            "required": []
        }
    },
    {
        "name": "fs_grep",
        "description": """Run a grep command under the workspace root.
Use for: fast text search with regular expression support.""",
        "parameters": {
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "Search pattern, supports extended regular expressions."
                },
                "path": {
                    "type": "string",
                    "description": "File or directory path (workspace-relative)."
                }
            },
            "required": ["keyword", "path"]
        }
    }
    ,
    {
        "name": "fs_file_search",
        "description": """Search for a string or regex in a file and return match contexts.
Use for: locating occurrences with surrounding preview text.""",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "File path (workspace-relative)."},
                "query": {"type": "string", "description": "Search string or regex pattern."},
                "regex": {"type": "boolean", "description": "Treat query as regex. Default: false."},
                "context": {"type": "integer", "description": "Chars around each match in preview. Default: 60."},
                "max_results": {"type": "integer", "description": "Max results per page. Default: 20."},
                "page": {"type": "integer", "description": "1-based page index. Default: 1."}
            },
            "required": ["path", "query"]
        }
    },
]

# Stage 2 tools (without search/read_webpage)
TOOL_DEFINITIONS_STAGE2 = [t for t in TOOL_DEFINITIONS_STAGE1 
                           if t["name"] not in ["search_web", "read_webpage"]]

