# Commands

Run from the `project-hub` repo root unless noted.

## Tokens

Read-only Security Center audit:

```sh
export CLOUDFLARE_API_TOKEN="$(LC_ALL=C tr -d '[:space:]' < /tmp/cloudflare-audit-token)"
```

Write/OpenTofu token:

```sh
export CLOUDFLARE_API_TOKEN="$(LC_ALL=C tr -d '[:space:]' < /tmp/cloudflare-write-token)"
export AWS_ACCESS_KEY_ID="$(curl -sS -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  https://api.cloudflare.com/client/v4/accounts/a3d6402fb66f7b9e9d1b8554b951d981/tokens/verify | jq -r '.result.id')"
export AWS_SECRET_ACCESS_KEY="$(printf '%s' "$CLOUDFLARE_API_TOKEN" | shasum -a 256 | awk '{print $1}')"
```

## Audit

```sh
./infra/cloudflare/scripts/audit-security-insights.sh > /tmp/cloudflare-security-audit.json
jq '{generated_at, active_insight_count, by_severity, by_type, by_class}' /tmp/cloudflare-security-audit.json
```

## OpenTofu

```sh
cd infra/cloudflare
tofu fmt -recursive
tofu validate
tofu plan
```

Apply only after reviewing plan output:

```sh
tofu apply
```

## Smoke

```sh
./infra/cloudflare/scripts/smoke-www-redirects.sh
./infra/cloudflare/scripts/smoke-apex-https.sh
```
