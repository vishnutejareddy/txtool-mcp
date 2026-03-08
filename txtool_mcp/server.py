"""txtool MCP server — exposes txtool text processing tools via FastMCP."""

from fastmcp import FastMCP

from txtool.core import search, replace, stats, filter, transform, extract, fileops, data, logtools, misc
from txtool.utils import resolve_files
from pathlib import Path

mcp = FastMCP(
    "txtool",
    instructions="Text processing tools for search, replace, transform, data formats, and more",
)


# ---------------------------------------------------------------------------
# Search / Replace
# ---------------------------------------------------------------------------

@mcp.tool()
def search_in_files(pattern: str, path: str, ignore_case: bool = False, line_numbers: bool = False) -> str:
    """Search for a regex pattern in a file or directory. Returns matching lines."""
    paths = resolve_files([path])
    if not paths:
        return "No files found."
    results = search.search(pattern, paths, ignore_case=ignore_case)
    if not results:
        return "No matches found."
    lines = []
    for r in results:
        prefix = f"{r['file']}:{r['line_number']}: " if line_numbers else f"{r['file']}: "
        lines.append(prefix + r["line"])
    return "\n".join(lines)


@mcp.tool()
def replace_in_file(pattern: str, replacement: str, path: str, dry_run: bool = True) -> str:
    """Find and replace in a file. dry_run=True shows diff without writing."""
    paths = resolve_files([path])
    if not paths:
        return "No files found."
    results = replace.replace(pattern, replacement, paths)
    output = []
    for r in results:
        if not r["changed"]:
            output.append(f"{r['file']}: no changes")
            continue
        diff_lines = []
        for old, new in zip(r["old_lines"], r["new_lines"]):
            if old != new:
                diff_lines.append(f"  - {old.rstrip()}")
                diff_lines.append(f"  + {new.rstrip()}")
        if not dry_run:
            replace.apply_replace(r)
            output.append(f"{r['file']}: updated\n" + "\n".join(diff_lines))
        else:
            output.append(f"{r['file']}: would change\n" + "\n".join(diff_lines))
    return "\n".join(output)


@mcp.tool()
def file_stats(path: str, top_words: int = 10) -> str:
    """Get line/word/char counts and top words for a file or directory."""
    paths = resolve_files([path])
    if not paths:
        return "No files found."
    results = stats.compute_stats(paths, top=top_words)
    lines = []
    for r in results:
        lines.append(f"File: {r['file']}")
        lines.append(f"  Lines: {r['lines']}, Words: {r['words']}, Chars: {r['chars']}")
        if r["top_words"]:
            lines.append(f"  Top words: " + ", ".join(f"{w}({c})" for w, c in r["top_words"]))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Transform
# ---------------------------------------------------------------------------

@mcp.tool()
def transform_text(text: str, trim: bool = False, wrap: int = None, indent: int = None) -> str:
    """Format text: trim whitespace, wrap lines, add indentation."""
    return transform.fmt_text(text, trim=trim, wrap=wrap, indent=indent)


@mcp.tool()
def convert_case(text: str, style: str) -> str:
    """Convert case. style: snake, camel, pascal, kebab, upper, lower, title"""
    return transform.convert_case(text, style)


@mcp.tool()
def sort_text(text: str, numeric: bool = False, reverse: bool = False, unique: bool = False) -> str:
    """Sort lines in text."""
    return transform.sort_lines(text, numeric=numeric, reverse=reverse, unique=unique)


@mcp.tool()
def dedup_text(text: str) -> str:
    """Remove duplicate lines from text, preserving order."""
    return transform.dedup_lines(text)


@mcp.tool()
def truncate_text(text: str, head: int = None, tail: int = None) -> str:
    """Keep first (head) or last (tail) N lines of text."""
    return transform.truncate_lines(text, head=head, tail=tail)


# ---------------------------------------------------------------------------
# Extract
# ---------------------------------------------------------------------------

@mcp.tool()
def extract_from_text(text: str, extract_type: str = None, unique: bool = False) -> str:
    """Extract emails, urls, ips, dates, phones, or numbers from text.

    extract_type: one of email, url, ip, date, phone, number (or None for all)
    """
    types = [extract_type] if extract_type else None
    results = extract.extract_patterns(text, types=types, unique=unique)
    if not results:
        return "No matches found."
    multi = len(set(r["type"] for r in results)) > 1
    lines = []
    for r in results:
        if multi:
            lines.append(f"{r['type']}: {r['value']}")
        else:
            lines.append(r["value"])
    return "\n".join(lines)


@mcp.tool()
def extract_between_markers(text: str, start: str, end: str, inclusive: bool = False) -> str:
    """Extract lines between start and end pattern matches."""
    return extract.extract_between(text, start, end, inclusive=inclusive)


# ---------------------------------------------------------------------------
# File Operations
# ---------------------------------------------------------------------------

@mcp.tool()
def diff_files(file1: str, file2: str, level: str = "line") -> str:
    """Compare two files. level: line, word, or char."""
    result = fileops.diff_files(file1, file2, level=level)
    return result if result else "No differences."


