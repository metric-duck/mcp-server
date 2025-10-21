# Changelog

All notable changes to the MetricDuck MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.0.2] - 2025-01-21

### Changed
- **DCF Methodology Simplified**: Updated tool descriptions to reflect simplified DCF API methodology
  - Beta calculation: Now uses industry-average by 11-sector classification (not company-specific)
  - Tax rates: Industry-average effective tax rates by sector (Damodaran data)
  - Cost of debt: Simplified to risk-free rate + 3% spread
  - Risk-free rate: Now fetched from FRED API (10-Year Treasury, updated weekly)
- **Margin of Safety**: Removed trading advice language (entry/exit prices, buy/sell recommendations)
  - Now displays raw and adjusted margin of safety with neutral interpretation
  - Shows valuation context (conservative/base/optimistic scenarios)
- **Tool Descriptions**: Enhanced transparency in DCF tool descriptions
  - Added explicit methodology section explaining WACC calculation
  - Clarified use of industry averages vs company-specific data
  - Added disclaimer about DCF sensitivity to assumptions
- **Handler Formatting**: Updated DCF response formatting to match simplified API
  - Removed conviction scoring references
  - Updated market comparison labels for clarity
  - Simplified batch DCF results table headers

### Fixed
- README tool count: Corrected from "2 DCF" to "3 DCF" tools (get_dcf_inputs, calculate_dcf, batch_dcf)

## [0.0.1] - 2025-01-15

### Added
- Initial pre-beta release
- **8 MCP Tools Implemented**:
  - Company tools (2): `get_company_info`, `search_companies`
  - Financial statements (3): `get_income_statement`, `get_balance_sheet`, `get_cash_flow`
  - DCF valuation (3): `get_dcf_inputs`, `calculate_dcf`, `batch_dcf`
  - Screener (1): `screen_companies`
- **DCF Trust Features** (Sprint 1):
  - Reverse DCF analysis (market-implied growth calculation)
  - Margin of safety analysis with multiple risk profiles
  - Data freshness assessment
  - Valuation range scenarios (conservative/moderate/optimistic)
- **Authentication**: OAuth 2.1 and legacy API key support
- **Documentation**: Comprehensive setup guides, tool reference, and API spec
- **Testing**: 34 unit tests with mock fixtures
- **MCP Compliance**: Full Model Context Protocol integration

### Technical
- Python 3.10+ support
- MCP SDK >= 0.9.0
- httpx for async HTTP requests
- Pydantic for data validation
- Structured logging with structlog

---

## Release Notes

### v0.0.2 Focus
This release focuses on syncing the MCP server with recent API simplifications. The changes improve transparency and remove trading advice language, making the DCF tools more suitable for educational and analytical purposes.

**Breaking Changes**: None. All tools maintain backward compatibility.

**Next Steps**: v0.0.3 will add opportunities scanner tool and improve error handling.

### v0.0.1 Focus
Initial pre-beta release establishing core MCP server functionality with 8 tools. Focus on DCF valuation with trust-building features (reverse DCF, margin of safety, data freshness).
