"""Pytest fixtures and configuration for MCP server tests"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from metricduck_mcp.config import Settings
from metricduck_mcp.handlers import CompaniesHandler, StatementsHandler


@pytest.fixture
def settings():
    """Test settings with mock API URL"""
    return Settings(
        api_base_url="http://localhost:8951",
        api_key="test_key",
        log_level="DEBUG"
    )


@pytest.fixture
def mock_http_client():
    """Mock HTTP client for testing handlers"""
    client = AsyncMock()

    # Default mock responses
    client.get = AsyncMock(return_value={
        "results": [
            {
                "ticker": "AAPL",
                "company_name": "Apple Inc.",
                "cik": "0000320193",
                "business_description": "Apple designs and manufactures consumer electronics..."
            }
        ]
    })

    client.post = AsyncMock(return_value={"success": True})

    return client


@pytest.fixture
async def companies_handler(settings):
    """Create CompaniesHandler instance for testing"""
    handler = CompaniesHandler(settings)
    yield handler
    await handler.close()


@pytest.fixture
def sample_company_overview():
    """Sample company overview data for testing"""
    return {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "cik": "0000320193",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "exchange": "NASDAQ",
        "market_cap": 2800000000000,
        "pe_ratio": 28.5,
        "pb_ratio": 42.3,
        "revenues": 385700000000,
        "net_income": 97000000000,
        "eps_diluted": 6.16,
        "gross_margin": 43.5,
        "operating_margin": 29.8,
        "net_margin": 25.1,
        "roe": 147.0,
        "roa": 23.1,
        "roic_v1": 52.4,
        "free_cash_flow": 105000000000,
        "operating_cash_flow": 118000000000,
        "total_debt": 106000000000,
        "cash_and_investments": 73000000000,
        "debt_to_equity": 1.75,
    }


@pytest.fixture
def sample_search_results():
    """Sample search results for testing"""
    return [
        {
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "cik": "0000320193",
            "business_description": "Apple designs and manufactures consumer electronics, computer software, and online services."
        },
        {
            "ticker": "MSFT",
            "company_name": "Microsoft Corporation",
            "cik": "0000789019",
            "business_description": "Microsoft develops, licenses, and supports software, services, devices, and solutions worldwide."
        }
    ]


@pytest.fixture
async def statements_handler(settings):
    """Create StatementsHandler instance for testing"""
    handler = StatementsHandler(settings)
    yield handler
    await handler.close()


@pytest.fixture
def sample_income_statement():
    """Sample income statement data for testing"""
    return [
        {
            "date": "2024-09-28",
            "period": "Q4",
            "fiscal_year": 2024,
            "symbol": "AAPL",
            "metrics": {
                "revenues": 94930000000,
                "cogs": 52990000000,
                "gross_profit": 41940000000,
                "ttl_oper_exps": 14340000000,
                "oper_inc": 27600000000,
                "net_income": 23000000000,
                "eps_diluted": 1.52,
                "gross_margin": 44.2,
                "oper_margin": 29.1,
                "net_margin": 24.2
            }
        },
        {
            "date": "2024-06-29",
            "period": "Q3",
            "fiscal_year": 2024,
            "symbol": "AAPL",
            "metrics": {
                "revenues": 85780000000,
                "cogs": 48450000000,
                "gross_profit": 37330000000,
                "ttl_oper_exps": 13540000000,
                "oper_inc": 23790000000,
                "net_income": 21450000000,
                "eps_diluted": 1.40,
                "gross_margin": 43.5,
                "oper_margin": 27.7,
                "net_margin": 25.0
            }
        }
    ]


@pytest.fixture
def sample_balance_sheet():
    """Sample balance sheet data for testing"""
    return [
        {
            "date": "2024-09-28",
            "period": "Q4",
            "fiscal_year": 2024,
            "symbol": "AAPL",
            "metrics": {
                "ttl_assets": 364980000000,
                "current_assets": 143560000000,
                "cash_eqv": 29940000000,
                "ttl_liabilities": 308030000000,
                "current_liabilities": 137480000000,
                "ttl_debt": 106630000000,
                "ttl_equity": 56950000000,
                "current_ratio": 1.04,
                "debt_to_equity": 1.87
            }
        },
        {
            "date": "2024-06-29",
            "period": "Q3",
            "fiscal_year": 2024,
            "symbol": "AAPL",
            "metrics": {
                "ttl_assets": 354590000000,
                "current_assets": 140300000000,
                "cash_eqv": 32950000000,
                "ttl_liabilities": 296040000000,
                "current_liabilities": 135460000000,
                "ttl_debt": 104070000000,
                "ttl_equity": 58550000000,
                "current_ratio": 1.04,
                "debt_to_equity": 1.78
            }
        }
    ]


@pytest.fixture
def sample_cash_flow():
    """Sample cash flow data for testing"""
    return [
        {
            "date": "2024-09-28",
            "period": "Q4",
            "fiscal_year": 2024,
            "symbol": "AAPL",
            "metrics": {
                "net_cf_ops": 31000000000,
                "capex": -2500000000,
                "fcf": 28500000000,
                "net_cf_inv": -3200000000,
                "net_cf_fin": -28400000000,
                "deprec_amort": 2800000000,
                "fcf_margin": 30.0
            }
        },
        {
            "date": "2024-06-29",
            "period": "Q3",
            "fiscal_year": 2024,
            "symbol": "AAPL",
            "metrics": {
                "net_cf_ops": 29100000000,
                "capex": -2100000000,
                "fcf": 27000000000,
                "net_cf_inv": -2850000000,
                "net_cf_fin": -25800000000,
                "deprec_amort": 2700000000,
                "fcf_margin": 31.5
            }
        }
    ]