@mcp.tool()
def set_ops(file1: str, file2: str, mode: str = "all") -> str:
    """Set operations on file lines. mode: only_a, only_b, common, or all."""
    ops = fileops.set_operations(file1, file2)
    if mode == "only_a":
        return "\n".join(ops["only_a"]) or "(empty)"
    elif mode == "only_b":
        return "\n".join(ops["only_b"]) or "(empty)"
    elif mode == "common":
        return "\n".join(ops["common"]) or "(empty)"
    else:
        parts = []
        if ops["only_a"]:
            parts.append("Only in file1:\n" + "\n".join(f"  {l}" for l in ops["only_a"]))
        if ops["only_b"]:
            parts.append("Only in file2:\n" + "\n".join(f"  {l}" for l in ops["only_b"]))
        if ops["common"]:
            parts.append("Common:\n" + "\n".join(f"  {l}" for l in ops["common"]))
        return "\n".join(parts) or "No differences."


# ---------------------------------------------------------------------------
# Data Formats
# ---------------------------------------------------------------------------

@mcp.tool()
def pretty_json(text: str) -> str:
    """Pretty-print JSON text."""
    return data.json_pretty(text)


@mcp.tool()
def minify_json(text: str) -> str:
    """Minify JSON text."""
    return data.json_minify(text)


@mcp.tool()
def validate_json(text: str) -> str:
    """Validate JSON. Returns 'Valid' or error message."""
    valid, error = data.json_validate(text)
    return "Valid" if valid else f"Invalid: {error}"


@mcp.tool()
def get_json_value(text: str, path: str) -> str:
    """Extract a value from JSON using dot-notation path like 'users[0].name'."""
    return data.json_get(text, path)


@mcp.tool()
def view_csv(text: str, delimiter: str = ",") -> str:
    """Render CSV as an aligned text table."""
    rows = data.csv_to_table(text, delimiter=delimiter)
    if not rows:
        return "(empty)"
    headers = list(rows[0].keys())
    col_widths = {h: len(h) for h in headers}
    for row in rows:
        for h in headers:
            col_widths[h] = max(col_widths[h], len(str(row.get(h, ""))))
    sep = "+-" + "-+-".join("-" * col_widths[h] for h in headers) + "-+"
    header_row = "| " + " | ".join(h.ljust(col_widths[h]) for h in headers) + " |"
    lines = [sep, header_row, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")).ljust(col_widths[h]) for h in headers) + " |")
    lines.append(sep)
    return "\n".join(lines)


@mcp.tool()
def filter_csv(text: str, condition: str, delimiter: str = ",") -> str:
    """Filter CSV rows by condition e.g. 'status=active' or 'age>30'."""
    return data.csv_filter(text, condition, delimiter=delimiter)


@mcp.tool()
def parse_env_file(text: str) -> str:
    """Parse and display a .env file as a key/value table."""
    env = data.parse_env(text)
    if not env:
        return "(empty)"
    max_key = max(len(k) for k in env)
    lines = []
    for k, v in sorted(env.items()):
        lines.append(f"{k.ljust(max_key)} = {v}")
    return "\n".join(lines)


@mcp.tool()
def apply_template(text: str, variables: str) -> str:
    """Replace {{VAR}} placeholders. variables: 'KEY=val KEY2=val2'"""
    return data.render_template(text, variables)


# ---------------------------------------------------------------------------
# Log Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def parse_log_file(path: str) -> str:
    """Parse log file: count levels (DEBUG/INFO/WARN/ERROR), show top errors."""
    paths = resolve_files([path])
    if not paths:
        return "No files found."
    results = logtools.parse_log_levels(paths)
    lines = []
    for r in results:
        lines.append(f"File: {r['file']}")
        lines.append(f"  Total lines: {r['total']}")
        for level, count in sorted(r["counts"].items()):
            lines.append(f"  {level}: {count}")
        if r["top_errors"]:
            lines.append("  Top errors:")
            for msg in r["top_errors"]:
                lines.append(f"    {msg}")
    return "\n".join(lines)


@mcp.tool()
def tail_file(path: str, n: int = 10) -> str:
    """Show last N lines of a file."""
    lines = logtools.tail_lines(path, n)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

@mcp.tool()
def encode_decode(text: str, method: str, decode: bool = False) -> str:
    """Encode or decode text. method: base64, url, html"""
    return misc.encode_text(text, method, decode=decode)


@mcp.tool()
def hash_file_content(path: str, algo: str = "sha256") -> str:
    """Compute hash of a file. algo: md5, sha1, sha256, sha512"""
    digest = misc.hash_file(path, algo)
    return f"{algo}: {digest}"


@mcp.tool()
def word_count(path: str) -> str:
    """Get line/word/char counts for a file or directory."""
    paths = resolve_files([path])
    if not paths:
        return "No files found."
    results = misc.word_count(paths)
    lines = []
    for r in results:
        lines.append(f"{r['file']}: {r['lines']} lines, {r['words']} words, {r['chars']} chars")
    return "\n".join(lines)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
