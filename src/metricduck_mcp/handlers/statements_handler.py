"""Handler for financial statement tools"""

import logging
from typing import List, Dict, Any
from .base import BaseHandler
from ..utils.formatting import format_currency, format_percentage


logger = logging.getLogger(__name__)


class StatementsHandler(BaseHandler):
    """Handler for financial statement retrieval and formatting"""

    async def get_income_statement(
        self,
        ticker: str,
        period: str = "quarterly",
        years: int = 2
    ) -> str:
        """
        Get income statement data and format for AI consumption

        Args:
            ticker: Company ticker symbol
            period: "quarterly" or "annual"
            years: Number of years of history

        Returns:
            Formatted markdown table with income statement data
        """
        logger.info(f"Fetching income statement for {ticker}, period={period}, years={years}")

        try:
            response = await self.get(
                f"/api/v1/companies/{ticker}/income-statement",
                params={"period": period, "years": years}
            )

            if not response:
                return f"No income statement data found for {ticker}."

            return self._format_income_statement(ticker, response, period)

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Failed to fetch income statement for {ticker}: {error_msg}")
            return f"❌ {error_msg}"

    async def get_balance_sheet(
        self,
        ticker: str,
        period: str = "quarterly",
        years: int = 2
    ) -> str:
        """
        Get balance sheet data and format for AI consumption

        Args:
            ticker: Company ticker symbol
            period: "quarterly" or "annual"
            years: Number of years of history

        Returns:
            Formatted markdown table with balance sheet data
        """
        logger.info(f"Fetching balance sheet for {ticker}, period={period}, years={years}")

        try:
            response = await self.get(
                f"/api/v1/companies/{ticker}/balance-sheet",
                params={"period": period, "years": years}
            )

            if not response:
                return f"No balance sheet data found for {ticker}."

            return self._format_balance_sheet(ticker, response, period)

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Failed to fetch balance sheet for {ticker}: {error_msg}")
            return f"❌ {error_msg}"

    async def get_cash_flow(
        self,
        ticker: str,
        period: str = "quarterly",
        years: int = 2
    ) -> str:
        """
        Get cash flow statement data and format for AI consumption

        Args:
            ticker: Company ticker symbol
            period: "quarterly" or "annual"
            years: Number of years of history

        Returns:
            Formatted markdown table with cash flow data
        """
        logger.info(f"Fetching cash flow for {ticker}, period={period}, years={years}")

        try:
            response = await self.get(
                f"/api/v1/companies/{ticker}/cash-flow",
                params={"period": period, "years": years}
            )

            if not response:
                return f"No cash flow data found for {ticker}."

            return self._format_cash_flow(ticker, response, period)

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Failed to fetch cash flow for {ticker}: {error_msg}")
            return f"❌ {error_msg}"

    def _format_income_statement(
        self,
        ticker: str,
        data: List[Dict[str, Any]],
        period: str
    ) -> str:
        """Format income statement as markdown table"""
        if not data:
            return f"No income statement data available for {ticker}."

        # Sort by date descending (most recent first)
        sorted_data = sorted(data, key=lambda x: x['date'], reverse=True)

        # Extract company name
        company_name = sorted_data[0].get('symbol', ticker)

        lines = [
            f"# {ticker} - Income Statement ({period.capitalize()})",
            "",
            f"**Showing {len(sorted_data)} periods** (most recent first)",
            ""
        ]

        # Key metrics to show
        key_metrics = [
            ('revenues', 'Revenue', format_currency),
            ('cogs', 'Cost of Revenue (COGS)', format_currency),
            ('gross_profit', 'Gross Profit', format_currency),
            ('ttl_oper_exps', 'Operating Expenses', format_currency),
            ('oper_inc', 'Operating Income', format_currency),
            ('net_income', 'Net Income', format_currency),
            ('eps_diluted', 'EPS (Diluted)', lambda x: f"${x:.2f}" if x else "N/A"),
            ('gross_margin', 'Gross Margin', format_percentage),
            ('oper_margin', 'Operating Margin', format_percentage),
            ('net_margin', 'Net Margin', format_percentage),
        ]

        # Build table header
        period_headers = []
        for item in sorted_data[:8]:  # Show max 8 periods
            fiscal_period = item.get('period', 'N/A')
            fiscal_year = item.get('fiscal_year', '')
            if period == 'quarterly':
                period_headers.append(f"{fiscal_period} {fiscal_year}")
            else:
                period_headers.append(f"FY{fiscal_year}")

        # Create table
        header = "| Metric | " + " | ".join(period_headers) + " |"
        separator = "|" + "|".join(["---"] * (len(period_headers) + 1)) + "|"

        lines.append(header)
        lines.append(separator)

        # Add data rows
        for metric_id, metric_name, formatter in key_metrics:
            row_values = []
            for item in sorted_data[:8]:
                metrics = item.get('metrics', {})
                value = metrics.get(metric_id)
                if value is not None:
                    row_values.append(formatter(value))
                else:
                    row_values.append("N/A")

            row = f"| **{metric_name}** | " + " | ".join(row_values) + " |"
            lines.append(row)

        # Add trend analysis
        lines.append("")
        lines.append("## 📈 Key Insights")
        lines.append("")

        # Revenue trend
        if len(sorted_data) >= 2:
            recent_revenue = sorted_data[0].get('metrics', {}).get('revenues')
            prior_revenue = sorted_data[1].get('metrics', {}).get('revenues')

            if recent_revenue and prior_revenue:
                revenue_change = ((recent_revenue - prior_revenue) / prior_revenue) * 100
                trend = "↑" if revenue_change > 0 else "↓"
                lines.append(f"- Revenue {trend} {abs(revenue_change):.1f}% vs prior period")

        # Margin trend
        recent_margin = sorted_data[0].get('metrics', {}).get('oper_margin')
        if recent_margin:
            lines.append(f"- Current Operating Margin: {format_percentage(recent_margin)}")

        response = "\n".join(lines)
        return self._add_feedback_footer(response)

    def _format_balance_sheet(
        self,
        ticker: str,
        data: List[Dict[str, Any]],
        period: str
    ) -> str:
        """Format balance sheet as markdown table"""
        if not data:
            return f"No balance sheet data available for {ticker}."

        sorted_data = sorted(data, key=lambda x: x['date'], reverse=True)

        lines = [
            f"# {ticker} - Balance Sheet ({period.capitalize()})",
            "",
            f"**Showing {len(sorted_data)} periods** (most recent first)",
            ""
        ]

        # Key metrics to show
        key_metrics = [
            ('ttl_assets', 'Total Assets', format_currency),
            ('current_assets', 'Current Assets', format_currency),
            ('cash_eqv', 'Cash & Equivalents', format_currency),
            ('ttl_liabilities', 'Total Liabilities', format_currency),
            ('current_liabilities', 'Current Liabilities', format_currency),
            ('ttl_debt', 'Total Debt', format_currency),
            ('ttl_equity', 'Total Equity', format_currency),
            ('current_ratio', 'Current Ratio', lambda x: f"{x:.2f}x" if x else "N/A"),
            ('debt_to_equity', 'Debt/Equity', lambda x: f"{x:.2f}x" if x else "N/A"),
        ]

        # Build table
        period_headers = []
        for item in sorted_data[:8]:
            fiscal_period = item.get('period', 'N/A')
            fiscal_year = item.get('fiscal_year', '')
            if period == 'quarterly':
                period_headers.append(f"{fiscal_period} {fiscal_year}")
            else:
                period_headers.append(f"FY{fiscal_year}")

        header = "| Metric | " + " | ".join(period_headers) + " |"
        separator = "|" + "|".join(["---"] * (len(period_headers) + 1)) + "|"

        lines.append(header)
        lines.append(separator)

        for metric_id, metric_name, formatter in key_metrics:
            row_values = []
            for item in sorted_data[:8]:
                metrics = item.get('metrics', {})
                value = metrics.get(metric_id)
                if value is not None:
                    row_values.append(formatter(value))
                else:
                    row_values.append("N/A")

            row = f"| **{metric_name}** | " + " | ".join(row_values) + " |"
            lines.append(row)

        # Add insights
        lines.append("")
        lines.append("## 🏦 Key Insights")
        lines.append("")

        recent = sorted_data[0].get('metrics', {})
        cash = recent.get('cash_eqv')
        debt = recent.get('ttl_debt')
        current_ratio = recent.get('current_ratio')

        if cash:
            lines.append(f"- Cash Position: {format_currency(cash)}")
        if debt:
            lines.append(f"- Total Debt: {format_currency(debt)}")
        if current_ratio:
            lines.append(f"- Current Ratio: {current_ratio:.2f}x (>1 = healthy liquidity)")

        response = "\n".join(lines)
        return self._add_feedback_footer(response)

    def _format_cash_flow(
        self,
        ticker: str,
        data: List[Dict[str, Any]],
        period: str
    ) -> str:
        """Format cash flow statement as markdown table"""
        if not data:
            return f"No cash flow data available for {ticker}."

        sorted_data = sorted(data, key=lambda x: x['date'], reverse=True)

        lines = [
            f"# {ticker} - Cash Flow Statement ({period.capitalize()})",
            "",
            f"**Showing {len(sorted_data)} periods** (most recent first)",
            ""
        ]

        # Key metrics to show
        key_metrics = [
            ('net_cf_ops', 'Operating Cash Flow', format_currency),
            ('capex', 'Capital Expenditures (CapEx)', format_currency),
            ('fcf', 'Free Cash Flow (FCF)', format_currency),
            ('net_cf_inv', 'Investing Cash Flow', format_currency),
            ('net_cf_fin', 'Financing Cash Flow', format_currency),
            ('deprec_amort', 'Depreciation & Amortization', format_currency),
            ('fcf_margin', 'FCF Margin', format_percentage),
        ]

        # Build table
        period_headers = []
        for item in sorted_data[:8]:
            fiscal_period = item.get('period', 'N/A')
            fiscal_year = item.get('fiscal_year', '')
            if period == 'quarterly':
                period_headers.append(f"{fiscal_period} {fiscal_year}")
            else:
                period_headers.append(f"FY{fiscal_year}")

        header = "| Metric | " + " | ".join(period_headers) + " |"
        separator = "|" + "|".join(["---"] * (len(period_headers) + 1)) + "|"

        lines.append(header)
        lines.append(separator)

        for metric_id, metric_name, formatter in key_metrics:
            row_values = []
            for item in sorted_data[:8]:
                metrics = item.get('metrics', {})
                value = metrics.get(metric_id)
                if value is not None:
                    row_values.append(formatter(value))
                else:
                    row_values.append("N/A")

            row = f"| **{metric_name}** | " + " | ".join(row_values) + " |"
            lines.append(row)

        # Add insights
        lines.append("")
        lines.append("## 💵 Key Insights")
        lines.append("")

        recent = sorted_data[0].get('metrics', {})
        ocf = recent.get('net_cf_ops')
        fcf = recent.get('fcf')
        fcf_margin = recent.get('fcf_margin')

        if fcf:
            cash_status = "generating cash" if fcf > 0 else "burning cash"
            lines.append(f"- Free Cash Flow: {format_currency(fcf)} ({cash_status})")
        if fcf_margin:
            lines.append(f"- FCF Margin: {format_percentage(fcf_margin)}")
        if ocf and fcf:
            capex_pct = ((ocf - fcf) / ocf * 100) if ocf > 0 else 0
            lines.append(f"- CapEx as % of OCF: {capex_pct:.1f}%")

        response = "\n".join(lines)
        return self._add_feedback_footer(response)
