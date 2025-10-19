"""
Pydantic models for MetricDuck API financial data responses.

⚠️ TEMPORARY: Subset of models copied from api/src/models/financial_statements.py
See models/__init__.py for migration plan.

This file contains ONLY the models needed by MCP tools:
- Company search and overview
- Earnings insights
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime


# ============================================================================
# Company Models
# ============================================================================

class CompanySearchResponse(BaseModel):
    """Company search result"""
    ticker: str
    company_name: str
    cik: str
    sic_code: Optional[str] = None
    business_description: Optional[str] = None


class CompanyOverviewResponse(BaseModel):
    """Company overview with key statistics"""
    ticker: str
    company_name: str
    cik: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None
    as_of_date_ttm: Optional[str] = None
    as_of_date_mrq: Optional[str] = None

    # Valuation (TTM/Current)
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    ev_sales: Optional[float] = None
    ev_fcf: Optional[float] = None
    market_cap: Optional[float] = None
    ev: Optional[float] = None

    # Profitability (TTM)
    net_income: Optional[float] = None
    eps_diluted: Optional[float] = None
    revenues: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    fcf_margin: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    roic_v1: Optional[float] = None
    roic_v2: Optional[float] = None
    roic_v3: Optional[float] = None

    # Time-series data for sparklines (8Q)
    revenues_8q: Optional[List[Optional[float]]] = None
    net_income_8q: Optional[List[Optional[float]]] = None
    free_cash_flow_8q: Optional[List[Optional[float]]] = None

    # Cash Flow (TTM)
    operating_cash_flow: Optional[float] = None
    free_cash_flow: Optional[float] = None

    # Balance Sheet (MRQ)
    total_debt: Optional[float] = None
    cash_and_investments: Optional[float] = None
    shares_basic: Optional[float] = None
    debt_to_equity: Optional[float] = None
    debt_to_assets: Optional[float] = None


# ============================================================================
# Earnings Insights Models
# ============================================================================

class HighlightItem(BaseModel):
    """Highlight with sentiment signal"""
    text: str
    signal: str  # positive, neutral, negative, attention


class HeadlineItem(BaseModel):
    """Headline item for anomalies or notable events"""
    text: str
    type: str  # record, anomaly, strategic, special_item, notable


class EarningsMetric(BaseModel):
    """Metric with quarterly and annual values"""
    q_current: Optional[float] = None
    q_prior_year: Optional[float] = None
    annual_current: Optional[float] = None
    annual_prior_year: Optional[float] = None
    yoy_growth: Optional[float] = None

    @classmethod
    def from_processor_format(cls, data: Dict[str, Any]) -> 'EarningsMetric':
        """Convert from processor's FinancialMetric format"""
        return cls(
            q_current=data.get('q_current'),
            q_prior_year=data.get('q_prior_year'),
            annual_current=data.get('fy_current'),
            annual_prior_year=data.get('fy_prior_year'),
            yoy_growth=data.get('growth_pct')
        )


class EarningsInsightSummary(BaseModel):
    """Summary of earnings insight for list views"""
    cik: str
    ticker: Optional[str] = None
    company_name: str
    filing_date: date
    fiscal_period: str
    fiscal_year: Optional[int] = None
    accession_number: str
    revenue_current: Optional[float] = None
    revenue_growth_yoy: Optional[float] = None
    net_income_current: Optional[float] = None
    net_income_growth_yoy: Optional[float] = None
    eps_diluted_current: Optional[float] = None
    eps_diluted_growth_yoy: Optional[float] = None
    extraction_confidence: Optional[float] = None
    processed_at: Optional[datetime] = None
    rank: Optional[int] = None

    # Optional detailed fields
    positive_highlights: Optional[List[HighlightItem]] = None
    concerns: Optional[List[HighlightItem]] = None
    headline_items: Optional[List[HeadlineItem]] = None


class EarningsInsight(BaseModel):
    """LLM-extracted earnings insights from 8-K releases"""
    # Identifiers
    cik: str
    company_name: str
    ticker: Optional[str] = None
    accession_number: str

    # Period information
    filing_date: date
    fiscal_period: str
    fiscal_year: int

    # LLM-extracted insights
    executive_summary: str
    positive_highlights: List[HighlightItem] = []
    concerns: List[HighlightItem] = []
    headline_items: List[HeadlineItem] = []
    key_highlights: List[str] = []
    financial_performance: Dict[str, Any]

    # Key metrics
    revenue: EarningsMetric
    net_income: EarningsMetric
    eps_diluted: EarningsMetric

    # Quality metadata
    extraction_confidence: float
    llm_model: str
    processing_cost_usd: float
    processed_at: datetime
