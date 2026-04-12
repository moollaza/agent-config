---
name: google-search-console
description: Query Google Search Console (Webmaster Tools) for SEO data — clicks, impressions, average position, CTR, top queries, top pages, indexing status, and sitemaps. Use this skill whenever the user asks about search performance, SEO metrics, Google rankings, search queries driving traffic, indexing issues, crawl status, search impressions, click-through rates, or anything related to how their site appears in Google Search. Also trigger when the user mentions "GSC", "Search Console", "webmaster tools", "Google rankings", or wants to check if a page is indexed.
---

# Google Search Console

Query SEO and search performance data from the Google Search Console API.

## Credential Setup

Google Search Console requires OAuth 2.0 or a service account — API keys alone don't work.

Check for credentials in this order:

1. **Service account JSON:** Look for `GOOGLE_APPLICATION_CREDENTIALS` env var, or `~/.config/gcloud/application_default_credentials.json`
2. **OAuth refresh token:** Check for `GSC_REFRESH_TOKEN`, `GSC_CLIENT_ID`, `GSC_CLIENT_SECRET` env vars
3. **gcloud CLI:** Check if `gcloud` is installed and authenticated: `gcloud auth application-default print-access-token 2>/dev/null`

If none are found, guide the user through setup:

> No Google Search Console credentials found. Choose a setup method:
>
> **Option A — Service Account (recommended for automation):**
> 1. Go to https://console.cloud.google.com → APIs & Services → Credentials
> 2. Create a service account, download the JSON key
> 3. `export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json`
> 4. In Search Console, add the service account email as a property user
>
> **Option B — gcloud CLI:**
> 1. `brew install google-cloud-sdk` (if needed)
> 2. `gcloud auth application-default login --scopes=https://www.googleapis.com/auth/webmasters.readonly`
>
> **Option C — OAuth refresh token:**
> 1. Create OAuth 2.0 Desktop credentials in Google Cloud Console
> 2. Run the one-time auth flow, store the refresh token
> 3. Set `GSC_CLIENT_ID`, `GSC_CLIENT_SECRET`, `GSC_REFRESH_TOKEN` env vars

### Getting an access token

Once credentials exist, get a bearer token:

```bash
# Via gcloud (simplest)
ACCESS_TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null)

# Via service account (using Python — one-liner)
ACCESS_TOKEN=$(python3 -c "
import json, time, jwt, urllib.request
sa = json.load(open('$GOOGLE_APPLICATION_CREDENTIALS'))
now = int(time.time())
payload = {'iss': sa['client_email'], 'scope': 'https://www.googleapis.com/auth/webmasters.readonly', 'aud': 'https://oauth2.googleapis.com/token', 'iat': now, 'exp': now + 3600}
signed = jwt.encode(payload, sa['private_key'], algorithm='RS256')
data = urllib.parse.urlencode({'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'assertion': signed}).encode()
resp = json.loads(urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data)).read())
print(resp['access_token'])
")
```

## API Reference

**Base URL:** `https://searchconsole.googleapis.com`

### Step 1: Identify the property

List accessible properties:

```bash
curl -s "https://searchconsole.googleapis.com/webmasters/v3/sites" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.siteEntry[] | {siteUrl, permissionLevel}'
```

Site URLs come in two forms:
- URL-prefix: `https://example.com/` (URL-encode as `https%3A%2F%2Fexample.com%2F`)
- Domain: `sc-domain:example.com` (URL-encode as `sc-domain%3Aexample.com`)

### Step 2: Query search analytics

The main endpoint for all search performance data:

