"""DCF (Discounted Cash Flow) valuation tools"""

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


def get_dcf_tools() -> list[Tool]:
    """
    Get list of DCF valuation tools

    Returns:
        List of MCP Tool definitions for DCF analysis
    """
    # Get annotations if supported
    annotations = _get_annotations(read_only=True)

    # Tool 1: Get DCF Inputs
    dcf_inputs_kwargs = {
        "name": "get_dcf_inputs",
        "description": """
Get all data needed for DCF (Discounted Cash Flow) valuation analysis.

Perfect for:
- Inspecting historical Free Cash Flow trends before running DCF
- Comparing assumptions across multiple companies
- Reviewing estimated WACC and its components
- Validating data quality before valuation

Returns comprehensive DCF inputs:
- **Historical FCF**: 2-10 years of Free Cash Flow data
- **Growth Rate**: Calculated FCF CAGR (compound annual growth rate)
- **Balance Sheet**: Latest debt, cash, equity, shares outstanding
- **Estimated WACC**: Industry-average based WACC with full component breakdown
- **Tax Rate**: Industry-average effective tax rate by sector (Damodaran data)

WACC Estimation Methodology (Simplified for Transparency):
- **Beta**: Industry-average by 11-sector classification (not company-specific)
- **Risk-Free Rate**: 10-Year US Treasury from FRED API (updated weekly)
- **Cost of Equity**: Risk-Free Rate + Beta × Market Risk Premium (7%)
- **Cost of Debt**: Risk-Free Rate + 3% spread (simplified)
- **Tax Rate**: Industry-average by sector (TECH: 18%, FIN: 21%, etc.)
- **Weights**: Based on market value of equity and debt

**Important**: These estimates use industry averages for simplicity and speed. For precise
valuations, calculate your own WACC using company-specific data and current market conditions.

Use Cases:
- "Show me the DCF inputs for Apple" → Inspect all assumptions before running DCF
- "Compare FCF growth between Apple and Microsoft" → Get inputs for both, compare growth rates
- "What's Tesla's estimated WACC?" → Quick WACC estimate for back-of-envelope valuation

Next Step: Use `calculate_dcf` with your chosen WACC to get intrinsic value.
            """.strip(),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company ticker symbol (e.g., 'AAPL', 'MSFT'). Must be exact."
                },
                "years": {
                    "type": "integer",
                    "minimum": 2,
                    "maximum": 10,
                    "default": 5,
                    "description": "Years of historical FCF data to retrieve (2-10, default 5)"
                }
            },
            "required": ["ticker"]
        }
    }

    # Tool 2: Calculate DCF
    calculate_dcf_kwargs = {
        "name": "calculate_dcf",
        "description": """
Run full DCF (Discounted Cash Flow) valuation to estimate intrinsic value per share.

⚠️ **FOR SINGLE COMPANIES ONLY**
- User asks for DCF on ONE specific company → Use this tool
- User asks for multiple companies → Use `batch_dcf` instead
- User asks to "find undervalued stocks" → Use `scan_opportunities` instead

Perfect for:
- Estimating fair value of ONE company's stock
- Deep-dive valuation analysis on a specific ticker
- Scenario analysis with different WACC assumptions
- Understanding valuation sensitivity to key assumptions

DCF Methodology:
1. Project future Free Cash Flows (FCF) using historical growth rate
2. Discount projected FCF to present value using WACC
3. Calculate Terminal Value using perpetuity growth model
4. Discount Terminal Value to present value
5. Sum PV of FCF + PV of Terminal Value = Enterprise Value
6. Subtract Net Debt = Equity Value
7. Divide by Shares Outstanding = Intrinsic Value Per Share

Returns:
- **Intrinsic Value Per Share**: Fair value estimate
- **Equity Value**: Total company equity value
- **Enterprise Value**: Total company value (equity + debt)
- **Projected FCF**: Year-by-year cash flow projections
- **Sensitivity Analysis**: 3x3 grid showing valuation at different WACC/growth rates
- **All Assumptions**: Full transparency on inputs used

Required Parameter:
- `wacc`: Weighted Average Cost of Capital (e.g., 0.08 for 8%)
  - Typical range: 7-12% for most companies
  - Use `get_dcf_inputs` to see estimated WACC
  - Or calculate your own using market data

Optional Parameters:
- `terminal_growth_rate`: Perpetual growth rate (default 2.5%, must be < WACC)
  - Typical range: 2-3% (GDP growth rate)
  - Higher growth = higher valuation
- `projection_years`: Years to project (default 5, range 1-10)
  - More years = more weight on near-term cash flows

Interpretation:
- Intrinsic Value > Current Price → **Trading below estimated fair value**
- Intrinsic Value < Current Price → **Trading above estimated fair value**
- Sensitivity table shows how valuation changes across different assumptions
- Use DCF as one data point among many for investment analysis

Use Cases:
- "Run DCF on Apple with 8% WACC" → Quick fair value estimate
- "What's Tesla's intrinsic value assuming 10% WACC and 3% terminal growth?" → Custom assumptions
- "Compare fair value of Costco vs Walmart" → Run DCF on both, compare results

⚠️ Important Disclaimer:
DCF is highly sensitive to assumptions (WACC, growth rate). Small changes can drastically
affect results. Always run sensitivity analysis and use DCF as one input among many for
investment decisions. Past FCF trends may not predict future performance.
            """.strip(),
        "inputSchema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Company ticker symbol (e.g., 'AAPL', 'MSFT'). Must be exact."
                },
                "wacc": {
                    "type": "number",
                    "minimum": 0.01,
                    "maximum": 0.50,
                    "description": "WACC (Weighted Average Cost of Capital) as decimal (e.g., 0.08 for 8%). Typical range: 0.07-0.12"
                },
                "terminal_growth_rate": {
                    "type": "number",
                    "minimum": 0.0,
                    "maximum": 0.10,
                    "default": 0.025,
                    "description": "Perpetual growth rate as decimal (default 0.025 = 2.5%). Must be < WACC. Typical range: 0.02-0.03"
                },
                "projection_years": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 10,
                    "default": 5,
                    "description": "Number of years to project FCF (default 5). Range: 1-10"
                }
            },
            "required": ["ticker", "wacc"]
        }
    }

    # Add annotations if supported
    if annotations is not None:
        dcf_inputs_kwargs["annotations"] = annotations
        calculate_dcf_kwargs["annotations"] = annotations

    # Add titles for better display in MCP clients
    dcf_inputs_kwargs["title"] = "Get DCF Inputs"
    calculate_dcf_kwargs["title"] = "Calculate DCF Valuation"

    # Tool 3: Batch DCF
    batch_dcf_kwargs = {
        "name": "batch_dcf",
        "description": """
Run DCF valuations on multiple companies in parallel for efficient analysis.

**WHEN TO USE THIS:**
- User asks for DCF on specific list of tickers (e.g., "Run DCF on AAPL, MSFT, GOOGL")
- Comparing valuations across a predefined set of companies
- Portfolio analysis across multiple holdings

**WHEN NOT TO USE:**
- User asks to "find undervalued stocks" → Use `scan_opportunities` instead
- Searching for investment opportunities → Use `scan_opportunities` instead
- Screening by criteria → Use `scan_opportunities` instead

Perfect for:
- Batch analysis of specific tickers you already know
- Comparing valuations across competitors
- Portfolio-wide DCF analysis
- Quick valuation of watchlist companies

Returns:
- **Results**: List of DCF analyses (one per ticker)
  - Success cases: Full DCF valuation with intrinsic value, margin of safety, upside
  - Failed cases: Error message explaining why DCF couldn't be calculated
- **Summary**: Success/failure counts, total execution time

Parameters:
- `tickers`: List of ticker symbols to analyze (required, max 5 for guests, 50 for auth)
- `wacc`: Discount rate (optional, default: estimated per company, or specify uniform WACC)
- `terminal_growth_rate`: Perpetual growth rate (default: 2.5%)
- `projection_years`: DCF forecast period (default: 5 years)

Example Use Cases:
- "Run DCF on AAPL, MSFT, GOOGL" → Batch analyze tech giants
- "Compare fair values of WMT, TGT, COST" → Retail comp analysis
- "DCF my portfolio: AAPL, TSLA, NVDA, AMD" → Portfolio valuation check

Guest Limits:
- Maximum 5 tickers per batch
- Sign in for up to 50 tickers

**Performance:**
- Runs DCF calculations in parallel for speed
- Typical 3-5s per ticker, parallelized across all tickers
- Much faster than running individual `calculate_dcf` calls sequentially
            """.strip(),
        "inputSchema": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "description": "List of ticker symbols to analyze (e.g., ['AAPL', 'MSFT', 'GOOGL']). Max 5 for guests, 50 for authenticated.",
                    "items": {
                        "type": "string"
                    },
                    "minItems": 1,
                    "maxItems": 50
                },
                "wacc": {
                    "type": "number",
                    "description": "WACC to use for ALL companies (optional). If not specified, uses estimated WACC per company. Typical: 0.08-0.12",
                    "minimum": 0.01,
                    "maximum": 0.50
                },
                "terminal_growth_rate": {
                    "type": "number",
                    "description": "Terminal growth rate (default 0.025 = 2.5%)",
                    "default": 0.025,
                    "minimum": 0.0,
                    "maximum": 0.10
                },
                "projection_years": {
                    "type": "integer",
                    "description": "Years to project FCF (default 5)",
                    "default": 5,
                    "minimum": 2,
                    "maximum": 10
                }
            },
            "required": ["tickers"]
        }
    }

    # Add annotations if supported
    if annotations is not None:
        batch_dcf_kwargs["annotations"] = annotations

    # Add title for better display
    batch_dcf_kwargs["title"] = "Batch DCF Valuation"

    return [
        Tool(**dcf_inputs_kwargs),
        Tool(**calculate_dcf_kwargs),
        Tool(**batch_dcf_kwargs)
    ]
