---
name: bing-webmaster
description: Query Bing Webmaster Tools API for search data — clicks, impressions, rankings, crawl stats, keyword research, backlinks, and URL submission. Use this skill whenever the user asks about Bing search performance, Bing rankings, Bing indexing, keyword research, backlink analysis, or wants to submit URLs to Bing. Also trigger when the user mentions "Bing", "Bing Webmaster", wants to compare Google vs Bing performance, needs keyword volume data, or wants to check how their site performs on Bing — even if they don't explicitly say "Bing Webmaster Tools".
---

# Bing Webmaster Tools

Query search performance, crawl data, keywords, and backlinks via the Bing Webmaster API.

## Credential Setup

Retrieve the API key in this order:

1. Environment variable: `$BING_WEBMASTER_API_KEY`
2. macOS Keychain: `security find-generic-password -s "bing-webmaster-api-key" -w 2>/dev/null`

If not found:

> No Bing Webmaster API key found. Set one up:
> 1. Sign in at https://www.bing.com/webmasters
> 2. Add and verify your site(s)
> 3. Settings (top right) → API Access → Generate API Key
> 4. Either `export BING_WEBMASTER_API_KEY=your_key` or store in Keychain:
>    `security add-generic-password -s "bing-webmaster-api-key" -a "bing" -w "your_key"`

One API key covers all verified sites — no per-site keys needed.

```bash
BING_KEY="${BING_WEBMASTER_API_KEY:-$(security find-generic-password -s "bing-webmaster-api-key" -w 2>/dev/null)}"
```

## API Reference

**Base URL:** `https://ssl.bing.com/webmaster/api.svc/json`
**Auth:** API key as query parameter `?apikey=$BING_KEY`

All responses are wrapped in `{"d": ...}`. Dates use WCF format (`/Date(1316156400000)/`) — parse epoch millis.

### Step 1: Identify the site

Check the service registry first:

```bash
jq '.projects["zaahir-ca"].domains[0]' ~/.claude/service-registry.json
```

Or list all verified sites:

```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetUserSites?apikey=$BING_KEY" \
  | jq '.d[] | {Url, IsVerified}'
```

Site URLs must be URL-encoded in all API calls (e.g. `http%3A%2F%2Fexample.com`).

### Traffic & Rankings

**Daily clicks and impressions:**
```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetRankAndTrafficStats?siteUrl=https%3A%2F%2Fexample.com&apikey=$BING_KEY" \
  | jq '.d[] | {Clicks, Impressions, Date}'
```

**Top queries (with position data, updated weekly):**
```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetQueryStats?siteUrl=https%3A%2F%2Fexample.com&apikey=$BING_KEY" \
  | jq '.d[] | {Query, Clicks, Impressions, AvgClickPosition, AvgImpressionPosition}'
```

**Top pages:**
```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetPageStats?siteUrl=https%3A%2F%2Fexample.com&apikey=$BING_KEY" \
  | jq '.d[] | {Query: .Query, Clicks, Impressions, AvgClickPosition}'
```
Note: the `Query` field contains the page URL for PageStats.

**Queries driving traffic to a specific page:**
```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetPageQueryStats?siteUrl=https%3A%2F%2Fexample.com&page=https%3A%2F%2Fexample.com%2Fblog&apikey=$BING_KEY" \
  | jq '.d[] | {Query, Clicks, Impressions, AvgClickPosition}'
```

**Daily trend for a specific query:**
```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetQueryTrafficStats?siteUrl=https%3A%2F%2Fexample.com&query=my+keyword&apikey=$BING_KEY" \
  | jq '.d[] | {Clicks, Impressions, Date}'
```

### Crawl Data

**Crawl stats (last 6 months, daily):**
```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetCrawlStats?siteUrl=https%3A%2F%2Fexample.com&apikey=$BING_KEY" \
  | jq '.d[] | {Date, CrawledPages, InIndex, Code2xx, Code4xx, Code5xx, CrawlErrors}'
```

