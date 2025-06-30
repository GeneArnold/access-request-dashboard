# Multi-Tenant Webhook Support

## Overview

Your webhook receiver now supports **multiple secret keys** for multi-tenant deployments! This enables you to:

- **Support multiple Atlan instances** (dev, staging, production)
- **Handle different customers** with their own webhook secrets  
- **Integrate multiple webhook sources** beyond just Atlan
- **Scale to enterprise deployments** with separate secret keys per environment

## Configuration

### Environment Variable Format

Set multiple secrets using comma-separated values:

```bash
# Single secret (existing behavior)
WEBHOOK_SECRET="16c71bb3-ab9d-48bb-ad73-51f8eaa7e989"

# Multiple secrets (new feature)
WEBHOOK_SECRET="secret1,secret2,secret3"

# Real example with multiple Atlan environments
WEBHOOK_SECRET="16c71bb3-ab9d-48bb-ad73-51f8eaa7e989,f3a225c-f1db-430d-8a73-818a9133df92,a1b2c3d4-e5f6-789a-bcde-f0123456789a"
```

### Render Configuration

In your Render dashboard:
1. Go to **Environment Variables**  
2. Update `WEBHOOK_SECRET` with comma-separated values
3. **Save** (triggers automatic redeploy)

## How It Works

### Signature Verification Process

1. **Webhook received** with signature header
2. **Try each secret** in the configured list
3. **First matching secret** validates the webhook
4. **Track which secret** was used (for logging/analytics)

### Security Benefits

- **No shared secrets** between different environments
- **Individual secret rotation** without affecting other clients
- **Source identification** - know which environment/client sent each webhook
- **Audit trail** - track which secrets are being used

## API Endpoints

### Configuration Endpoint

Check your current setup:

```bash
GET /config
```

Response shows multi-tenant status:

```json
{
  "signature_verification_enabled": true,
  "secrets_configured": 3,
  "secret_previews": ["16c71bb3...", "f3a225c-...", "a1b2c3d4..."],
  "webhook_file": "./data/webhooks.json",
  "multi_tenant_support": true
}
```

### Webhook Response

Successful webhooks now include which secret was used:

```json
{
  "status": "success",
  "message": "Webhook received and stored", 
  "type": "DATA_ACCESS_REQUEST",
  "asset_name": "customer_table",
  "signature_verified": true,
  "verified_with_secret": "16c71bb3..."
}
```

## Use Cases

### 1. Multiple Atlan Environments

```bash
# Development, Staging, Production
WEBHOOK_SECRET="dev-secret-123,staging-secret-456,prod-secret-789"
```

### 2. Multiple Customers

```bash
# Different webhook secrets per customer  
WEBHOOK_SECRET="customer-a-secret,customer-b-secret,customer-c-secret"
```

### 3. Multiple Webhook Sources

```bash
# Atlan + other data governance tools
WEBHOOK_SECRET="atlan-secret,collibra-secret,apache-atlas-secret"
```

## Stored Data

Each webhook now includes tracking information:

```json
{
  "type": "DATA_ACCESS_REQUEST",
  "payload": { ... },
  "signature_verified": true,
  "verified_with_secret": "16c71bb3...",
  "received_at": "2024-12-30T12:00:00"
}
```

## Migration

### From Single Secret

**Before:**
```bash
WEBHOOK_SECRET="16c71bb3-ab9d-48bb-ad73-51f8eaa7e989"
```

**After (backward compatible):**
```bash  
WEBHOOK_SECRET="16c71bb3-ab9d-48bb-ad73-51f8eaa7e989"
# OR add more secrets:
WEBHOOK_SECRET="16c71bb3-ab9d-48bb-ad73-51f8eaa7e989,new-secret-2,new-secret-3"
```

### Zero Downtime

- **Existing webhooks continue working** during migration
- **Add new secrets** without breaking existing integrations
- **Remove old secrets** after confirming all sources use new ones

## Dashboard Integration

Your Streamlit dashboard automatically shows:
- **Which secret verified** each webhook request
- **Source identification** based on secret used
- **Multi-tenant filtering** capabilities

## Security Best Practices

1. **Unique secrets per environment/client**
2. **Regular secret rotation** (rotate individually)
3. **Monitor secret usage** via dashboard analytics
4. **Remove unused secrets** to reduce attack surface
5. **Log verification failures** for security monitoring

## Troubleshooting

### Common Issues

**New webhook failing validation:**
- Check if new secret is added to `WEBHOOK_SECRET`  
- Verify webhook source is using correct secret
- Check `/config` endpoint to confirm secrets loaded

**Multiple environments interfering:**
- Ensure each environment uses unique secret
- Check dashboard to see which secret validated each request
- Verify no duplicate secrets across environments

### Debug Information

Check configuration:
```bash
curl https://access-request-api.onrender.com/config
```

This shows:
- How many secrets are configured
- Preview of each secret (first 8 characters)
- Whether multi-tenant support is active 