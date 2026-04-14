---
name: fathom-analytics
description: Query the Fathom Analytics API for website traffic data — pageviews, top pages, referrers, conversions, current visitors, and time-series analytics. Use this skill whenever the user asks about website analytics, traffic, pageviews, visitors, top pages, referrers, bounce rate, Fathom, site stats, conversion tracking, or website performance metrics. Also use when the user wants to check how a page or blog post is performing, compare traffic periods, see where visitors come from, or monitor real-time visitors — even if they don't mention "Fathom" by name.
---

# Fathom Analytics

Query website analytics from the Fathom Analytics API.

## Credential Setup

Retrieve the API key in this order:

1. Environment variable: `$FATHOM_API_KEY`
2. macOS Keychain: `security find-generic-password -s "fathom-api-key" -w 2>/dev/null`

If neither is found, tell the user:

> No Fathom API key found. Set one up:
> 1. Get a token from https://app.usefathom.com/api
> 2. Either `export FATHOM_API_KEY=your_token` or store in Keychain:
>    `security add-generic-password -s "fathom-api-key" -a "fathom" -w "your_token"`

Store the resolved key in a shell variable for the session:

```bash
FATHOM_API_KEY="${FATHOM_API_KEY:-$(security find-generic-password -s "fathom-api-key" -w 2>/dev/null)}"
```

## API Reference

**Base URL:** `https://api.usefathom.com/v1`
**Auth header:** `Authorization: Bearer $FATHOM_API_KEY`

### Step 1: Identify the site

Check the service registry first to avoid unnecessary API calls:

```bash
# Look up by project name or domain
jq '.projects["repo-remover"].fathom' ~/.claude/service-registry.json
# Or find by domain
jq '.projects[] | select(.domains[] == "zaahir.ca") | .fathom' ~/.claude/service-registry.json
```

If the project isn't in the registry, fall back to listing sites:

```bash
curl -s "https://api.usefathom.com/v1/sites" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq '.data[] | {id, name}'
```

Response is cursor-paginated: `data[]` array with `has_more` boolean. Use `starting_after` for next page.

### Event Tracking and Funnels

The registry includes tracked events per site. Query event conversions to understand funnels:

```bash
# Get conversion data for a specific event
curl -s "https://api.usefathom.com/v1/aggregations?entity=event&site_id=SITE_ID&entity_name=EVENT_NAME&aggregates=conversions,unique_conversions,value&date_from=$(date -v-30d +%Y-%m-%d)%2000:00:00" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq

# Get all events for a site
curl -s "https://api.usefathom.com/v1/sites/SITE_ID/events" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq '.data[] | {id, name}'

# Compare multiple events over time (funnel stages)
# Run one query per funnel step and compare conversion counts
```

When the user asks about funnels or conversions, check the registry for known events and query each stage to show drop-off between steps.

### Step 2: Query analytics

The `/aggregations` endpoint handles all reporting. Build queries by combining these parameters:

| Parameter | Required | Values |
|-----------|----------|--------|
| `entity` | Yes | `pageview` or `event` |
| `entity_id` | Yes (pageview) | Site ID |
| `site_id` + `entity_name` | Yes (event) | Site ID + event name |
| `aggregates` | Yes | See below |
| `date_from` | No | `YYYY-MM-DD HH:MM:SS` (in timezone) |
| `date_to` | No | `YYYY-MM-DD HH:MM:SS` (defaults to now) |
| `date_grouping` | No | `hour`, `day`, `month`, `year` |
| `field_grouping` | No | Comma-separated dimensions |
| `sort_by` | No | `field:asc` or `field:desc` |
| `timezone` | No | TZ name (e.g. `Africa/Johannesburg`), default UTC |
| `limit` | No | Max rows returned |
| `filters` | No | JSON array of filter objects |

**Pageview aggregates:** `visits`, `uniques`, `pageviews`, `avg_duration`, `bounce_rate`

**Event aggregates:** `conversions`, `unique_conversions`, `value` (returned in cents — divide by 100)

**Grouping dimensions:** `pathname`, `hostname`, `referrer_hostname`, `referrer_pathname`, `referrer_source`, `browser`, `country_code`, `city`, `region`, `device_type`, `operating_system`, `utm_campaign`, `utm_content`, `utm_medium`, `utm_source`, `utm_term`

**Filter syntax:**
```json
[{"property": "pathname", "operator": "is like", "value": "/blog%"}]
```
Operators: `is`, `is not`, `is like`, `is not like`, `matching` (regex), `not matching`

### Common Queries

**Top pages (last 30 days):**
```bash
curl -s "https://api.usefathom.com/v1/aggregations?entity=pageview&entity_id=SITE_ID&aggregates=pageviews,visits,uniques&field_grouping=pathname&sort_by=pageviews:desc&date_from=$(date -v-30d +%Y-%m-%d)%2000:00:00&limit=20" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

**Top referrers (last 7 days):**
```bash
curl -s "https://api.usefathom.com/v1/aggregations?entity=pageview&entity_id=SITE_ID&aggregates=pageviews,visits&field_grouping=referrer_hostname&sort_by=pageviews:desc&date_from=$(date -v-7d +%Y-%m-%d)%2000:00:00&limit=20" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

**Daily traffic over time:**
```bash
curl -s "https://api.usefathom.com/v1/aggregations?entity=pageview&entity_id=SITE_ID&aggregates=pageviews,visits,uniques&date_grouping=day&date_from=$(date -v-30d +%Y-%m-%d)%2000:00:00&sort_by=timestamp:asc" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

**Current visitors (real-time):**
```bash
curl -s "https://api.usefathom.com/v1/current_visitors?site_id=SITE_ID&detailed=true" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

**Event conversions:**
```bash
curl -s "https://api.usefathom.com/v1/aggregations?entity=event&site_id=SITE_ID&entity_name=EVENT_NAME&aggregates=conversions,unique_conversions,value&date_from=$(date -v-30d +%Y-%m-%d)%2000:00:00" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

**Traffic by country:**
```bash
curl -s "https://api.usefathom.com/v1/aggregations?entity=pageview&entity_id=SITE_ID&aggregates=visits,pageviews&field_grouping=country_code&sort_by=visits:desc&date_from=$(date -v-30d +%Y-%m-%d)%2000:00:00&limit=20" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

**Traffic by device type:**
```bash
curl -s "https://api.usefathom.com/v1/aggregations?entity=pageview&entity_id=SITE_ID&aggregates=visits,pageviews&field_grouping=device_type&sort_by=visits:desc&date_from=$(date -v-30d +%Y-%m-%d)%2000:00:00" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

**UTM campaign performance:**
```bash
curl -s "https://api.usefathom.com/v1/aggregations?entity=pageview&entity_id=SITE_ID&aggregates=visits,pageviews,uniques&field_grouping=utm_campaign,utm_source&sort_by=visits:desc&date_from=$(date -v-30d +%Y-%m-%d)%2000:00:00&limit=20" \
  -H "Authorization: Bearer $FATHOM_API_KEY" | jq
```

### Presenting Results

Format results as a clean table. Aggregation values come back as strings — parse them as numbers for display. For event `value`, divide by 100 (it's in cents).

When the user asks a vague question like "how's my site doing", default to a summary: total visits/pageviews/uniques for the last 30 days, top 10 pages, and top 5 referrers.

### Constraints

- Daily grouping queries cannot exceed 6 months of data — use monthly grouping for longer ranges
- Aggregations endpoint: 10 requests/minute rate limit — batch wisely
- List endpoints (sites, events): cursor-based pagination, max 100 per page
- `date_from`/`date_to` are interpreted in the specified `timezone` (default UTC)
