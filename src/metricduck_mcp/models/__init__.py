"""
Pydantic models for MetricDuck API responses.

⚠️  TEMPORARY DUPLICATION STRATEGY
====================================

These models are copied from api/src/models/ to enable rapid development
without shared package infrastructure. This is a PRAGMATIC approach to start
building the MCP server quickly.

📋 MIGRATION PATH (Phase 2, Month 2-3):
-----------------------------------------
When model duplication becomes painful (3+ models updated frequently):

1. Create shared package at: /packages/metricduck-shared/
2. Move models to: packages/metricduck-shared/src/metricduck_shared/models/
3. Update imports in both services:
   - Before: from src.models.financial_statements import CompanyOverviewResponse
   - After:  from metricduck_shared.models import CompanyOverviewResponse
4. Install shared package in both api/ and mcp-server/ requirements.txt

💡 RATIONALE:
--------------
- START FAST: No shared package setup overhead
- VALIDATE DESIGN: Ensure MCP server architecture is correct first
- LOW RISK: Models are stable (changes infrequent)
- PRAGMATIC: YAGNI principle—don't build shared package until clearly needed

🔍 CURRENT STATUS:
-------------------
- Models last synced: 2025-10-18
- Source: api/src/models/financial_statements.py, api/src/models/base.py
- Subset: Only models needed by MCP tools (not all API models)

When syncing models, search codebase for "TEMPORARY DUPLICATION" to find this file.
"""

from .base import SECFilingMixin
from .financial_statements import (
    CompanySearchResponse,
    CompanyOverviewResponse,
    EarningsInsight,
    EarningsInsightSummary,
    HighlightItem,
    HeadlineItem,
    EarningsMetric,
)

__all__ = [
    "SECFilingMixin",
    "CompanySearchResponse",
    "CompanyOverviewResponse",
    "EarningsInsight",
    "EarningsInsightSummary",
    "HighlightItem",
    "HeadlineItem",
    "EarningsMetric",
]
