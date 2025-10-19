"""
Base models and mixins for API responses

⚠️ TEMPORARY: Copied from api/src/models/base.py
See models/__init__.py for migration plan.
"""

from pydantic import BaseModel, computed_field
from typing import Optional


class SECFilingMixin(BaseModel):
    """
    Mixin providing SEC EDGAR filing URL generation for financial statements.

    Automatically generates sec_filing_url from cik and accession_number fields.
    Used by all financial statement models (income statement, balance sheet, cash flow, ROIC).

    Example:
        CIK: "0000063908"
        Accession: "0000063908-25-000012"
        → https://www.sec.gov/Archives/edgar/data/63908/000006390825000012/0000063908-25-000012-index.htm
    """

    cik: str
    accession_number: Optional[str] = None

    @computed_field
    @property
    def sec_filing_url(self) -> Optional[str]:
        """
        Generate SEC EDGAR filing index URL.

        Returns:
            URL string if accession_number exists, None otherwise
        """
        if not self.accession_number:
            return None

        # Strip leading zeros from CIK for URL (0000063908 → 63908)
        cik_unpadded = self.cik.lstrip('0')

        # Remove dashes from accession number for path (0000063908-25-000012 → 000006390825000012)
        accn_no_dashes = self.accession_number.replace('-', '')

        # SEC EDGAR URL format
        return f"https://www.sec.gov/Archives/edgar/data/{cik_unpadded}/{accn_no_dashes}/{self.accession_number}-index.htm"
