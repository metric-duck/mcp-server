"""Company search and information tools"""

from mcp.types import Tool

try:
    from mcp.types import ToolAnnotations
except ImportError:
    # Fallback for older MCP versions that don't support annotations
    ToolAnnotations = None


def _get_annotations(read_only: bool = True):
    """Helper to create tool annotations if supported"""
    if ToolAnnotations is None:
        return None
    return ToolAnnotations(
        readOnlyHint=read_only,
        idempotentHint=read_only  # Read-only operations are idempotent
    )


def get_company_tools() -> list[Tool]:
    """
    Get list of company-related tools

    Returns:
        List of MCP Tool definitions
    """
    # Build tool kwargs with annotations if supported
    search_tool_kwargs = {
        "name": "search_companies",
        "description": """
Search for companies by name or ticker with intelligent fuzzy matching.

This tool helps you find companies even with:
- Partial names (e.g., "micro" → Microsoft)
- Typos (e.g., "aplle" → Apple)
- Common variations (e.g., "faceb look" → Meta Platforms, "FB" → Meta)
- Case insensitivity

Examples:
- "apple" → AAPL (Apple Inc.)
- "micro soft" → MSFT (Microsoft Corporation)
- "tsla" → TSLA (Tesla, Inc.)
- "costco" → COST (Costco Wholesale Corporation)
- "berk hire" → BRK.A, BRK.B (Berkshire Hathaway)

Returns: List of matching companies with ticker, full name, CIK, and business description.
Best for: Initial exploration, finding the right ticker, disambiguating similar names.
            """.strip(),
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Company name or ticker (supports partial matches and typos)"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return (default: 5, max: 20)",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": ["query"]
        }
    }

    # Add annotations if supported
    annotations = _get_annotations(read_only=True)
    if annotations is not None:
        search_tool_kwargs["annotations"] = annotations

    # Add title for better display in MCP clients
    search_tool_kwargs["title"] = "Search Companies"

    # Build overview tool
    overview_tool_kwargs = {
        "name": "get_company_overview",
        "description": """
Get comprehensive financial overview for a specific company.

Provides key metrics across valuation, profitability, cash flow, and balance sheet.
Perfect for quick company analysis or answering specific questions about financial health.

Data Included:
- Valuation: P/E, P/B, EV/Sales, EV/FCF, Market Cap, Enterprise Value (TTM)
- Profitability: Revenue, Net Income, EPS, Margins (Gross, Operating, Net, FCF), ROE, ROA, ROIC (TTM)
- Cash Flow: Operating Cash Flow, Free Cash Flow (TTM)
- Balance Sheet: Total Debt, Cash & Investments, Shares Outstanding, Debt Ratios (Most Recent Quarter)
- Trends: 8-quarter history for Revenue, Net Income, Free Cash Flow

Use Cases:
- "What is Apple's P/E ratio?" → get_company_overview("AAPL")
- "How profitable is Microsoft?" → get_company_overview("MSFT") [check margins, ROE, ROIC]
- "Show me Tesla's financial health" → get_company_overview("TSLA")
- "Compare Costco's valuation to Walmart" → get both overviews, compare P/E, EV/Sales

Note: Requires exact ticker symbol. Use search_companies first if unsure.
            """.strip(),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company ticker symbol (e.g., 'AAPL', 'MSFT', 'GOOGL'). Must be exact."
                }
            },
            "required": ["ticker"]
        }
    }

    # Add annotations if supported
    if annotations is not None:
        overview_tool_kwargs["annotations"] = annotations

    # Add title for better display in MCP clients
    overview_tool_kwargs["title"] = "Company Overview"

    # Return tools
    return [
        Tool(**search_tool_kwargs),
        Tool(**overview_tool_kwargs)
    ]
