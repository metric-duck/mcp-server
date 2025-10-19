"""
MetricDuck MCP Server

Main entry point for the Model Context Protocol server.
Registers tools and handles requests from AI clients like Claude Code.
"""

import asyncio
import logging
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from .config import get_settings
from .handlers import CompaniesHandler, StatementsHandler
from .tools.companies import get_company_tools
from .tools.statements import get_statement_tools


logger = logging.getLogger(__name__)


class MetricDuckMCPServer:
    """MetricDuck MCP Server coordinating all tools and handlers"""

    def __init__(self):
        """Initialize server with configuration"""
        self.settings = get_settings()
        self.server = Server("metricduck-mcp")

        # Initialize handlers
        self.companies_handler = CompaniesHandler(self.settings)
        self.statements_handler = StatementsHandler(self.settings)

        logger.info("MetricDuck MCP Server initialized")
        logger.info(f"API Base URL: {self.settings.api_base_url}")

    def register_tools(self):
        """Register all MCP tools"""

        # Get all tools
        company_tools = get_company_tools()
        statement_tools = get_statement_tools()
        all_tools = company_tools + statement_tools

        @self.server.list_tools()
        async def list_tools():
            """List all available tools"""
            logger.debug("Listing available tools")
            return all_tools

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict):
            """
            Handle tool invocations

            Routes tool calls to appropriate handlers based on tool name.
            """
            logger.info(f"Tool called: {name} with arguments: {arguments}")

            try:
                # Route to appropriate handler
                if name == "search_companies":
                    result = await self.companies_handler.search_companies(
                        query=arguments["query"],
                        limit=arguments.get("limit", 5)
                    )
                    return [TextContent(type="text", text=result)]

                elif name == "get_company_overview":
                    result = await self.companies_handler.get_company_overview(
                        ticker=arguments["ticker"]
                    )
                    return [TextContent(type="text", text=result)]

                elif name == "get_income_statement":
                    result = await self.statements_handler.get_income_statement(
                        ticker=arguments["ticker"],
                        period=arguments.get("period", "quarterly"),
                        years=arguments.get("years", 2)
                    )
                    return [TextContent(type="text", text=result)]

                elif name == "get_balance_sheet":
                    result = await self.statements_handler.get_balance_sheet(
                        ticker=arguments["ticker"],
                        period=arguments.get("period", "quarterly"),
                        years=arguments.get("years", 2)
                    )
                    return [TextContent(type="text", text=result)]

                elif name == "get_cash_flow":
                    result = await self.statements_handler.get_cash_flow(
                        ticker=arguments["ticker"],
                        period=arguments.get("period", "quarterly"),
                        years=arguments.get("years", 2)
                    )
                    return [TextContent(type="text", text=result)]

                else:
                    error_msg = f"Unknown tool: {name}"
                    logger.error(error_msg)
                    return [TextContent(type="text", text=f"❌ {error_msg}")]

            except Exception as e:
                error_msg = f"Error executing tool '{name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [TextContent(type="text", text=f"❌ {error_msg}")]

        logger.info(f"Registered {len(all_tools)} tools ({len(company_tools)} company + {len(statement_tools)} statement)")

    async def run(self):
        """Run the MCP server using stdio transport"""
        logger.info("Starting MetricDuck MCP Server...")

        # Register all tools
        self.register_tools()

        # Run server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server running on stdio")
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

    async def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        await self.companies_handler.close()
        await self.statements_handler.close()
        logger.info("Cleanup complete")


async def main():
    """Main entry point"""
    server = MetricDuckMCPServer()

    try:
        await server.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        await server.cleanup()


if __name__ == "__main__":
    # Run the server
    asyncio.run(main())