```bash
curl -s -X POST "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/searchAnalytics/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

**Request body:**

| Field | Required | Values |
|-------|----------|--------|
| `startDate` | Yes | `YYYY-MM-DD` |
| `endDate` | Yes | `YYYY-MM-DD` |
| `dimensions` | No | Array: `query`, `page`, `country`, `device`, `date`, `searchAppearance` |
| `type` | No | `web` (default), `image`, `video`, `news`, `discover`, `googleNews` |
| `dimensionFilterGroups` | No | Array of filter groups (see below) |
| `rowLimit` | No | 1–25000 (default 1000) |
| `startRow` | No | Offset for pagination (0-indexed) |
| `aggregationType` | No | `auto`, `byPage`, `byProperty` |
| `dataState` | No | `final` (default, 2-3 day lag) or `all` (includes fresh partial data) |

**Filter syntax:**
```json
{
  "dimensionFilterGroups": [{
    "filters": [
      {"dimension": "query", "operator": "contains", "expression": "keyword"},
      {"dimension": "country", "operator": "equals", "expression": "ZAF"}
    ]
  }]
}
```
Operators: `contains`, `equals`, `notContains`, `notEquals`, `includingRegex`, `excludingRegex`

Country codes are ISO 3166-1 alpha-3 (e.g. `USA`, `GBR`, `ZAF`). Device values: `DESKTOP`, `MOBILE`, `TABLET`.

**Response:**
```json
{
  "rows": [
    {"keys": ["search query", "https://example.com/page"], "clicks": 150, "impressions": 3200, "ctr": 0.046875, "position": 4.2}
  ]
}
```
- `keys` corresponds to `dimensions` in same order
- `ctr` is 0.0–1.0 (multiply by 100 for percentage)
- `position` is 1-indexed (1 = top)
- Fewer rows than `rowLimit` means end of data

### Common Queries

**Top queries (last 28 days):**
```bash
curl -s -X POST "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/searchAnalytics/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -v-28d +%Y-%m-%d)'",
    "endDate": "'$(date -v-3d +%Y-%m-%d)'",
    "dimensions": ["query"],
    "rowLimit": 25,
    "aggregationType": "byProperty"
  }' | jq '.rows | sort_by(-.clicks) | .[:25]'
```

**Top pages by clicks:**
```bash
curl -s -X POST "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/searchAnalytics/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -v-28d +%Y-%m-%d)'",
    "endDate": "'$(date -v-3d +%Y-%m-%d)'",
    "dimensions": ["page"],
    "rowLimit": 25
  }' | jq '.rows | sort_by(-.clicks) | .[:25]'
```

**Daily click/impression trend:**
```bash
curl -s -X POST "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/searchAnalytics/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -v-28d +%Y-%m-%d)'",
    "endDate": "'$(date -v-3d +%Y-%m-%d)'",
    "dimensions": ["date"]
  }' | jq '.rows'
```

**Performance by device:**
```bash
curl -s -X POST "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/searchAnalytics/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -v-28d +%Y-%m-%d)'",
    "endDate": "'$(date -v-3d +%Y-%m-%d)'",
    "dimensions": ["device"]
  }' | jq '.rows'
```

**Performance by country:**
```bash
curl -s -X POST "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/searchAnalytics/query" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "startDate": "'$(date -v-28d +%Y-%m-%d)'",
    "endDate": "'$(date -v-3d +%Y-%m-%d)'",
    "dimensions": ["country"],
    "rowLimit": 20
  }' | jq '.rows | sort_by(-.clicks)'
```

### URL Inspection (Indexing Status)

Check if a specific URL is indexed:

```bash
curl -s -X POST "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inspectionUrl": "https://example.com/page",
    "siteUrl": "https://example.com/"
  }' | jq '.inspectionResult.indexStatusResult | {verdict, coverageState, lastCrawlTime, pageFetchState, indexingState, robotsTxtState, googleCanonical}'
```

Key fields: `verdict` (PASS/PARTIAL/FAIL/NEUTRAL), `coverageState`, `lastCrawlTime`, `pageFetchState`.

Quota: 2,000 inspections/day per property, 600/minute.

### Sitemaps

```bash
# List sitemaps
curl -s "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/sitemaps" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.sitemap[] | {path, lastSubmitted, isPending, warnings, errors}'

# Submit a sitemap
curl -s -X PUT "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/sitemaps/ENCODED_SITEMAP_URL" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Presenting Results

Format results as clean tables. For CTR, multiply by 100 and show as percentage. Round position to 1 decimal place. Default to last 28 days (minus 3 days for data freshness) if no date range specified.

When the user asks a vague question like "how's my SEO" or "how's search going", provide: total clicks/impressions/avg position for the period, top 10 queries, and top 10 pages by clicks.

### Constraints

- Data has a 2-3 day processing lag — use `dataState: "all"` for fresher (but partial) data
- Historical data available for ~16 months
- Max 25,000 rows per request — paginate with `startRow` for larger exports
- Rate limit: 1,200 requests/minute per project
- URL Inspection: 2,000/day per property
