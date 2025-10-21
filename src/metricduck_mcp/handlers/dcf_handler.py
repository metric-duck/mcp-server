"""Handler for DCF (Discounted Cash Flow) valuation tools"""

import logging
from typing import Dict, Any
from .base import BaseHandler
from ..utils.formatting import format_currency, format_percentage

logger = logging.getLogger(__name__)


class DCFHandler(BaseHandler):
    """Handler for DCF valuation tools"""

    async def get_dcf_inputs(
        self,
        ticker: str,
        years: int = 5
    ) -> str:
        """
        Get all data needed for DCF analysis with estimated WACC.

        Args:
            ticker: Company ticker symbol
            years: Years of historical FCF data (2-10)

        Returns:
            AI-friendly formatted DCF inputs with estimated WACC
        """
        logger.info(f"Fetching DCF inputs for: {ticker}")

        try:
            response = await self.get(
                f"/api/v1/dcf/inputs/{ticker}",
                params={"years": years}
            )

            return self._format_dcf_inputs(response)

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Failed to fetch DCF inputs for {ticker}: {error_msg}")
            return f"❌ Failed to fetch DCF inputs for {ticker}: {error_msg}"

    async def calculate_dcf(
        self,
        ticker: str,
        wacc: float,
        terminal_growth_rate: float = 0.025,
        projection_years: int = 5
    ) -> str:
        """
        Run full DCF valuation.

        Args:
            ticker: Company ticker symbol
            wacc: Weighted average cost of capital (decimal)
            terminal_growth_rate: Perpetual growth rate (decimal)
            projection_years: Years to project (1-10)

        Returns:
            AI-friendly formatted DCF valuation results
        """
        logger.info(f"Running DCF for {ticker} with WACC={wacc}")

        try:
            # Build URL with query parameters (POST endpoint uses query params)
            url = (
                f"/api/v1/dcf/calculate/{ticker}"
                f"?wacc={wacc}"
                f"&terminal_growth_rate={terminal_growth_rate}"
                f"&projection_years={projection_years}"
            )
            response = await self.post(url)

            return self._format_dcf_results(response)

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Failed to calculate DCF for {ticker}: {error_msg}")
            return f"❌ Failed to calculate DCF for {ticker}: {error_msg}"

    async def batch_dcf(
        self,
        tickers: list,
        wacc: float = None,
        terminal_growth_rate: float = 0.025,
        projection_years: int = 5
    ) -> str:
        """
        Run batch DCF valuations on multiple companies in parallel.

        Args:
            tickers: List of ticker symbols to analyze
            wacc: Optional WACC to apply to all (None = estimated per company)
            terminal_growth_rate: Perpetual growth rate (decimal)
            projection_years: Years to project (2-10)

        Returns:
            AI-friendly formatted batch DCF results
        """
        logger.info(f"Running batch DCF for {len(tickers)} tickers")

        try:
            # Build request payload
            payload = {
                "tickers": tickers,
                "options": {
                    "terminal_growth_rate": terminal_growth_rate,
                    "projection_years": projection_years
                }
            }

            # Add WACC if specified
            if wacc is not None:
                payload["options"]["wacc"] = wacc

            # Call batch DCF API
            response = await self.post(
                "/api/v1/dcf/batch",
                json=payload
            )

            # Extract results
            results = response.get("results", [])
            summary = response.get("summary", {})

            logger.info(
                f"Batch DCF completed: {summary.get('successful', 0)} successful, "
                f"{summary.get('failed', 0)} failed"
            )

            return self._format_batch_dcf_results(
                results=results,
                summary=summary,
                tickers=tickers
            )

        except Exception as e:
            error_msg = self._format_error(e)
            logger.error(f"Batch DCF failed: {error_msg}")
            return f"❌ Batch DCF failed: {error_msg}"

    def _format_dcf_inputs(self, data: Dict[str, Any]) -> str:
        """
        Format DCF inputs for AI consumption.

        Returns well-structured overview of all inputs needed for DCF.
        """
        lines = []

        # Header
        ticker = data.get("ticker", "N/A")
        company_name = data.get("company_name", "N/A")
        lines.append(f"# DCF Inputs for {ticker} ({company_name})\n")

        # Historical FCF
        fcf_history = data.get("historical_fcf", [])
        if fcf_history:
            lines.append("## Historical Free Cash Flow")
            for period in fcf_history:
                fcf = period.get("fcf", 0)
                year = period.get("fiscal_year", "N/A")
                lines.append(f"  - FY {year}: {format_currency(fcf)}")

            growth_rate = data.get("fcf_growth_rate_cagr", 0)
            years_count = data.get("years_of_data", 0)
            lines.append(f"\n  📈 **FCF Growth Rate (CAGR)**: {format_percentage(growth_rate)} ({years_count} years)")
        else:
            lines.append("## Historical Free Cash Flow\n  ⚠️ No FCF data available")

        # Balance Sheet
        bs = data.get("balance_sheet", {})
        lines.append("\n## Balance Sheet (Latest)")
        lines.append(f"  - **Total Debt**: {format_currency(bs.get('total_debt', 0))}")
        lines.append(f"  - **Cash & Equivalents**: {format_currency(bs.get('cash_and_equivalents', 0))}")
        lines.append(f"  - **Net Debt**: {format_currency(bs.get('net_debt', 0))}")
        lines.append(f"  - **Total Equity**: {format_currency(bs.get('total_equity', 0))}")
        lines.append(f"  - **Shares Outstanding**: {bs.get('shares_outstanding', 0) / 1_000_000:.1f}M shares")
        lines.append(f"  - **As of**: {bs.get('as_of_date', 'N/A')}")

        # Tax Rate
        tax_rate = data.get("tax_rate", 0)
        lines.append(f"\n## Tax Rate")
        lines.append(f"  - **Effective Tax Rate**: {format_percentage(tax_rate)}")

        # Estimated WACC
        wacc_data = data.get("estimated_wacc", {})
        wacc = wacc_data.get("wacc", 0)
        components = wacc_data.get("components", {})

        lines.append(f"\n## Estimated WACC")
        lines.append(f"  - **WACC**: {format_percentage(wacc)}")
        lines.append(f"\n  ### Components:")
        lines.append(f"  - Cost of Equity: {format_percentage(components.get('cost_of_equity', 0))}")
        lines.append(f"    - Beta: {components.get('beta', 0):.2f}")
        lines.append(f"    - Risk-Free Rate: {format_percentage(components.get('risk_free_rate', 0))}")
        lines.append(f"    - Market Risk Premium: {format_percentage(components.get('market_risk_premium', 0))}")
        lines.append(f"  - Cost of Debt (after-tax): {format_percentage(components.get('cost_of_debt_after_tax', 0))}")
        lines.append(f"  - Weight Equity: {format_percentage(components.get('weight_equity', 0))}")
        lines.append(f"  - Weight Debt: {format_percentage(components.get('weight_debt', 0))}")

        methodology = wacc_data.get("methodology", "N/A")
        disclaimer = wacc_data.get("disclaimer", "")
        lines.append(f"\n  💡 **Methodology**: {methodology}")
        if disclaimer:
            lines.append(f"  ⚠️ **Note**: {disclaimer}")

        # Data Freshness
        freshness = data.get("data_freshness")
        if freshness:
            status_emoji = {
                "fresh": "✅",
                "aging": "⚠️",
                "stale": "⚠️⚠️",
                "very_stale": "❌",
                "unknown": "❓"
            }.get(freshness.get("status"), "❓")

            lines.append(f"\n## Data Freshness")
            lines.append(f"  {status_emoji} **Status**: {freshness.get('status', 'unknown').replace('_', ' ').title()}")
            lines.append(f"  📅 **Latest Filing**: {freshness.get('newest_filing_date', 'N/A')} "
                        f"({freshness.get('days_since_newest_filing', '?')} days ago)")
            lines.append(f"  📊 **Period End**: {freshness.get('period_end', 'N/A')}")

            warning = freshness.get('warning')
            if warning:
                lines.append(f"\n  ⚠️  **Warning**: {warning}")

            days_until_next = freshness.get('days_until_estimated_next_filing')
            if days_until_next and days_until_next > 0:
                lines.append(f"  📆 **Estimated Next Filing**: {freshness.get('estimated_next_filing', 'N/A')} "
                            f"(~{days_until_next} days)")

        # Next Steps
        lines.append(f"\n## Next Steps")
        lines.append(f"To run DCF valuation:")
        lines.append(f"1. Review the estimated WACC above ({format_percentage(wacc)})")
        lines.append(f"2. Optionally calculate your own WACC if you have better assumptions")
        lines.append(f"3. Use `calculate_dcf` with your chosen WACC")
        lines.append(f"\nExample: `calculate_dcf('{ticker}', wacc=0.08, terminal_growth_rate=0.025)`")

        return "\n".join(lines)

    def _format_dcf_results(self, data: Dict[str, Any]) -> str:
        """
        Format DCF valuation results for AI consumption.

        Returns comprehensive valuation report with interpretation.
        """
        lines = []

        # Header
        ticker = data.get("ticker", "N/A")
        company_name = data.get("company_name", "N/A")
        lines.append(f"# DCF Valuation Results for {ticker} ({company_name})\n")

        # Valuation
        valuation = data.get("valuation", {})
        intrinsic_value = valuation.get("intrinsic_value_per_share", 0)
        equity_value = valuation.get("equity_value", 0)
        enterprise_value = valuation.get("enterprise_value", 0)

        lines.append("## Intrinsic Value")
        lines.append(f"  - **Intrinsic Value Per Share**: ${intrinsic_value:.2f}")
        lines.append(f"  - **Equity Value**: ${equity_value:.1f}M")
        lines.append(f"  - **Enterprise Value**: ${enterprise_value:.1f}M")

        # Valuation Range (from growth scenarios)
        valuation_range = data.get("valuation_range")
        if valuation_range:
            lines.append(f"\n## Valuation Range")
            lines.append(f"Based on conservative/base/optimistic FCF growth scenarios:")

            conservative = valuation_range.get("conservative", {})
            base = valuation_range.get("base", {})
            optimistic = valuation_range.get("optimistic", {})

            cons_value = conservative.get("intrinsic_value_per_share", 0)
            cons_growth = conservative.get("fcf_growth_rate", 0)
            base_value = base.get("intrinsic_value_per_share", 0)
            base_growth = base.get("fcf_growth_rate", 0)
            opt_value = optimistic.get("intrinsic_value_per_share", 0)
            opt_growth = optimistic.get("fcf_growth_rate", 0)

            lines.append(f"  - **Conservative**: ${cons_value:.2f} (FCF growth: {format_percentage(cons_growth)})")
            lines.append(f"  - **Base Case**: ${base_value:.2f} (FCF growth: {format_percentage(base_growth)})")
            lines.append(f"  - **Optimistic**: ${opt_value:.2f} (FCF growth: {format_percentage(opt_growth)})")

            # Calculate range
            range_width = opt_value - cons_value
            range_pct = (range_width / base_value * 100) if base_value > 0 else 0
            lines.append(f"\n  📊 **Range**: ${cons_value:.2f} - ${opt_value:.2f} (±{range_pct:.1f}%)")

            note = valuation_range.get("note")
            if note:
                lines.append(f"  💡 {note}")

        # Market Comparison (if available)
        market_comparison = data.get("market_comparison")
        if market_comparison:
            lines.append(f"\n## Market Comparison")
            current_price = market_comparison.get("current_price", 0)
            price_date = market_comparison.get("price_date", "N/A")
            upside_pct = market_comparison.get("upside_percent", 0)
            recommendation = market_comparison.get("recommendation", "N/A")

            lines.append(f"  - **Current Market Price**: ${current_price:.2f} (as of {price_date})")
            lines.append(f"  - **Intrinsic Value**: ${intrinsic_value:.2f}")
            lines.append(f"  - **Upside/Downside**: {upside_pct:+.2f}%")
            lines.append(f"  - **Relative Valuation**: {recommendation}")

            # 52-week range comparison
            high_52w = market_comparison.get("fifty_two_week_high")
            low_52w = market_comparison.get("fifty_two_week_low")
            if high_52w and low_52w:
                lines.append(f"\n  **52-Week Range**: ${low_52w:.2f} - ${high_52w:.2f}")

                intrinsic_vs_high = market_comparison.get("intrinsic_vs_52w_high_pct")
                intrinsic_vs_low = market_comparison.get("intrinsic_vs_52w_low_pct")

                if intrinsic_vs_high is not None:
                    lines.append(f"  - Intrinsic vs 52W High: {intrinsic_vs_high:+.2f}%")
                if intrinsic_vs_low is not None:
                    lines.append(f"  - Intrinsic vs 52W Low: {intrinsic_vs_low:+.2f}%")

        # Reverse DCF (Market Implied Growth)
        reverse_dcf = data.get("reverse_dcf")
        if reverse_dcf and reverse_dcf.get("converged"):
            lines.append(f"\n## Reverse DCF Analysis")
            implied_growth = reverse_dcf.get("implied_fcf_growth_rate", 0)
            lines.append(f"  💡 **Market Implied FCF Growth**: {format_percentage(implied_growth)}")

            # Compare to historical growth
            assumptions_temp = data.get("assumptions", {})
            historical_growth = assumptions_temp.get("fcf_growth_rate", 0)
            lines.append(f"  📊 **Historical Growth (CAGR)**: {format_percentage(historical_growth)}")

            # Generate interpretation
            if implied_growth > historical_growth * 1.2:
                diff_pct = ((implied_growth / historical_growth) - 1) * 100 if historical_growth > 0 else 0
                lines.append(f"\n  ⚠️  Market expects **{diff_pct:.0f}% higher growth** than historical trend")
                lines.append(f"  💭 Current price implies optimistic growth assumptions")
            elif implied_growth < historical_growth * 0.8:
                diff_pct = (1 - (implied_growth / historical_growth)) * 100 if historical_growth > 0 else 0
                lines.append(f"\n  ✅ Market expects **{diff_pct:.0f}% lower growth** than historical trend")
                lines.append(f"  💭 Current price may be conservative or market sees headwinds")
            else:
                lines.append(f"\n  ✔️  Market expectations **aligned** with historical growth")
                lines.append(f"  💭 Current price reflects recent performance trajectory")
        elif reverse_dcf:
            error = reverse_dcf.get("error") or reverse_dcf.get("warning")
            if error:
                lines.append(f"\n## Reverse DCF Analysis")
                lines.append(f"  ⚠️  {error}")

        # Margin of Safety
        mos = data.get("margin_of_safety")
        if mos:
            lines.append(f"\n## Margin of Safety")
            raw_mos = mos.get("raw_margin_of_safety", 0)
            adjusted_mos = mos.get("adjusted_margin_of_safety", 0)
            interpretation = mos.get("interpretation", "")
            confidence_mult = mos.get("confidence_multiplier", 1.0)

            lines.append(f"  📊 **Raw MOS**: {format_percentage(raw_mos)}")
            lines.append(f"  📊 **Adjusted MOS**: {format_percentage(adjusted_mos)} (confidence: {confidence_mult:.1f}x)")
            lines.append(f"  💭 **Interpretation**: {interpretation}")

            # Valuation context (conservative/base/optimistic)
            valuation_context = mos.get("valuation_context", {})
            if valuation_context:
                lines.append(f"\n  ### Valuation Range Context:")
                cons = valuation_context.get("conservative", 0)
                base = valuation_context.get("base", 0)
                opt = valuation_context.get("optimistic", 0)
                lines.append(f"  - **Conservative**: ${cons:.2f}")
                lines.append(f"  - **Base Case**: ${base:.2f}")
                lines.append(f"  - **Optimistic**: ${opt:.2f}")

        # Assumptions
        assumptions = data.get("assumptions", {})
        lines.append(f"\n## Assumptions Used")
        lines.append(f"  - **WACC**: {format_percentage(assumptions.get('wacc', 0))}")
        lines.append(f"  - **Terminal Growth Rate**: {format_percentage(assumptions.get('terminal_growth_rate', 0))}")
        lines.append(f"  - **FCF Growth Rate (CAGR)**: {format_percentage(assumptions.get('fcf_growth_rate', 0))}")
        lines.append(f"  - **Projection Years**: {assumptions.get('projection_years', 5)}")
        lines.append(f"  - **Last FCF**: ${assumptions.get('last_fcf', 0):.1f}M")
        lines.append(f"  - **Net Debt**: ${assumptions.get('net_debt', 0):.1f}M")
        lines.append(f"  - **Shares Outstanding**: {assumptions.get('shares_outstanding', 0):.1f}M")

        # Projections
        projections = data.get("projections", {})
        fcf_projected = projections.get("fcf_projected", [])

        if fcf_projected:
            lines.append(f"\n## Projected Free Cash Flows")
            for year_data in fcf_projected:
                year = year_data.get("year", 0)
                fcf = year_data.get("fcf", 0)
                pv_fcf = year_data.get("pv_fcf", 0)
                lines.append(f"  - Year {year}: FCF ${fcf:.1f}M → PV ${pv_fcf:.1f}M")

            total_pv = projections.get("total_pv_fcf", 0)
            lines.append(f"\n  **Total PV of Projected FCF**: ${total_pv:.1f}M")

        # Terminal Value
        terminal_value = projections.get("terminal_value", 0)
        pv_terminal = projections.get("pv_terminal_value", 0)
        lines.append(f"\n## Terminal Value")
        lines.append(f"  - Terminal Value: ${terminal_value:.1f}M")
        lines.append(f"  - PV of Terminal Value: ${pv_terminal:.1f}M")

        # Sensitivity Analysis
        sensitivity = data.get("sensitivity_analysis", {})
        if sensitivity:
            wacc_range = sensitivity.get("wacc_range", [])
            growth_range = sensitivity.get("terminal_growth_range", [])
            grid = sensitivity.get("intrinsic_value_grid", [])

            lines.append(f"\n## Sensitivity Analysis")
            lines.append(f"Intrinsic value per share at different WACC and terminal growth rates:\n")

            # Table header
            header = "WACC \\ Growth |"
            for g in growth_range:
                header += f" {g*100:.1f}% |"
            lines.append(header)
            lines.append("-" * len(header))

            # Table rows
            for i, wacc in enumerate(wacc_range):
                row = f" {wacc*100:.1f}%        |"
                for j in range(len(growth_range)):
                    value = grid[i][j]
                    row += f" ${value:>6.2f} |"
                lines.append(row)

        # Metadata
        calc_date = data.get("calculation_date", "N/A")
        source = data.get("data_source", "N/A")
        lines.append(f"\n## Data Source")
        lines.append(f"  - Calculation Date: {calc_date}")
        lines.append(f"  - Data Source: {source}")

        # Interpretation (optional, for AI guidance)
        lines.append(f"\n## Interpretation Guide")
        if market_comparison:
            upside_pct = market_comparison.get("upside_percent", 0)
            if upside_pct > 0:
                lines.append(f"  - ✅ **Potentially Undervalued**: Intrinsic value is {abs(upside_pct):.1f}% higher than current price")
            else:
                lines.append(f"  - ⚠️ **Potentially Overvalued**: Intrinsic value is {abs(upside_pct):.1f}% lower than current price")
        else:
            lines.append(f"  - If intrinsic value **> current price** → Stock may be **undervalued**")
            lines.append(f"  - If intrinsic value **< current price** → Stock may be **overvalued**")
        lines.append(f"  - Sensitivity table shows valuation range across different assumptions")
        lines.append(f"  - DCF is highly sensitive to WACC and growth rate assumptions")

        return "\n".join(lines)

    def _format_batch_dcf_results(
        self,
        results: list,
        summary: Dict[str, Any],
        tickers: list
    ) -> str:
        """
        Format batch DCF results for AI consumption.

        Returns concise summary table with key metrics for all companies.
        """
        lines = []

        # Header
        lines.append(f"# Batch DCF Results for {len(tickers)} Companies\n")

        # Summary
        successful = summary.get("successful", 0)
        failed = summary.get("failed", 0)
        total_time = summary.get("total_time_ms", 0)

        lines.append(f"## Summary")
        lines.append(f"  - ✅ **Successful**: {successful}/{len(tickers)}")
        lines.append(f"  - ❌ **Failed**: {failed}/{len(tickers)}")
        lines.append(f"  - ⏱️  **Total Time**: {total_time:.0f}ms ({total_time/1000:.1f}s)")
        lines.append("")

        # Results table
        if successful > 0:
            lines.append("## Results\n")

            # Table header
            lines.append("| Ticker | Company | Intrinsic Value | Current Price | Upside | MOS | Valuation |")
            lines.append("|--------|---------|-----------------|---------------|--------|-----|-----------|")

            # Successful results
            for result in results:
                if not result.get("success"):
                    continue

                ticker = result.get("ticker", "N/A")
                dcf = result.get("dcf", {})
                company_name = dcf.get("company_name", "N/A")[:30]  # Truncate

                valuation = dcf.get("valuation", {})
                iv = valuation.get("intrinsic_value_per_share")

                market = dcf.get("market_comparison", {})
                price = market.get("current_price")
                upside = market.get("upside_percent")
                rec = market.get("recommendation", "N/A")

                mos_data = dcf.get("margin_of_safety", {})
                mos = mos_data.get("raw_margin_of_safety")

                # Format values
                iv_str = f"${iv:.2f}" if iv is not None else "N/A"
                price_str = f"${price:.2f}" if price is not None else "N/A"
                upside_str = f"{upside:+.1f}%" if upside is not None else "N/A"
                mos_str = f"{mos*100:.1f}%" if mos is not None else "N/A"

                lines.append(f"| {ticker} | {company_name} | {iv_str} | {price_str} | {upside_str} | {mos_str} | {rec} |")

            lines.append("")

        # Failed results
        if failed > 0:
            lines.append("## Failed Calculations\n")
            for result in results:
                if result.get("success"):
                    continue

                ticker = result.get("ticker", "N/A")
                error = result.get("error", "Unknown error")
                lines.append(f"- **{ticker}**: {error}")

            lines.append("")

        # Insights
        if successful > 0:
            lines.append("## Quick Insights")

            # Count undervalued vs overvalued
            undervalued = 0
            overvalued = 0
            for result in results:
                if not result.get("success"):
                    continue
                market = result.get("dcf", {}).get("market_comparison", {})
                upside = market.get("upside_percent", 0)
                if upside > 0:
                    undervalued += 1
                else:
                    overvalued += 1

            if undervalued > 0:
                lines.append(f"  - ✅ **{undervalued}** potentially undervalued (intrinsic > price)")
            if overvalued > 0:
                lines.append(f"  - ⚠️  **{overvalued}** potentially overvalued (intrinsic < price)")

            # Best opportunity
            best_upside = None
            best_ticker = None
            for result in results:
                if not result.get("success"):
                    continue
                market = result.get("dcf", {}).get("market_comparison", {})
                upside = market.get("upside_percent", 0)
                if upside > 0 and (best_upside is None or upside > best_upside):
                    best_upside = upside
                    best_ticker = result.get("ticker")

            if best_ticker:
                lines.append(f"  - 🎯 **Best Opportunity**: {best_ticker} ({best_upside:+.1f}% upside)")

        return "\n".join(lines)