**Crawl issues:**
```bash
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetCrawlIssues?siteUrl=https%3A%2F%2Fexample.com&apikey=$BING_KEY" \
  | jq '.d[] | {Url, HttpCode, Issues}'
```

### URL Submission

```bash
# Check remaining quota
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetUrlSubmissionQuota?siteUrl=https%3A%2F%2Fexample.com&apikey=$BING_KEY" \
  | jq '.d | {DailyQuota, MonthlyQuota}'

# Submit single URL
curl -s -X POST "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrl?apikey=$BING_KEY" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"siteUrl":"https://example.com","url":"https://example.com/new-page"}'

# Submit batch (up to 500 URLs)
curl -s -X POST "https://ssl.bing.com/webmaster/api.svc/json/SubmitUrlBatch?apikey=$BING_KEY" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"siteUrl":"https://example.com","urlList":["https://example.com/page1","https://example.com/page2"]}'
```

### Keyword Research

These endpoints work without site ownership — useful for content planning and competitive analysis.

```bash
# Keyword volume (specify country + language + date range)
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetKeyword?q=prayer+times&country=us&language=en&startDate=2026-01-01&endDate=2026-03-31&apikey=$BING_KEY" \
  | jq '.d | {Query, Impressions, BroadImpressions}'

# Related keywords
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetRelatedKeywords?q=prayer+times&country=us&language=en&startDate=2026-01-01&endDate=2026-03-31&apikey=$BING_KEY" \
  | jq '.d[] | {Query, Impressions, BroadImpressions}'
```

Country codes: 2-letter (e.g. `us`, `ca`, `gb`, `za`). Language: 2-letter (e.g. `en`, `fr`).

### Backlinks

```bash
# Pages with inbound links (paginated, page=0 is first)
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetLinkCounts?siteUrl=https%3A%2F%2Fexample.com&page=0&apikey=$BING_KEY" \
  | jq '.d | {TotalPages, Links: [.Links[] | {Url, Count}]}'

# Inbound links to a specific URL (with anchor text)
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetUrlLinks?siteUrl=https%3A%2F%2Fexample.com&link=https%3A%2F%2Fexample.com%2Fpage&page=0&apikey=$BING_KEY" \
  | jq '.d | {TotalPages, Details: [.Details[] | {Url, AnchorText}]}'
```

### Sitemaps

```bash
# List sitemaps
curl -s "https://ssl.bing.com/webmaster/api.svc/json/GetFeeds?siteUrl=https%3A%2F%2Fexample.com&apikey=$BING_KEY" \
  | jq '.d[] | {Url, Status, LastCrawled, UrlCount}'

# Submit sitemap
curl -s -X POST "https://ssl.bing.com/webmaster/api.svc/json/SubmitFeed?apikey=$BING_KEY" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{"siteUrl":"https://example.com","feedUrl":"https://example.com/sitemap.xml"}'
```

### Presenting Results

Format results as clean tables. For WCF dates, convert epoch millis to readable dates. When the user asks a vague question like "how's my Bing performance", show: total clicks/impressions trend, top 10 queries, and crawl health summary.

When comparing with GSC data, note that Bing traffic includes all verticals (Web, Chat, News, Images, Videos, Knowledge Panel) since March 2023.

### Unique Capabilities vs Google Search Console

Bing Webmaster has features GSC doesn't:
- **Keyword research** — volume data for any keyword, no site ownership needed
- **Backlink data** — inbound links with anchor text
- **Content submission** — push HTML directly to Bing's index
- **Batch URL submission** — up to 500 URLs at once
- **Simpler auth** — API key, no OAuth dance

### Constraints

- Traffic data (daily): updated daily
- Query/page stats: updated weekly
- Crawl stats: last 6 months available
- URL submission: check quota with GetUrlSubmissionQuota before bulk submitting
- Site URLs must be URL-encoded in all requests
