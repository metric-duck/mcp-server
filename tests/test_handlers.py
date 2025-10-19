"""Tests for handler modules"""

import pytest
from unittest.mock import AsyncMock, patch
from metricduck_mcp.handlers import CompaniesHandler, StatementsHandler


class TestCompaniesHandler:
    """Tests for CompaniesHandler"""

    @pytest.mark.asyncio
    async def test_search_companies_success(self, companies_handler, mock_http_client, sample_search_results):
        """Test successful company search"""
        # Mock the handler's client
        companies_handler.client = mock_http_client
        mock_http_client.get.return_value = {"results": sample_search_results}

        # Execute search
        result = await companies_handler.search_companies("apple", limit=5)

        # Verify API was called correctly
        mock_http_client.get.assert_called_once_with(
            "/api/v1/companies/search",
            params={"q": "apple", "limit": 5}
        )

        # Verify result format
        assert "Found 2 matching companies" in result
        assert "AAPL" in result
        assert "Apple Inc." in result
        assert "MSFT" in result
        assert "Microsoft Corporation" in result

    @pytest.mark.asyncio
    async def test_search_companies_no_results(self, companies_handler, mock_http_client):
        """Test search with no results"""
        companies_handler.client = mock_http_client
        mock_http_client.get.return_value = {"results": []}

        # Mock fuzzy_match_company to also return empty
        with patch('metricduck_mcp.handlers.companies_handler.fuzzy_match_company', return_value=[]):
            result = await companies_handler.search_companies("nonexistent", limit=5)

        # Verify helpful message
        assert "No companies found" in result
        assert "Try:" in result

    @pytest.mark.asyncio
    async def test_search_companies_ticker_extraction(self, companies_handler, mock_http_client, sample_search_results):
        """Test that ticker is extracted from query"""
        companies_handler.client = mock_http_client
        mock_http_client.get.return_value = {"results": sample_search_results}

        # Search with ticker in natural language
        result = await companies_handler.search_companies("Get AAPL data", limit=5)

        # Verify ticker was extracted and used in search
        mock_http_client.get.assert_called_once()
        call_args = mock_http_client.get.call_args
        assert call_args[1]["params"]["q"] == "AAPL"

    @pytest.mark.asyncio
    async def test_get_company_overview_success(self, companies_handler, mock_http_client, sample_company_overview):
        """Test successful company overview fetch"""
        companies_handler.client = mock_http_client
        mock_http_client.get.return_value = sample_company_overview

        # Execute overview fetch
        result = await companies_handler.get_company_overview("AAPL")

        # Verify API was called correctly
        mock_http_client.get.assert_called_once_with("/api/v1/companies/AAPL/overview")

        # Verify result contains key sections
        assert "Apple Inc. (AAPL)" in result
        assert "Valuation Metrics" in result
        assert "Profitability Metrics" in result
        assert "Cash Flow" in result
        assert "Balance Sheet" in result

        # Verify formatting
        assert "$2.80T" in result  # Market cap formatted
        assert "28.50x" in result  # P/E ratio formatted
        assert "43.50%" in result  # Gross margin formatted

    @pytest.mark.asyncio
    async def test_get_company_overview_not_found(self, companies_handler, mock_http_client):
        """Test overview fetch for non-existent company"""
        companies_handler.client = mock_http_client

        # Mock 404 error
        from httpx import HTTPStatusError, Response, Request
        error_response = Response(
            status_code=404,
            text="Company not found",
            request=Request("GET", "http://test.com")
        )
        mock_http_client.get.side_effect = HTTPStatusError(
            "404 Not Found",
            request=error_response.request,
            response=error_response
        )

        # Execute overview fetch
        result = await companies_handler.get_company_overview("INVALID")

        # Verify error message
        assert "❌" in result
        assert "Resource not found" in result

    @pytest.mark.asyncio
    async def test_format_search_results(self, companies_handler, sample_search_results):
        """Test search results formatting"""
        from metricduck_mcp.models import CompanySearchResponse

        # Convert to models
        results = [CompanySearchResponse(**r) for r in sample_search_results]

        # Format results
        formatted = companies_handler._format_search_results(results)

        # Verify formatting
        assert "Found 2 matching companies" in formatted
        assert "AAPL - Apple Inc." in formatted
        assert "MSFT - Microsoft Corporation" in formatted
        assert "CIK:" in formatted
        assert "Apple designs and manufactures" in formatted

    @pytest.mark.asyncio
    async def test_format_overview(self, companies_handler, sample_company_overview):
        """Test company overview formatting"""
        from metricduck_mcp.models import CompanyOverviewResponse

        # Convert to model
        overview = CompanyOverviewResponse(**sample_company_overview)

        # Format overview
        formatted = companies_handler._format_overview(overview)

        # Verify sections
        assert "# Apple Inc. (AAPL)" in formatted
        assert "## 💰 Valuation Metrics" in formatted
        assert "## 📊 Profitability Metrics" in formatted
        assert "## 💵 Cash Flow" in formatted
        assert "## 🏦 Balance Sheet" in formatted

        # Verify metrics present
        assert "Market Cap: $2.80T" in formatted
        assert "P/E Ratio: 28.50x" in formatted
        assert "Revenue: $385.70B" in formatted
        assert "Net Income: $97.00B" in formatted
        assert "Gross Margin: 43.50%" in formatted
        assert "ROE: 147.00%" in formatted


