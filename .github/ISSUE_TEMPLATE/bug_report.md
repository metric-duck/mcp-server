---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

<!-- A clear and concise description of what the bug is -->

## Steps to Reproduce

1.
2.
3.

## Expected Behavior

<!-- What you expected to happen -->

## Actual Behavior

<!-- What actually happened -->

## Environment

- **OS:** [e.g., Windows 11, macOS 14, Ubuntu 22.04]
- **Python Version:** [e.g., 3.10.5]
- **MCP Server Version:** [e.g., 0.3.0]
- **AI Client:** [e.g., Claude Desktop 1.2.3, Cursor, Windsurf]
- **Installation Method:** [PyPI or GitHub]

## Configuration

<!-- Share relevant parts of your MCP configuration (remove sensitive tokens!) -->

```json
{
  "mcpServers": {
    "metricduck": {
      "command": "python",
      "args": ["-m", "metricduck_mcp"],
      "env": {
        "METRICDUCK_MCP_API_BASE_URL": "https://api.metricduck.com",
        "METRICDUCK_MCP_ACCESS_TOKEN": "[REDACTED]"
      }
    }
  }
}
```

## Error Messages / Logs

<!-- Paste any error messages or relevant log output -->

```
Paste error messages here
```

## Additional Context

<!-- Add any other context about the problem here -->

## Possible Solution

<!-- If you have suggestions on how to fix the bug, share them here -->
