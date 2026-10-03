# MetricDuck MCP — SEC filings, financials and earnings for AI agents

MetricDuck is a **hosted remote MCP server**. It answers questions about public companies from their SEC filings: 10-K, 10-Q and 8-K text, financial statements and metrics, earnings calls and guidance. Every figure traces back to the filing it came from. There is nothing to install.

```
https://mcp.metricduck.com/mcp
```

Streamable HTTP, with OAuth sign-in (Google or GitHub) on first use. **Free tier, no card.** Setup guide: [metricduck.com/mcp/setup](https://www.metricduck.com/mcp/setup)

## Connect

**Claude (claude.ai and Claude Desktop):** MetricDuck is in Claude's connector directory. Go to **Customize → Connectors**, search "MetricDuck" and click **Connect**. If it isn't listed for you, choose **Customize → Connectors → Add custom connector**, paste the URL above and click **Add**. This works on every Claude plan, including Free.

**ChatGPT:** open the [MetricDuck app](https://chatgpt.com/apps/metricduck/asdk_app_6a283782f9d48191a3422b95827b227b), press **Connect**, then **Sign in with MetricDuck**. In a new chat, type **@MetricDuck** followed by your question.

**Claude Code:**

```bash
claude mcp add --transport http -s user metricduck https://mcp.metricduck.com/mcp
```

**Cursor, Codex, Windsurf, VS Code and other MCP clients:** add the URL as a remote (HTTP) server. For example, in `.mcp.json` or `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "metricduck": {
      "type": "http",
      "url": "https://mcp.metricduck.com/mcp"
    }
  }
}
```

Your client opens a browser once to sign in, and it's automatic after that. For headless agents, create an API key at [metricduck.com/dashboard/api-keys](https://www.metricduck.com/dashboard/api-keys).

## Try asking

- "What risks did Nvidia add in its latest 10-K?"
- "Compare Apple's and Microsoft's operating margins over the last 5 years."
- "What guidance did Tesla give on its latest earnings call?"

## What it covers

- **SEC filing text:** sections of 10-K, 10-Q, 8-K, DEF 14A, 20-F, 40-F and 6-K filings (risk factors, MD&A, business, legal proceedings), quoted from the filing.
- **Financials:** statements and 250+ pre-computed metrics (margins, free cash flow, ROIC, balance sheet), quarterly and annual history, and XBRL facts with lineage back to the filing.
- **Screening and comparison** across 5,500+ US public companies and the foreign private issuers that file with the SEC.
- **Earnings:** earnings-call content and guidance compared with actual results. Each is labeled by source: SEC-filed, issuer-published or machine-transcribed.
- **8-K material events** and recent filings across the market.
- **End-of-day prices** and the valuation multiples built on them (P/E, EV/EBITDA).

Data is updated daily from SEC EDGAR. **Not covered:** intraday prices, options, analyst estimates, Form 4 insider trades and 13F holdings.

## For agents

- Server URL: `https://mcp.metricduck.com/mcp` (MCP registry name `com.metricduck/financial-analysis`; see [`server.json`](server.json))
- Site summary for LLMs: [metricduck.com/llms.txt](https://www.metricduck.com/llms.txt)
- The server's own instructions and tool descriptions explain which tool fits which question. Quote figures exactly as the tools return them.

## Links

[Website](https://www.metricduck.com) · [Setup guide](https://www.metricduck.com/mcp/setup) · [Pricing](https://www.metricduck.com/pricing) · [Contact](https://www.metricduck.com/contact) · [Privacy](https://www.metricduck.com/mcp/privacy) · [Terms](https://www.metricduck.com/terms)

---

The early local Python package (`metricduck-mcp` 0.0.2) is preserved at tag [`v0.0.2`](https://github.com/metric-duck/mcp-server/tree/v0.0.2). The hosted server above replaces it.
