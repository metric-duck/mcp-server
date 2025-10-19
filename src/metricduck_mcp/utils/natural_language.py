"""Natural language query utilities for fuzzy matching"""

import logging
from typing import List, Dict, Any, Optional
from rapidfuzz import fuzz, process


logger = logging.getLogger(__name__)

# In-memory cache for company universe
_COMPANY_CACHE: Optional[List[Dict[str, Any]]] = None


async def load_company_universe(api_client) -> List[Dict[str, Any]]:
    """
    Load company universe from API for fuzzy matching

    Args:
        api_client: HTTP client with access to MetricDuck API

    Returns:
        List of company dictionaries with ticker, name, CIK, etc.
    """
    global _COMPANY_CACHE

    if _COMPANY_CACHE is None:
        try:
            logger.info("Loading company universe for fuzzy matching...")
            response = await api_client.get("/api/v1/companies")
            _COMPANY_CACHE = response.get("companies", [])
            logger.info(f"Loaded {len(_COMPANY_CACHE)} companies")
        except Exception as e:
            logger.error(f"Failed to load company universe: {e}")
            _COMPANY_CACHE = []

    return _COMPANY_CACHE


async def fuzzy_match_company(
    query: str,
    api_client,
    limit: int = 5,
    score_cutoff: int = 60
) -> List[Dict[str, Any]]:
    """
    Fuzzy match query against company names and tickers

    Uses RapidFuzz library to find companies matching the query string,
    handling typos, partial matches, and variations in company names.

    Args:
        query: Search query (e.g., "apple", "micro soft", "tsla")
        api_client: HTTP client with access to MetricDuck API
        limit: Maximum number of results to return
        score_cutoff: Minimum similarity score (0-100) to include result

    Returns:
        List of matching company dictionaries, sorted by match score

    Examples:
        >>> await fuzzy_match_company("apple", client, limit=3)
        [
            {"ticker": "AAPL", "company_name": "Apple Inc.", "cik": "0000320193"},
            {"ticker": "APL", "company_name": "Apollo Global Management Inc.", ...},
            ...
        ]
    """
    companies = await load_company_universe(api_client)

    if not companies:
        logger.warning("Company universe is empty, cannot perform fuzzy match")
        return []

    # Create searchable strings: "AAPL - Apple Inc."
    choices = {
        f"{c['ticker']} - {c['company_name']}": c
        for c in companies
    }

    # Use RapidFuzz for fuzzy matching
    matches = process.extract(
        query,
        choices.keys(),
        scorer=fuzz.WRatio,  # Weighted ratio scorer (best for names)
        limit=limit,
        score_cutoff=score_cutoff
    )

    logger.debug(f"Fuzzy matched '{query}' to {len(matches)} companies")

    # Extract company objects from matches
    return [choices[match[0]] for match in matches]


def extract_ticker(query: str) -> Optional[str]:
    """
    Extract ticker symbol from natural language query

    Args:
        query: Natural language query (e.g., "Get AAPL data", "what is MSFT's revenue?")

    Returns:
        Ticker symbol if found, None otherwise

    Examples:
        >>> extract_ticker("Get AAPL data")
        'AAPL'
        >>> extract_ticker("what is MSFT's revenue?")
        'MSFT'
        >>> extract_ticker("Apple's financials")
        None
    """
    import re

    # Match 1-5 uppercase letters (typical ticker pattern)
    match = re.search(r'\b([A-Z]{1,5})\b', query)

    if match:
        ticker = match.group(1)
        logger.debug(f"Extracted ticker '{ticker}' from query '{query}'")
        return ticker

    return None
