"""Value formatting utilities for AI-readable output"""

from typing import Optional


def format_currency(value: Optional[float], decimals: int = 2) -> str:
    """
    Format currency value with appropriate units (B, M, K)

    Args:
        value: Numeric value to format
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "$1.2B", "$500.5M", "$25.3K", "$1,234")

    Examples:
        >>> format_currency(1_200_000_000)
        '$1.20B'
        >>> format_currency(500_500_000)
        '$500.50M'
        >>> format_currency(25_300)
        '$25.30K'
        >>> format_currency(1234)
        '$1,234'
    """
    if value is None:
        return "N/A"

    abs_value = abs(value)
    sign = "-" if value < 0 else ""

    if abs_value >= 1_000_000_000:
        return f"{sign}${abs_value / 1_000_000_000:.{decimals}f}B"
    elif abs_value >= 1_000_000:
        return f"{sign}${abs_value / 1_000_000:.{decimals}f}M"
    elif abs_value >= 1_000:
        return f"{sign}${abs_value / 1_000:.{decimals}f}K"
    else:
        return f"{sign}${abs_value:,.{decimals}f}"


def format_percentage(value: Optional[float], decimals: int = 2) -> str:
    """
    Format percentage value

    Args:
        value: Percentage value (e.g., 15.5 for 15.5%)
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "15.50%")

    Examples:
        >>> format_percentage(15.5)
        '15.50%'
        >>> format_percentage(-5.25)
        '-5.25%'
    """
    if value is None:
        return "N/A"

    return f"{value:.{decimals}f}%"


def format_number(value: Optional[float], decimals: int = 2) -> str:
    """
    Format number with thousands separator

    Args:
        value: Numeric value
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "1,234.56")

    Examples:
        >>> format_number(1234.5678)
        '1,234.57'
        >>> format_number(1000000)
        '1,000,000.00'
    """
    if value is None:
        return "N/A"

    return f"{value:,.{decimals}f}"


def format_ratio(value: Optional[float], decimals: int = 2) -> str:
    """
    Format ratio value (e.g., P/E ratio, debt-to-equity)

    Args:
        value: Ratio value
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "2.50x")

    Examples:
        >>> format_ratio(2.5)
        '2.50x'
        >>> format_ratio(0.75)
        '0.75x'
    """
    if value is None:
        return "N/A"

    return f"{value:.{decimals}f}x"


def format_per_share(value: Optional[float], decimals: int = 2) -> str:
    """
    Format per-share value (e.g., EPS, book value per share)

    Args:
        value: Per-share value
        decimals: Number of decimal places

    Returns:
        Formatted string (e.g., "$5.25")

    Examples:
        >>> format_per_share(5.25)
        '$5.25'
        >>> format_per_share(-0.50)
        '-$0.50'
    """
    if value is None:
        return "N/A"

    sign = "-" if value < 0 else ""
    return f"{sign}${abs(value):.{decimals}f}"
