"""Allow running the MCP server as a module: python -m metricduck_mcp"""

from .server import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
