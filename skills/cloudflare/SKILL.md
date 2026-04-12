---
name: cloudflare
description: Manage Cloudflare zones, DNS records, cache, and analytics via the Cloudflare API. Use this skill whenever the user asks about DNS records, Cloudflare zones, cache purging, zone analytics, traffic stats from Cloudflare, managing DNS, adding/removing DNS records, checking zone status, or anything related to Cloudflare infrastructure management. Also trigger when the user mentions "CF", "Cloudflare", domain DNS, CDN configuration, or wants to purge cache, even if they don't explicitly say "Cloudflare".
---

# Cloudflare

Manage zones, DNS, cache, and analytics via the Cloudflare API.

## Credential Setup

Retrieve the API token in this order:

1. Environment variable: `$CLOUDFLARE_API_TOKEN` (or `$CF_API_TOKEN`)
2. macOS Keychain: `security find-generic-password -s "cloudflare-api-token" -w 2>/dev/null`

If not found:

> No Cloudflare API token found. Set one up:
> 1. Go to https://dash.cloudflare.com/profile/api-tokens
> 2. Create a token with the permissions you need (Zone:Read, DNS:Edit, Cache Purge, Analytics:Read)
> 3. Either `export CLOUDFLARE_API_TOKEN=your_token` or store in Keychain:
>    `security add-generic-password -s "cloudflare-api-token" -a "cloudflare" -w "your_token"`

```bash
CF_TOKEN="${CLOUDFLARE_API_TOKEN:-${CF_API_TOKEN:-$(security find-generic-password -s "cloudflare-api-token" -w 2>/dev/null)}}"
```

Verify token works:

```bash
curl -s "https://api.cloudflare.com/client/v4/user/tokens/verify" \
  -H "Authorization: Bearer $CF_TOKEN" | jq '.success'
```

## API Reference

**Base URL:** `https://api.cloudflare.com/client/v4`
**Auth header:** `Authorization: Bearer $CF_TOKEN`
**Rate limit:** 1,200 requests per 5 minutes

All REST responses follow the envelope: `{"success": bool, "errors": [], "result": ..., "result_info": {page, per_page, count, total_count}}`

### Zone Management

**List zones:**
```bash
curl -s "https://api.cloudflare.com/client/v4/zones?per_page=50" \
  -H "Authorization: Bearer $CF_TOKEN" | jq '.result[] | {id, name, status, plan: .plan.name}'
```

Filter with `?name=example.com` to find a specific zone.

**Get zone details:**
```bash
curl -s "https://api.cloudflare.com/client/v4/zones/ZONE_ID" \
  -H "Authorization: Bearer $CF_TOKEN" | jq '.result | {id, name, status, name_servers, plan: .plan.name, paused}'
```

### DNS Records

**List records:**
```bash
curl -s "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records?per_page=100" \
  -H "Authorization: Bearer $CF_TOKEN" | jq '.result[] | {id, type, name, content, proxied, ttl}'
```

Filter: `?type=A`, `?name=sub.example.com`, `?content=1.2.3.4`

**Create record:**
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "A",
    "name": "sub.example.com",
    "content": "198.51.100.4",
    "ttl": 1,
    "proxied": true
  }' | jq '.result | {id, type, name, content}'
```

TTL: `1` = auto (recommended when proxied), or 60–86400 seconds.

**Update record (full replacement):**
```bash
curl -s -X PUT "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records/RECORD_ID" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "A",
    "name": "sub.example.com",
    "content": "198.51.100.5",
    "ttl": 1,
    "proxied": true
  }' | jq '.result | {id, type, name, content}'
```

**Delete record:**
```bash
curl -s -X DELETE "https://api.cloudflare.com/client/v4/zones/ZONE_ID/dns_records/RECORD_ID" \
  -H "Authorization: Bearer $CF_TOKEN" | jq '.result.id'
```

### Cache Purge

```bash
# Purge everything
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"purge_everything": true}' | jq '.success'

