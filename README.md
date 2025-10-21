# MetricDuck MCP Server

Model Context Protocol (MCP) server providing AI-native access to MetricDuck's financial data API.

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/metric-duck/mcp-server/blob/main/LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io)

**Status:** 🚧 Pre-Beta (v0.0.2) - 8 tools active (2 company + 3 statements + 3 DCF + 1 screener)

---

## Overview

This MCP server enables AI assistants like Claude Code, Cursor, and Windsurf to seamlessly access MetricDuck's comprehensive financial data. Instead of making manual API calls, AI can use natural language to search companies, fetch financial metrics, and analyze data.

### Key Features

- 🔍 **Smart Company Search**: Fuzzy matching handles typos and variations
- 📊 **Comprehensive Financial Data**: Valuation, profitability, cash flow, balance sheet metrics
- 🤖 **AI-Optimized Output**: Formatted for readability and context
- ⚡ **HTTP-Based**: Complete decoupling from API codebase
- 🧪 **Well-Tested**: Comprehensive test suite with fixtures

### Architecture Highlights

- **Decoupled Design**: MCP server communicates with API via HTTP only (no code imports)
- **Temporary Model Duplication**: Pydantic models copied from API for rapid development (migration path documented)
- **Scalable**: Pattern-based structure for adding new tools
- **Production-Ready**: Logging, error handling, configuration management

---

## 📚 Documentation

**Complete documentation is now centralized in the `docs/` folder.**

