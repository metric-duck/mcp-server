"""Base handler with HTTP client for MetricDuck API"""

import httpx
import logging
from typing import Optional, Dict, Any
from ..config import Settings


logger = logging.getLogger(__name__)


class BaseHandler:
    """
    Base handler providing HTTP client for MetricDuck API.

    All tool handlers inherit from this class to access the API via HTTP.
    This ensures complete decoupling - the MCP server communicates with
    the API exactly as external users would.
    """

    def __init__(self, settings: Settings):
        """
        Initialize handler with API client

        Args:
            settings: Configuration settings with API URL and auth
        """
        self.settings = settings
        self.api_base_url = settings.api_base_url.rstrip('/')

        # Build headers with authentication
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "metricduck-mcp/0.3.0"  # Updated version for OAuth support
        }

        # Add authentication headers (OAuth token preferred, API key for backward compatibility)
        try:
            auth_headers = settings.get_auth_headers()
            headers.update(auth_headers)

            # Log auth method (without exposing credentials)
            auth_method = "OAuth 2.1" if settings.access_token else "API Key (legacy)"
            logger.info(f"Using authentication method: {auth_method}")
        except ValueError as e:
            logger.error(f"Authentication configuration error: {e}")
            raise

        # Initialize HTTP client
        self.client = httpx.AsyncClient(
            base_url=self.api_base_url,
            headers=headers,
            timeout=settings.timeout,
            follow_redirects=True
        )

        logger.info(f"Initialized handler with API base URL: {self.api_base_url}")

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make GET request to API

        Args:
            path: API endpoint path (e.g., "/api/v1/companies")
            params: Optional query parameters

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        try:
            logger.debug(f"GET {path} with params: {params}")
            response = await self.client.get(path, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for GET {path}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for GET {path}: {e}")
            raise

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make POST request to API

        Args:
            path: API endpoint path
            json: Optional JSON body
            data: Optional form data

        Returns:
            JSON response as dictionary

        Raises:
            httpx.HTTPStatusError: If request fails
        """
        try:
            logger.debug(f"POST {path} with json: {json}")
            response = await self.client.post(path, json=json, data=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for POST {path}: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for POST {path}: {e}")
            raise

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
        logger.info("Closed HTTP client")

    def _add_feedback_footer(self, response: str) -> str:
        """
        Add feedback prompt to tool response.
        Encourages users to report missing features or data.

        Args:
            response: Tool response text

        Returns:
            Response with feedback footer appended
        """
        footer = """

---
💡 **Missing something?** Tell us what data you need: https://metricduck.com/mcp/feedback"""
        return response + footer

    def _format_error(self, error: Exception) -> str:
        """
        Format error for AI-friendly output with actionable guidance

        Args:
            error: Exception to format

        Returns:
            Human-readable error message with next steps
        """
        if isinstance(error, httpx.HTTPStatusError):
            status = error.response.status_code

            if status == 404:
                return "❌ Resource not found. Please check the ticker symbol or parameters."

            elif status == 401:
                return (
                    "❌ Authentication failed. Your API key is invalid or missing.\n\n"
                    "📋 Next steps:\n"
                    "1. Get an API key at https://metricduck.com/dashboard/api-keys\n"
                    "2. Add it to your MCP config: METRICDUCK_MCP_API_KEY=your_key_here\n"
                    "3. Restart your AI assistant"
                )

            elif status == 403:
                return (
                    "❌ Access forbidden. This feature requires a higher subscription tier.\n\n"
                    "📋 Next steps:\n"
                    "- View plans: https://metricduck.com/pricing\n"
                    "- Upgrade to Professional ($29/mo) or AI Access ($20/mo)"
                )

            elif status == 429:
                # Try to extract quota info from response
                try:
                    error_data = error.response.json()
                    if isinstance(error_data, dict) and 'detail' in error_data:
                        detail = error_data['detail']
                        if isinstance(detail, dict):
                            current = detail.get('current_usage', 'unknown')
                            limit = detail.get('monthly_limit', 'unknown')
                            return (
                                f"❌ Monthly quota exceeded ({current}/{limit} requests used).\n\n"
                                "📋 Next steps:\n"
                                "- Upgrade for higher limits: https://metricduck.com/pricing\n"
                                "- Professional: 100,000 requests/month\n"
                                "- Enterprise: Unlimited"
                            )
                except Exception:
                    pass

                return (
                    "❌ Rate limit exceeded. You've used your monthly quota.\n\n"
                    "📋 Next steps:\n"
                    "- Check usage: https://metricduck.com/dashboard/usage\n"
                    "- Upgrade: https://metricduck.com/pricing"
                )

            elif status >= 500:
                return (
                    "❌ Server error. The MetricDuck API may be experiencing issues.\n\n"
                    "📋 Next steps:\n"
                    "- Try again in a few moments\n"
                    "- Check status: https://status.metricduck.com (if available)\n"
                    "- Report: support@metricduck.com"
                )

            else:
                return f"❌ API error (HTTP {status}): {error.response.text}"

        else:
            return f"❌ Error: {str(error)}"
