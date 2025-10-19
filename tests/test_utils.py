"""Tests for utility modules"""

import pytest
from metricduck_mcp.utils.formatting import (
    format_currency,
    format_percentage,
    format_ratio,
    format_per_share,
    format_number
)
from metricduck_mcp.utils.natural_language import extract_ticker


class TestFormatting:
    """Tests for formatting utilities"""

    def test_format_currency_billions(self):
        """Test currency formatting for billions"""
        assert format_currency(1_200_000_000) == "$1.20B"
        assert format_currency(5_500_000_000) == "$5.50B"

    def test_format_currency_millions(self):
        """Test currency formatting for millions"""
        assert format_currency(500_000_000) == "$500.00M"
        assert format_currency(1_500_000) == "$1.50M"

    def test_format_currency_thousands(self):
        """Test currency formatting for thousands"""
        assert format_currency(25_000) == "$25.00K"
        assert format_currency(500_000) == "$500.00K"

    def test_format_currency_small_amounts(self):
        """Test currency formatting for small amounts"""
        assert format_currency(500) == "$500.00"
        assert format_currency(1234.56) == "$1,234.56"

    def test_format_currency_negative(self):
        """Test currency formatting for negative values"""
        assert format_currency(-1_000_000_000) == "-$1.00B"
        assert format_currency(-500_000) == "-$500.00K"

    def test_format_currency_none(self):
        """Test currency formatting for None"""
        assert format_currency(None) == "N/A"

    def test_format_percentage(self):
        """Test percentage formatting"""
        assert format_percentage(15.5) == "15.50%"
        assert format_percentage(-5.25) == "-5.25%"
        assert format_percentage(100.0) == "100.00%"
        assert format_percentage(None) == "N/A"

    def test_format_ratio(self):
        """Test ratio formatting"""
        assert format_ratio(2.5) == "2.50x"
        assert format_ratio(0.75) == "0.75x"
        assert format_ratio(None) == "N/A"

    def test_format_per_share(self):
        """Test per-share formatting"""
        assert format_per_share(5.25) == "$5.25"
        assert format_per_share(-0.50) == "-$0.50"
        assert format_per_share(None) == "N/A"

    def test_format_number(self):
        """Test number formatting"""
        assert format_number(1234.5678) == "1,234.57"
        assert format_number(1_000_000) == "1,000,000.00"
        assert format_number(None) == "N/A"


class TestNaturalLanguage:
    """Tests for natural language utilities"""

    def test_extract_ticker_simple(self):
        """Test ticker extraction from simple queries"""
        assert extract_ticker("Get AAPL data") == "AAPL"
        assert extract_ticker("What is MSFT's revenue?") == "MSFT"
        assert extract_ticker("TSLA earnings") == "TSLA"

    def test_extract_ticker_multiple(self):
        """Test ticker extraction when multiple tickers present"""
        # Should return first ticker found
        result = extract_ticker("Compare AAPL and MSFT")
        assert result in ["AAPL", "MSFT"]

    def test_extract_ticker_no_ticker(self):
        """Test ticker extraction when no ticker present"""
        assert extract_ticker("Apple's financials") is None
        assert extract_ticker("microsoft revenue") is None

    def test_extract_ticker_lowercase(self):
        """Test that lowercase letters are not extracted"""
        # Only uppercase 1-5 letter sequences should be tickers
        assert extract_ticker("I like apple") is None
        assert extract_ticker("Get data") is None
