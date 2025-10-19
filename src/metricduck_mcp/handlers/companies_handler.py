"""Handler for company-related tools"""

import logging
from typing import List, Dict, Any
from .base import BaseHandler
from ..utils.natural_language import fuzzy_match_company, extract_ticker
from ..utils.formatting import (
    format_currency,
    format_percentage,
    format_ratio,
    format_per_share
)
from ..models import CompanySearchResponse, CompanyOverviewResponse


logger = logging.getLogger(__name__)


class CompaniesHandler(BaseHandler):
    """Handler for company search and information tools"""

    async def search_companies(
        self,
        query: str,
        limit: int = 5
    ) -> str:
        """
        Search for companies with fuzzy matching fallback

        Strategy:
        1. Extract ticker if query looks like a ticker (e.g., "AAPL")
        2. Try exact API search first
        3. If no results, use fuzzy matching on cached company list
        4. Format results for AI readability

        Args:
            query: Company name or ticker to search
            limit: Maximum results to return

        Returns:
            AI-friendly formatted search results
        """
        logger.info(f"Searching companies with query: '{query}', limit: {limit}")

        # Try to extract ticker from query
        ticker = extract_ticker(query)
        if ticker:
            logger.debug(f"Detected ticker '{ticker}' in query")
            query = ticker

        # Try exact API search first
        try:
            response = await self.get(
                "/api/v1/companies/search",
                params={"q": query, "limit": limit}
            )

            if response.get("results"):
                results = [CompanySearchResponse(**r) for r in response["results"]]
                logger.info(f"API search found {len(results)} results")
                return self._format_search_results(results)

        except Exception as e:
            logger.warning(f"API search failed, falling back to fuzzy match: {e}")

        # Fallback: fuzzy match against company universe
        try:
            matches = await fuzzy_match_company(query, self, limit=limit)
            logger.info(f"Fuzzy match found {len(matches)} results")

            # Convert to CompanySearchResponse models
            results = [CompanySearchResponse(**m) for m in matches]
            return self._format_search_results(results)

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Company search failed: {error_msg}")
            return f"❌ Search failed: {error_msg}"

    def _format_search_results(self, results: List[CompanySearchResponse]) -> str:
        """
        Format search results for AI consumption

        Args:
            results: List of company search results

        Returns:
            Formatted string with company information
        """
        if not results:
            return "No companies found matching your query. Try:\n" \
                   "- Using a different spelling\n" \
                   "- Using the ticker symbol (e.g., 'AAPL' for Apple)\n" \
                   "- Being less specific (e.g., 'micro' instead of 'Microsoft Corp')"

        lines = [f"🔍 Found {len(results)} matching compan{'y' if len(results) == 1 else 'ies'}:\n"]

        for i, company in enumerate(results, 1):
            lines.append(f"{i}. **{company.ticker}** - {company.company_name}")

            if company.business_description:
                # Truncate description to 120 chars for readability
                desc = company.business_description
                if len(desc) > 120:
                    desc = desc[:117] + "..."
                lines.append(f"   {desc}")

            # Add CIK for reference (useful for SEC filings)
            lines.append(f"   CIK: {company.cik}")

            # Add separator between companies (except last)
            if i < len(results):
                lines.append("")

        response = "\n".join(lines)
        return self._add_feedback_footer(response)

    async def get_company_overview(self, ticker: str) -> str:
        """
        Get comprehensive company overview

        Args:
            ticker: Company ticker symbol

        Returns:
            AI-friendly formatted company overview with key metrics
        """
        logger.info(f"Fetching company overview for: {ticker}")

        try:
            response = await self.get(f"/api/v1/companies/{ticker}/overview")
            overview = CompanyOverviewResponse(**response)
            return self._format_overview(overview)

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Failed to fetch overview for {ticker}: {error_msg}")
            return f"❌ Failed to fetch overview for {ticker}: {error_msg}"

    def _format_overview(self, overview: CompanyOverviewResponse) -> str:
        """
        Format company overview for AI consumption

        Args:
            overview: Company overview data

        Returns:
            Well-formatted multi-section overview
        """
        lines = [
            f"# {overview.company_name} ({overview.ticker})",
            "",
        ]

        # Company metadata
        metadata_parts = []
        if overview.sector:
            metadata_parts.append(f"Sector: {overview.sector}")
        if overview.industry:
            metadata_parts.append(f"Industry: {overview.industry}")
        if overview.exchange:
            metadata_parts.append(f"Exchange: {overview.exchange}")

        if metadata_parts:
            lines.append(" | ".join(metadata_parts))
            lines.append("")

        # Data freshness
        if overview.as_of_date_ttm:
            lines.append(f"📅 **TTM Data as of:** {overview.as_of_date_ttm}")
        if overview.as_of_date_mrq:
            lines.append(f"📅 **MRQ Data as of:** {overview.as_of_date_mrq}")
        lines.append("")

        # Valuation Section
        lines.append("## 💰 Valuation Metrics (TTM)")
        lines.append("")
        val_metrics = [
            ("Market Cap", overview.market_cap, format_currency),
            ("Enterprise Value", overview.ev, format_currency),
            ("P/E Ratio", overview.pe_ratio, format_ratio),
            ("P/B Ratio", overview.pb_ratio, format_ratio),
            ("EV/Sales", overview.ev_sales, format_ratio),
            ("EV/FCF", overview.ev_fcf, format_ratio),
        ]

        for name, value, formatter in val_metrics:
            if value is not None:
                lines.append(f"- **{name}:** {formatter(value)}")
        lines.append("")

        # Profitability Section
        lines.append("## 📊 Profitability Metrics (TTM)")
        lines.append("")

        # Revenue & Income
        if overview.revenues:
            lines.append(f"- **Revenue:** {format_currency(overview.revenues)}")
        if overview.net_income:
            lines.append(f"- **Net Income:** {format_currency(overview.net_income)}")
        if overview.eps_diluted:
            lines.append(f"- **EPS (Diluted):** {format_per_share(overview.eps_diluted)}")
        lines.append("")

        # Margins
        lines.append("**Margins:**")
        margin_metrics = [
            ("Gross Margin", overview.gross_margin),
            ("Operating Margin", overview.operating_margin),
            ("Net Margin", overview.net_margin),
            ("FCF Margin", overview.fcf_margin),
        ]

        for name, value in margin_metrics:
            if value is not None:
                lines.append(f"- {name}: {format_percentage(value)}")
        lines.append("")

        # Returns
        lines.append("**Returns:**")
        return_metrics = [
            ("ROE", overview.roe),
            ("ROA", overview.roa),
            ("ROIC (v1)", overview.roic_v1),
        ]

        for name, value in return_metrics:
            if value is not None:
                lines.append(f"- {name}: {format_percentage(value)}")
        lines.append("")

        # Cash Flow Section
        lines.append("## 💵 Cash Flow (TTM)")
        lines.append("")
        if overview.operating_cash_flow:
            lines.append(f"- **Operating Cash Flow:** {format_currency(overview.operating_cash_flow)}")
        if overview.free_cash_flow:
            lines.append(f"- **Free Cash Flow:** {format_currency(overview.free_cash_flow)}")
        lines.append("")

        # Balance Sheet Section
        lines.append("## 🏦 Balance Sheet (Most Recent Quarter)")
        lines.append("")
        bs_metrics = [
            ("Total Debt", overview.total_debt, format_currency),
            ("Cash & Investments", overview.cash_and_investments, format_currency),
            ("Shares Outstanding", overview.shares_basic, lambda x: format_number(x, 0) + " shares"),
            ("Debt/Equity", overview.debt_to_equity, format_ratio),
            ("Debt/Assets", overview.debt_to_assets, format_percentage),
        ]

        for name, value, formatter in bs_metrics:
            if value is not None:
                lines.append(f"- **{name}:** {formatter(value)}")

        response = "\n".join(lines)
        return self._add_feedback_footer(response)


def format_number(value: float, decimals: int = 2) -> str:
    """Helper to format large numbers with units"""
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.{decimals}f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.{decimals}f}M"
    elif value >= 1_000:
        return f"{value / 1_000:.{decimals}f}K"
    else:
        return f"{value:,.{decimals}f}"