# Purge specific URLs
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"files": ["https://example.com/style.css", "https://example.com/script.js"]}' | jq '.success'

# Purge by prefix
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"prefixes": ["/api/", "/static/"]}' | jq '.success'

# Purge by hostname
curl -s -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/purge_cache" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hosts": ["blog.example.com"]}' | jq '.success'
```

Options are mutually exclusive. Only one of `purge_everything`, `files`, `tags`, `hosts`, or `prefixes` per request.

### Analytics (GraphQL)

Cloudflare analytics uses GraphQL at a separate endpoint:

```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "QUERY", "variables": {}}'
```

**Daily traffic summary (last 7 days):**
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ viewer { zones(filter: { zoneTag: \"ZONE_ID\" }) { httpRequests1dGroups(filter: { date_geq: \"'$(date -v-7d +%Y-%m-%d)'\", date_leq: \"'$(date +%Y-%m-%d)'\" }, limit: 7, orderBy: [date_ASC]) { dimensions { date } sum { requests bytes cachedBytes threats pageViews } uniq { uniques } } } } }"
  }' | jq '.data.viewer.zones[0].httpRequests1dGroups'
```

**Hourly traffic (last 24h):**
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ viewer { zones(filter: { zoneTag: \"ZONE_ID\" }) { httpRequests1hGroups(filter: { datetime_geq: \"'$(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)'\", datetime_leq: \"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\" }, limit: 24, orderBy: [datetime_ASC]) { dimensions { datetime } sum { requests cachedBytes bytes } } } } }"
  }' | jq '.data.viewer.zones[0].httpRequests1hGroups'
```

**Top request paths:**
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ viewer { zones(filter: { zoneTag: \"ZONE_ID\" }) { httpRequestsAdaptiveGroups(filter: { datetime_geq: \"'$(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)'\", datetime_leq: \"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\" }, limit: 20, orderBy: [count_DESC]) { dimensions { clientRequestPath } count } } } }"
  }' | jq '.data.viewer.zones[0].httpRequestsAdaptiveGroups'
```

**Firewall events:**
```bash
curl -s -X POST "https://api.cloudflare.com/client/v4/graphql" \
  -H "Authorization: Bearer $CF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ viewer { zones(filter: { zoneTag: \"ZONE_ID\" }) { firewallEventsAdaptiveGroups(filter: { datetime_geq: \"'$(date -u -v-24H +%Y-%m-%dT%H:%M:%SZ)'\", datetime_leq: \"'$(date -u +%Y-%m-%dT%H:%M:%SZ)'\" }, limit: 20, orderBy: [count_DESC]) { dimensions { action clientCountryName } count } } } }"
  }' | jq '.data.viewer.zones[0].firewallEventsAdaptiveGroups'
```

**Key GraphQL datasets:**
- `httpRequests1dGroups` — daily aggregates
- `httpRequests1hGroups` — hourly aggregates  
- `httpRequestsAdaptiveGroups` — flexible aggregations with dimensions
- `firewallEventsAdaptiveGroups` — WAF/firewall events

GraphQL filter operators: `gt`, `lt`, `geq`, `leq`, `neq`, `in`, `like` (with `%`). Date format: ISO 8601.

GraphQL rate limit: 320 queries per 5 minutes.

### Workers

```bash
# List workers
curl -s "https://api.cloudflare.com/client/v4/accounts/ACCOUNT_ID/workers/scripts" \
  -H "Authorization: Bearer $CF_TOKEN" | jq '.result[] | {id, etag, created_on, modified_on}'
```

### Presenting Results

When listing DNS records, format as a table with type, name, content, proxied status, and TTL. For analytics, summarize requests, bandwidth (format bytes as KB/MB/GB), cache hit ratio (cachedBytes/bytes), and unique visitors. When the user asks about their "site" or "domain", start by resolving the zone ID from the domain name.

### Safety

DNS and cache operations modify live infrastructure. Before creating, updating, or deleting DNS records, confirm the specific change with the user. Cache purges are safe to execute without confirmation (they're non-destructive and self-healing).
