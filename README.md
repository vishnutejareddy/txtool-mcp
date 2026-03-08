# txtool-mcp

MCP server exposing [txtool](https://pypi.org/project/txtlvit/) text processing capabilities as tools for Claude and other MCP-compatible agents.

## Prerequisites

Install `uv` (if not already):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

No separate install step needed — `uvx` fetches and runs `txtool-mcp` automatically.

## Setup

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "txtool": {
      "command": "uvx",
      "args": ["txtool-mcp"]
    }
  }
}
```

Restart Claude Desktop — txtool tools will appear automatically.

### Claude Code (CLI)

**Option 1 — CLI command (recommended):**

```bash
claude mcp add txtool -s user -- uvx txtool-mcp
```

**Option 2 — Manual config:**

Add to `~/.claude.json`:

```json
{
  "mcpServers": {
    "txtool": {
      "command": "uvx",
      "args": ["txtool-mcp"]
    }
  }
}
```

Restart Claude Code — txtool tools will appear automatically.

### Other MCP-compatible tools (Kiro, etc.)

Refer to your tool's documentation for how to register MCP servers. Use `uvx txtool-mcp` as the server command.

## Available Tools

| Tool | Description |
|------|-------------|
| `search_in_files` | Search for a regex pattern in a file or directory |
| `replace_in_file` | Find and replace in a file (with dry-run diff) |
| `file_stats` | Line/word/char counts and top words |
| `transform_text` | Trim, wrap, indent text |
| `convert_case` | snake, camel, pascal, kebab, upper, lower, title |
| `sort_text` | Sort lines (alpha, numeric, reverse, unique) |
| `dedup_text` | Remove duplicate lines |
| `truncate_text` | Keep first/last N lines |
| `extract_from_text` | Extract emails, URLs, IPs, dates, phones, numbers |
| `extract_between_markers` | Extract lines between start/end patterns |
| `diff_files` | Compare two files (line/word/char level) |
| `set_ops` | Set operations on file lines (only_a, only_b, common) |
| `pretty_json` | Pretty-print JSON |
| `minify_json` | Minify JSON |
| `validate_json` | Validate JSON |
| `get_json_value` | Extract value by dot-notation path |
| `view_csv` | Render CSV as aligned table |
| `filter_csv` | Filter CSV rows by condition |
| `parse_env_file` | Parse .env file as key/value table |
| `apply_template` | Replace {{VAR}} placeholders |
| `parse_log_file` | Count log levels, show top errors |
| `tail_file` | Show last N lines of a file |
| `encode_decode` | Encode/decode base64, URL, HTML |
| `hash_file_content` | Compute file hash (md5, sha1, sha256, sha512) |
| `word_count` | Line/word/char counts for file or directory |

## Example Prompts

- "Search for all TODO comments in my project"
- "Replace all occurrences of 'foo' with 'bar' in this file — show me a diff first"
- "Pretty print this JSON and extract the users[0].email value"
- "Parse this log file and summarize the errors"
- "Convert this text to snake_case"
