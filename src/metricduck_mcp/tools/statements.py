"""Financial statement tools for income statement, balance sheet, and cash flow"""

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


def get_statement_tools() -> list[Tool]:
    """
    Get list of financial statement tools

    Returns:
        List of MCP Tool definitions for financial statements
    """
    # Get annotations if supported
    annotations = _get_annotations(read_only=True)

    # Common input schema for all statement tools
    common_schema = {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Company ticker symbol (e.g., 'AAPL', 'MSFT'). Must be exact."
            },
            "period": {
                "type": "string",
                "enum": ["quarterly", "annual"],
                "default": "quarterly",
                "description": "Time period granularity. Quarterly shows 8 quarters, Annual shows 5 years."
            },
            "years": {
                "type": "integer",
                "minimum": 1,
                "maximum": 5,
                "default": 2,
                "description": "Number of years of history (default 2 = 8 quarters, max 5 years)"
            }
        },
        "required": ["ticker"]
    }

    # Build tool kwargs
    income_statement_kwargs = {
        "name": "get_income_statement",
        "description": """
Get multi-period income statement data for detailed revenue and profitability analysis.

Perfect for:
- Revenue trend analysis over time
- Margin expansion or contraction tracking
- Profitability assessment and earnings quality
- Quarter-over-quarter and year-over-year comparisons
- Understanding the P&L story

Returns historical income statement data with key metrics:
- **Top Line**: Revenue (total sales)
- **Costs**: Cost of Revenue (COGS), Operating Expenses
- **Profitability**: Gross Profit, Operating Income (EBIT), Net Income
- **Per-Share**: EPS (Basic and Diluted)
- **Margins**: Gross Margin %, Operating Margin %, Net Margin %

Data Format:
- Quarterly: Returns 8 quarters (2 years) showing seasonal patterns
- Annual: Returns 5 years showing long-term trends

Example Queries:
- "Show me Apple's revenue growth over the last 8 quarters"
- "What's the trend in Tesla's operating margin?"
- "Compare Microsoft's quarterly earnings to last year"
- "Has Amazon's profitability improved recently?"

Note: All metrics are from XBRL filings, calculated using industry-standard formulas.
            """.strip(),
        "inputSchema": common_schema
    }

    balance_sheet_kwargs = {
        "name": "get_balance_sheet",
        "description": """
Get multi-period balance sheet data for financial position and solvency analysis.

Perfect for:
- Asset quality and composition assessment
- Debt and leverage analysis
- Liquidity and working capital trends
- Equity and shareholder value tracking
- Capital structure evaluation

Returns historical balance sheet data with key metrics:
- **Assets**: Total Assets, Current Assets, Cash & Equivalents, Inventory, PP&E
- **Liabilities**: Total Liabilities, Current Liabilities, Total Debt, Accounts Payable
- **Equity**: Total Equity, Retained Earnings, Treasury Stock
- **Ratios**: Current Ratio, Quick Ratio, Debt/Equity, Debt/Assets

Data Format:
- Quarterly: Returns 8 quarters (point-in-time snapshots at quarter-end)
- Annual: Returns 5 years (year-end snapshots)

Example Queries:
- "What's Apple's cash position over time?"
- "Is Tesla taking on more debt?"
- "How liquid is Microsoft's balance sheet?"
- "What's the trend in Amazon's working capital?"
- "Show me Netflix's debt-to-equity ratio history"

Note: Balance sheet items are point-in-time (snapshot at period end), not period-over-period flows.
            """.strip(),
        "inputSchema": common_schema
    }

    cash_flow_kwargs = {
        "name": "get_cash_flow",
        "description": """
Get multi-period cash flow statement data for cash generation and capital allocation analysis.

Perfect for:
- Cash generation quality assessment
- Free cash flow trends and sustainability
- Capital expenditure (CapEx) analysis
- Dividend and buyback capacity evaluation
- Cash burn rate for growth companies

Returns historical cash flow data with key metrics:
- **Operating Activities**: Operating Cash Flow (OCF), Changes in Working Capital
- **Investing Activities**: Capital Expenditures (CapEx), Acquisitions, Asset Sales
- **Financing Activities**: Debt Issuance/Repayment, Dividends, Stock Buybacks
- **Key Derived**: Free Cash Flow (OCF - CapEx), FCF Margin %, Cash Conversion

Data Format:
- Quarterly: Returns 8 quarters showing seasonal cash patterns
- Annual: Returns 5 years showing long-term cash trends

Example Queries:
- "What's Apple's free cash flow trend?"
- "Is Tesla burning cash or generating cash?"
- "How much does Microsoft spend on CapEx?"
- "What's Amazon's operating cash flow conversion?"
- "Show me Netflix's cash flow history"

Note: Cash flow shows actual cash movements (not accrual-based), critical for assessing financial health.
            """.strip(),
        "inputSchema": common_schema
    }

    # Add annotations if supported
    if annotations is not None:
        income_statement_kwargs["annotations"] = annotations
        balance_sheet_kwargs["annotations"] = annotations
        cash_flow_kwargs["annotations"] = annotations

    # Add titles for better display in MCP clients
    income_statement_kwargs["title"] = "Income Statement"
    balance_sheet_kwargs["title"] = "Balance Sheet"
    cash_flow_kwargs["title"] = "Cash Flow Statement"

    return [
        Tool(**income_statement_kwargs),
        Tool(**balance_sheet_kwargs),
        Tool(**cash_flow_kwargs)
    ]