class TestStatementsHandler:
    """Tests for StatementsHandler"""

    @pytest.mark.asyncio
    async def test_get_income_statement_success(self, statements_handler, mock_http_client, sample_income_statement):
        """Test successful income statement fetch"""
        statements_handler.client = mock_http_client
        mock_http_client.get.return_value = sample_income_statement

        # Execute income statement fetch
        result = await statements_handler.get_income_statement("AAPL", period="quarterly", years=2)

        # Verify API was called correctly
        mock_http_client.get.assert_called_once_with(
            "/api/v1/companies/AAPL/income-statement",
            params={"period": "quarterly", "years": 2}
        )

        # Verify result format
        assert "AAPL - Income Statement (Quarterly)" in result
        assert "Showing 2 periods" in result
        assert "Q4 2024" in result
        assert "Q3 2024" in result

        # Verify key metrics
        assert "Revenue" in result
        assert "$94.93B" in result  # Q4 2024 revenue
        assert "$85.78B" in result  # Q3 2024 revenue
        assert "Gross Profit" in result
        assert "Operating Income" in result
        assert "Net Income" in result

        # Verify margins
        assert "Gross Margin" in result
        assert "44.2%" in result  # Q4 2024 gross margin

        # Verify insights section
        assert "Key Insights" in result

    @pytest.mark.asyncio
    async def test_get_income_statement_no_data(self, statements_handler, mock_http_client):
        """Test income statement fetch with no data"""
        statements_handler.client = mock_http_client
        mock_http_client.get.return_value = []

        result = await statements_handler.get_income_statement("INVALID", period="quarterly", years=2)

        # Verify helpful message
        assert "No income statement data available" in result

    @pytest.mark.asyncio
    async def test_get_balance_sheet_success(self, statements_handler, mock_http_client, sample_balance_sheet):
        """Test successful balance sheet fetch"""
        statements_handler.client = mock_http_client
        mock_http_client.get.return_value = sample_balance_sheet

        # Execute balance sheet fetch
        result = await statements_handler.get_balance_sheet("AAPL", period="quarterly", years=2)

        # Verify API was called correctly
        mock_http_client.get.assert_called_once_with(
            "/api/v1/companies/AAPL/balance-sheet",
            params={"period": "quarterly", "years": 2}
        )

        # Verify result format
        assert "AAPL - Balance Sheet (Quarterly)" in result
        assert "Showing 2 periods" in result

        # Verify key metrics
        assert "Total Assets" in result
        assert "$364.98B" in result  # Q4 2024 assets
        assert "Cash & Equivalents" in result
        assert "Total Debt" in result
        assert "Total Equity" in result

        # Verify ratios
        assert "Current Ratio" in result
        assert "1.04x" in result
        assert "Debt/Equity" in result
        assert "1.87x" in result

        # Verify insights section
        assert "Key Insights" in result

    @pytest.mark.asyncio
    async def test_get_balance_sheet_no_data(self, statements_handler, mock_http_client):
        """Test balance sheet fetch with no data"""
        statements_handler.client = mock_http_client
        mock_http_client.get.return_value = []

        result = await statements_handler.get_balance_sheet("INVALID", period="quarterly", years=2)

        # Verify helpful message
        assert "No balance sheet data available" in result

    @pytest.mark.asyncio
    async def test_get_cash_flow_success(self, statements_handler, mock_http_client, sample_cash_flow):
        """Test successful cash flow fetch"""
        statements_handler.client = mock_http_client
        mock_http_client.get.return_value = sample_cash_flow

        # Execute cash flow fetch
        result = await statements_handler.get_cash_flow("AAPL", period="quarterly", years=2)

        # Verify API was called correctly
        mock_http_client.get.assert_called_once_with(
            "/api/v1/companies/AAPL/cash-flow",
            params={"period": "quarterly", "years": 2}
        )

        # Verify result format
        assert "AAPL - Cash Flow Statement (Quarterly)" in result
        assert "Showing 2 periods" in result

        # Verify key metrics
        assert "Operating Cash Flow" in result
        assert "$31.00B" in result  # Q4 2024 OCF
        assert "Free Cash Flow (FCF)" in result
        assert "$28.50B" in result  # Q4 2024 FCF
        assert "Capital Expenditures (CapEx)" in result

        # Verify FCF margin
        assert "FCF Margin" in result
        assert "30.0%" in result

        # Verify insights section
        assert "Key Insights" in result
        assert "generating cash" in result  # FCF is positive

    @pytest.mark.asyncio
    async def test_get_cash_flow_no_data(self, statements_handler, mock_http_client):
        """Test cash flow fetch with no data"""
        statements_handler.client = mock_http_client
        mock_http_client.get.return_value = []

        result = await statements_handler.get_cash_flow("INVALID", period="quarterly", years=2)

        # Verify helpful message
        assert "No cash flow data available" in result

    @pytest.mark.asyncio
    async def test_income_statement_default_parameters(self, statements_handler, mock_http_client, sample_income_statement):
        """Test income statement with default parameters"""
        statements_handler.client = mock_http_client
        mock_http_client.get.return_value = sample_income_statement

        # Execute with defaults (should be quarterly, 2 years)
        result = await statements_handler.get_income_statement("AAPL")

        # Verify defaults were used
        mock_http_client.get.assert_called_once_with(
            "/api/v1/companies/AAPL/income-statement",
            params={"period": "quarterly", "years": 2}
        )

    @pytest.mark.asyncio
    async def test_annual_period_formatting(self, statements_handler, mock_http_client):
        """Test annual period formatting in headers"""
        statements_handler.client = mock_http_client

        # Create annual data
        annual_data = [
            {
                "date": "2024-09-28",
                "period": "FY",
                "fiscal_year": 2024,
                "symbol": "AAPL",
                "metrics": {"revenues": 391000000000, "gross_margin": 45.0}
            }
        ]
        mock_http_client.get.return_value = annual_data

        result = await statements_handler.get_income_statement("AAPL", period="annual", years=1)

        # Verify annual formatting
        assert "Annual" in result
        assert "FY2024" in result

    @pytest.mark.asyncio
    async def test_error_handling(self, statements_handler, mock_http_client):
        """Test error handling for API failures"""
        statements_handler.client = mock_http_client

        # Mock HTTP error
        from httpx import HTTPStatusError, Response, Request
        error_response = Response(
            status_code=500,
            text="Internal Server Error",
            request=Request("GET", "http://test.com")
        )
        mock_http_client.get.side_effect = HTTPStatusError(
            "500 Internal Server Error",
            request=error_response.request,
            response=error_response
        )

        result = await statements_handler.get_income_statement("AAPL")

        # Verify error message
        assert "❌" in result
        assert "500" in result or "Server error" in result
