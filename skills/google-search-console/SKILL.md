---
name: google-search-console
description: Query Google Search Console (Webmaster Tools) for SEO data — clicks, impressions, average position, CTR, top queries, top pages, indexing status, and sitemaps. Use this skill whenever the user asks about search performance, SEO metrics, Google rankings, search queries driving traffic, indexing issues, crawl status, search impressions, click-through rates, or anything related to how their site appears in Google Search. Also trigger when the user mentions "GSC", "Search Console", "webmaster tools", "Google rankings", or wants to check if a page is indexed.
---

# Google Search Console

Query SEO and search performance data from the Google Search Console API.

## Prerequisites

Install the `searchconsole` Python package (wrapper around the official Google API):

```bash
pip install searchconsole
```

If not installed, fall back to `google-api-python-client`:

```bash
pip install google-api-python-client google-auth google-auth-oauthlib
```

## Credential Setup

GSC requires OAuth 2.0 or a service account — no simple API keys.

### Check for existing credentials

```bash
# Check for serialized searchconsole credentials
ls ~/.config/gsc/credentials.json 2>/dev/null && echo "FOUND: searchconsole credentials"

# Check for service account
echo "${GOOGLE_APPLICATION_CREDENTIALS:-not set}"
ls ~/.config/gsc/service-account.json 2>/dev/null && echo "FOUND: service account"

# Check for gcloud
gcloud auth application-default print-access-token 2>/dev/null && echo "FOUND: gcloud ADC"
```

### First-time setup

If no credentials found, guide the user through the simplest path:

> **One-time GSC setup (~5 minutes):**
>
> 1. Go to https://console.cloud.google.com/apis/credentials
> 2. Create a project (or select existing)
> 3. Enable the "Google Search Console API" under APIs & Services → Library
> 4. Create an **OAuth 2.0 Client ID** (type: Desktop app)
> 5. Download the client secrets JSON
> 6. Save it as `~/.config/gsc/client-secrets.json`
> 7. Run the auth flow (opens browser once):
>    ```bash
>    python3 -c "
>    import searchconsole
>    account = searchconsole.authenticate(
>        client_config='$HOME/.config/gsc/client-secrets.json',
>        serialize='$HOME/.config/gsc/credentials.json'
>    )
>    print('Authenticated. Properties:', [p.url for p in account])
>    "
>    ```
>
> After this, credentials are saved and refresh automatically — no more browser interaction.

**Alternative — Service account (fully headless):**

> 1. Create a service account in Google Cloud Console
> 2. Download the JSON key to `~/.config/gsc/service-account.json`
> 3. In Search Console → Settings → Users, add the service account email as a user
> 4. `export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gsc/service-account.json`

## Querying with the searchconsole package

The `searchconsole` package provides a fluent Python API. Use `python3 -c` or the bundled helper script.

### List properties

```bash
python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
for p in account:
    print(p.url)
"
```

### Top queries (last 28 days)

```bash
python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
prop = account['SITE_URL']
report = prop.query.range('today', days=-28).dimension('query').limit(25).get()
for row in report.rows:
    print(f'{row.query:50s}  clicks={row.clicks}  impressions={row.impressions}  ctr={row.ctr:.1%}  position={row.position:.1f}')
"
```

### Top pages

```bash
python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
prop = account['SITE_URL']
report = prop.query.range('today', days=-28).dimension('page').limit(25).get()
for row in report.rows:
    print(f'{row.page:80s}  clicks={row.clicks}  impressions={row.impressions}  position={row.position:.1f}')
"
```

### Daily trend

```bash
python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
prop = account['SITE_URL']
report = prop.query.range('today', days=-28).dimension('date').get()
for row in report.rows:
    print(f'{row.date}  clicks={row.clicks}  impressions={row.impressions}  ctr={row.ctr:.1%}  position={row.position:.1f}')
"
```

### Filter by query or page

```bash
python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
prop = account['SITE_URL']
report = prop.query.range('today', days=-28).dimension('query').filter('query', 'KEYWORD', 'contains').limit(25).get()
for row in report.rows:
    print(f'{row.query:50s}  clicks={row.clicks}  impressions={row.impressions}  position={row.position:.1f}')
"
```

### By device or country

```bash
python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
prop = account['SITE_URL']
report = prop.query.range('today', days=-28).dimension('device').get()
for row in report.rows:
    print(f'{row.device:10s}  clicks={row.clicks}  impressions={row.impressions}  ctr={row.ctr:.1%}')
"
```

## URL Inspection (Indexing Status)

The `searchconsole` package doesn't cover URL Inspection — use the REST API directly:

```bash
# Get access token from saved credentials
ACCESS_TOKEN=$(python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
print(account.credentials.token)
")

# Inspect a URL
curl -s -X POST "https://searchconsole.googleapis.com/v1/urlInspection/index:inspect" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inspectionUrl": "https://example.com/page",
    "siteUrl": "https://example.com/"
  }' | jq '.inspectionResult.indexStatusResult | {verdict, coverageState, lastCrawlTime, pageFetchState, indexingState, robotsTxtState, googleCanonical}'
```

Key fields: `verdict` (PASS/PARTIAL/FAIL/NEUTRAL), `coverageState`, `lastCrawlTime`.

Quota: 2,000 inspections/day per property.

## Sitemaps

```bash
ACCESS_TOKEN=$(python3 -c "
import searchconsole
account = searchconsole.authenticate(
    client_config='$HOME/.config/gsc/client-secrets.json',
    serialize='$HOME/.config/gsc/credentials.json')
print(account.credentials.token)
")

# List sitemaps
curl -s "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/sitemaps" \
  -H "Authorization: Bearer $ACCESS_TOKEN" | jq '.sitemap[] | {path, lastSubmitted, isPending, warnings, errors}'

# Submit a sitemap
curl -s -X PUT "https://searchconsole.googleapis.com/webmasters/v3/sites/ENCODED_SITE_URL/sitemaps/ENCODED_SITEMAP_URL" \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

## Service Account Fallback

If using a service account instead of OAuth:

```bash
python3 -c "
from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

creds = service_account.Credentials.from_service_account_file(
    os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', os.path.expanduser('~/.config/gsc/service-account.json')),
    scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
service = build('webmasters', 'v3', credentials=creds)

response = service.searchanalytics().query(
    siteUrl='SITE_URL',
    body={
        'startDate': '$(date -v-28d +%Y-%m-%d)',
        'endDate': '$(date -v-3d +%Y-%m-%d)',
        'dimensions': ['query'],
        'rowLimit': 25
    }).execute()

for row in response.get('rows', []):
    q = row['keys'][0]
    print(f\"{q:50s}  clicks={row['clicks']}  impressions={row['impressions']}  ctr={row['ctr']:.1%}  position={row['position']:.1f}\")
"
```

## Presenting Results

Format results as clean tables. For CTR, multiply by 100 and show as percentage. Round position to 1 decimal. Default to last 28 days (minus 3 days for data freshness) if no date range specified.

When the user asks a vague question like "how's my SEO" or "how's search going", provide: total clicks/impressions/avg position for the period, top 10 queries, and top 10 pages by clicks.

## Constraints

- Data has a 2-3 day processing lag — use `dataState: "all"` for fresher (but partial) data
- Historical data available for ~16 months
- Max 25,000 rows per request — paginate with `startRow` for larger exports
- Rate limit: 1,200 requests/minute per project
- URL Inspection: 2,000/day per property
- Country codes are ISO 3166-1 alpha-3 (e.g. `USA`, `GBR`, `ZAF`)