### For Users
- **[User Documentation](./docs/user/README.md)** - Installation, configuration, tools reference
- **[Analytical Workflows](./ANALYTICAL_WORKFLOWS.md)** - 20+ workflow examples
- **[Quick Start](#installation)** - Get started in 5 minutes (below)

### For Developers
- **[Internal Documentation](./docs/internal/README.md)** - Architecture, development, features
- **[Sprint Documentation](./docs/internal/sprints/)** - Sprint plans & retrospectives
- **[API Specification](./docs/openapi/metricduck-api.json)** - OpenAPI spec

### Latest Updates
- ✅ **v0.0.2 Released**: Simplified DCF Methodology
  - Updated to industry-average beta/tax rates (11-sector classification)
  - FRED API integration for risk-free rate (updated weekly)
  - Simplified margin of safety (removed trading advice language)
  - Updated tool descriptions for transparency
- ✅ **Sprint 1 Complete**: DCF Trust Features ([docs](./docs/internal/sprints/sprint1-complete.md))
  - Reverse DCF (market-implied growth)
  - Margin of Safety analysis
  - Data Freshness assessment
- 📖 **Documentation Consolidation**: All docs now in MCP-compliant structure ([summary](./DOCUMENTATION_COMPLETE.md))

---

## Installation

### Prerequisites

- Python 3.10 or higher
- MetricDuck API running locally or remotely

### Quick Install (PyPI - Coming Soon)

```bash
pip install metricduck-mcp
```

### Development Install (From Source)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/metric-duck/mcp-server.git
   cd mcp-server
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment:**
   - **Windows:** `venv\Scripts\activate`
   - **Linux/Mac:** `source venv/bin/activate`

4. **Install dependencies:**
   ```bash
   pip install -e .
   ```

5. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your OAuth token (see Configuration section)
   ```

6. **Verify installation:**
   ```bash
   python -m metricduck_mcp --help
   ```

---

## Configuration

### Authentication

**🔐 OAuth 2.1 (Recommended)** - Secure, compliant with Anthropic MCP specification

1. **Get your OAuth token:**
   - Visit https://metricduck.com/mcp/auth
   - Sign in with Google, GitHub, or Email
   - Copy your access token

2. **Configure your MCP client:**
   ```json
   {
     "mcpServers": {
       "metricduck": {
         "command": "python",
         "args": ["-m", "metricduck_mcp"],
         "env": {
           "METRICDUCK_MCP_API_BASE_URL": "https://api.metricduck.com",
           "METRICDUCK_MCP_ACCESS_TOKEN": "your_oauth_token_here"
         }
       }
     }
   }
   ```

**🔑 API Key (Legacy)** - Deprecated for MCP, use for direct API access only

```json
{
  "mcpServers": {
    "metricduck": {
      "command": "python",
      "args": ["-m", "metricduck_mcp"],
      "env": {
        "METRICDUCK_MCP_API_BASE_URL": "https://api.metricduck.com",
        "METRICDUCK_MCP_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**Migration from API Key to OAuth:**
- OAuth tokens are more secure (1-hour expiration with automatic refresh)
- Required for Anthropic MCP Directory listing
- See [MCP_OAUTH_MIGRATION.md](MCP_OAUTH_MIGRATION.md) for full migration guide

### Environment Variables

Create a `.env` file in the project root:

```env
# MetricDuck API Configuration
METRICDUCK_MCP_API_BASE_URL=https://api.metricduck.com

# Authentication (choose one)
METRICDUCK_MCP_ACCESS_TOKEN=your_oauth_token_here  # Recommended
# METRICDUCK_MCP_API_KEY=your_api_key_here  # Legacy

# Server Settings
METRICDUCK_MCP_LOG_LEVEL=INFO
```

### Claude Desktop Integration

**Config Location:**
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux:** `~/.config/claude/claude_desktop_config.json`

**Example Configuration (OAuth):**

```json
{
  "mcpServers": {
    "metricduck": {
      "command": "python",
      "args": ["-m", "metricduck_mcp"],
      "env": {
        "METRICDUCK_MCP_API_BASE_URL": "https://api.metricduck.com",
        "METRICDUCK_MCP_ACCESS_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
      }
    }
  }
}
```

**After configuration:**
1. Restart Claude Desktop
2. Look for the 🔨 hammer icon in the chat interface
3. MetricDuck tools will be available for use

---

## Usage

### Starting the Server

**Option 1: Direct Python invocation**
```bash
python -m metricduck_mcp
```

**Option 2: Using startup script (Windows)**
```bash
cd mcp-server
scripts\start_server.bat
```

**Option 3: Using startup script (Linux/Mac)**
```bash
cd mcp-server
./scripts/start_server.sh
```

### Available Tools

#### 1. `search_companies`

Search for companies by name or ticker with fuzzy matching.

**Example Queries:**
- "apple" → AAPL (Apple Inc.)
- "micro soft" → MSFT (Microsoft Corporation)
- "tsla" → TSLA (Tesla, Inc.)

**Parameters:**
- `query` (required): Company name or ticker
- `limit` (optional): Max results (default: 5, max: 20)

**Usage in AI Chat:**
```
User: Find companies matching "costco"
AI: Uses search_companies tool with query="costco"
```

#### 2. `get_company_overview`

Get comprehensive financial overview for a specific company.

**Data Included:**
- Valuation metrics (P/E, P/B, EV/Sales, Market Cap)
- Profitability metrics (Revenue, Net Income, Margins, ROE, ROIC)
- Cash flow (Operating CF, Free CF)
- Balance sheet (Debt, Cash, Ratios)

**Parameters:**
- `ticker` (required): Company ticker symbol (e.g., "AAPL")

**Usage in AI Chat:**
```
User: What is Apple's P/E ratio?
AI: Uses get_company_overview tool with ticker="AAPL"
```

#### 3. `get_income_statement`

Get multi-period income statement data for revenue and profitability analysis.

**Data Included:**
- Top Line: Revenue (total sales)
- Costs: Cost of Revenue (COGS), Operating Expenses
- Profitability: Gross Profit, Operating Income (EBIT), Net Income
- Per-Share: EPS (Basic and Diluted)
- Margins: Gross Margin %, Operating Margin %, Net Margin %

**Parameters:**
- `ticker` (required): Company ticker symbol (e.g., "AAPL")
- `period` (optional): "quarterly" or "annual" (default: "quarterly")
- `years` (optional): Number of years of history (default: 2, max: 5)

**Usage in AI Chat:**
```
User: Show me Apple's revenue growth over the last 8 quarters
AI: Uses get_income_statement tool with ticker="AAPL", period="quarterly", years=2
```

#### 4. `get_balance_sheet`

Get multi-period balance sheet data for financial position and solvency analysis.

**Data Included:**
- Assets: Total Assets, Current Assets, Cash & Equivalents, Inventory, PP&E
- Liabilities: Total Liabilities, Current Liabilities, Total Debt, Accounts Payable
- Equity: Total Equity, Retained Earnings, Treasury Stock
- Ratios: Current Ratio, Quick Ratio, Debt/Equity, Debt/Assets

**Parameters:**
- `ticker` (required): Company ticker symbol (e.g., "AAPL")
- `period` (optional): "quarterly" or "annual" (default: "quarterly")
- `years` (optional): Number of years of history (default: 2, max: 5)

**Usage in AI Chat:**
```
User: What's Apple's cash position over time?
AI: Uses get_balance_sheet tool with ticker="AAPL", period="quarterly", years=2
```

#### 5. `get_cash_flow`

Get multi-period cash flow statement data for cash generation and capital allocation analysis.

**Data Included:**
- Operating Activities: Operating Cash Flow (OCF), Changes in Working Capital
- Investing Activities: Capital Expenditures (CapEx), Acquisitions, Asset Sales
- Financing Activities: Debt Issuance/Repayment, Dividends, Stock Buybacks
- Key Derived: Free Cash Flow (OCF - CapEx), FCF Margin %, Cash Conversion

**Parameters:**
- `ticker` (required): Company ticker symbol (e.g., "AAPL")
- `period` (optional): "quarterly" or "annual" (default: "quarterly")
- `years` (optional): Number of years of history (default: 2, max: 5)

**Usage in AI Chat:**
```
User: What's Apple's free cash flow trend?
AI: Uses get_cash_flow tool with ticker="AAPL", period="quarterly", years=2
```

---

## Development

### Project Structure

```
mcp-server/
├── src/metricduck_mcp/
│   ├── __init__.py           # Package init
│   ├── __main__.py           # Module entry point
│   ├── server.py             # MCP server main logic
│   ├── config.py             # Configuration management
│   │
│   ├── tools/                # Tool definitions by domain
│   │   ├── __init__.py
│   │   ├── companies.py      # Company tools
│   │   └── statements.py     # Financial statement tools
│   │
│   ├── handlers/             # Tool implementation
│   │   ├── __init__.py
│   │   ├── base.py           # Base HTTP handler
│   │   ├── companies_handler.py
│   │   └── statements_handler.py
│   │
│   ├── models/               # Pydantic models (temporary)
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── financial_statements.py
│   │
│   └── utils/                # Utilities
│       ├── __init__.py
│       ├── formatting.py     # Value formatting
│       └── natural_language.py  # Fuzzy matching
│
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures (21 total)
│   ├── test_handlers.py      # Handler tests (21 tests)
│   └── test_utils.py         # Utility tests (13 tests)
│
├── scripts/                  # Startup scripts
│   ├── start_server.sh       # Linux/Mac
│   └── start_server.bat      # Windows
│
├── pyproject.toml            # Package metadata
├── requirements.txt          # Dependencies
├── requirements-dev.txt      # Dev dependencies
└── .env.example              # Environment template
```

### Testing

We provide multiple testing levels for comprehensive quality assurance.

#### Quick Start

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=metricduck_mcp --cov-report=html
```

#### Testing Levels

**1. Unit Tests (Fastest - 5-10 seconds)**

```bash
# Run all unit tests
pytest tests/

# Run specific test file
pytest tests/test_handlers.py -v

# Run with coverage
pytest --cov=metricduck_mcp --cov-report=term
```

**2. MCP Inspector (Interactive Visual Testing)**

Anthropic's official tool for visual debugging:

```bash
# Install inspector (one-time)
npm install -g @modelcontextprotocol/inspector

# Start inspector with MCP server
npx @modelcontextprotocol/inspector python -m metricduck_mcp
```

Opens http://localhost:5173 with interactive UI to test all tools.

**3. End-to-End Testing (Claude Code)**

Test real user experience:

1. Configure in `~/.config/claude/mcp_settings.json`
2. Restart Claude Code
3. Test queries: "Search for 'apple'", "What's Microsoft's P/E ratio?"

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/

# Type checking
mypy src/
```

---

## Troubleshooting

### Common User Errors

#### 1. Authentication Errors (401 Unauthorized)

**Solution (OAuth - Recommended):**
1. Visit https://metricduck.com/mcp/auth
2. Sign in and copy your OAuth access token
3. Add it to your MCP config in `claude_desktop_config.json`
4. Restart Claude Desktop

**Still not working?**
- **OAuth:** Ensure token is complete (starts with `eyJ`), no spaces/line breaks
- **API Key:** Verify full key copied (starts with `fda_`)
- Token expired? OAuth tokens expire after 1 hour - regenerate at https://metricduck.com/mcp/auth

#### 2. MCP Server Won't Start

**Solution:**
1. **Check virtual environment is activated:**
   ```bash
   which python  # Should point to venv/bin/python
   ```

2. **Verify dependencies installed:**
   ```bash
   pip list | grep mcp
   ```

3. **Reinstall if needed:**
   ```bash
   pip install --upgrade -e .
   ```

#### 3. Tools Not Appearing in AI Client

**Solution:**
1. Verify MCP server is configured in your AI client's settings
2. Restart your AI client (Claude Desktop, Cursor, etc.)
3. Check MCP server logs for startup errors
4. Test with MCP Inspector:
   ```bash
   npx @modelcontextprotocol/inspector python -m metricduck_mcp
   ```

### Getting Help

**Still having issues?**

- **Email:** support@metricduck.com
- **GitHub Issues:** https://github.com/metric-duck/mcp-server/issues
- **Documentation:** https://metricduck.com/docs
- **Privacy Policy:** https://metricduck.com/mcp/privacy

---

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Write docstrings for public functions
- Format with Black
- Lint with Ruff

### Commit Messages

- Use conventional commits format
- Examples:
  - `feat(tools): add earnings insights tool`
  - `fix(handler): handle null values in overview`
  - `docs(readme): add troubleshooting section`

### Pull Request Process

1. Create feature branch
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit PR with clear description

---

## Privacy & Legal

### Privacy Policy

View our privacy policy for the MCP server at: https://metricduck.com/mcp/privacy

**Summary:**
- We log API requests (endpoints, tickers, timestamps) for analytics and quota enforcement
- We do NOT collect your conversations with AI assistants
- Your data is retained for 90 days, then deleted
- You can request data deletion at any time
- We do not sell your data

### Terms of Service

By using the MetricDuck MCP Server, you agree to MetricDuck's Terms of Service at: https://metricduck.com/terms

---

## License

MIT License - see [LICENSE](LICENSE) file for details

---

## Support

- **Issues**: Report bugs at https://github.com/metric-duck/mcp-server/issues
- **Email**: support@metricduck.com
- **Documentation**: https://metricduck.com/docs
- **Privacy Policy**: https://metricduck.com/mcp/privacy
- **Get OAuth Token**: https://metricduck.com/mcp/auth

---

**Built with ❤️ for AI-native financial data access**

---

## 📖 Analytical Capabilities

MetricDuck MCP enables **20+ high-value financial analytical workflows**. 

**Currently Supported (7 workflows):**
- ✅ Company search & discovery
- ✅ Financial health assessment
- ✅ Revenue & profitability analysis  
- ✅ Cash generation quality evaluation
- ✅ Financial position & liquidity check
- ✅ DCF intrinsic value calculation
- ✅ Margin trend analysis

**Coming Soon (13 workflows):**
- 🔄 Value stock screening (131+ metrics)
- 🔄 Quality company identification
- 🔄 Industry peer comparison
- 🔄 Growth stock screening
- 🔄 AI-powered earnings insights
- 🔄 Sector performance analysis
- 🔄 And more...

> **See [ANALYTICAL_WORKFLOWS.md](ANALYTICAL_WORKFLOWS.md) for complete workflow guide with examples**

