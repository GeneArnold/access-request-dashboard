# Multi-Tenant Webhook Support Guide

## Overview

This webhook system supports **multi-tenant architecture** allowing multiple Atlan instances, customers, or webhook sources to send authenticated requests to the same endpoint using different secret keys.

## Authentication Methods Supported

### 1. Atlan's secret-key Header Method (Primary)
**Atlan uses direct secret key comparison** rather than HMAC signatures.

**How it works**:
- Atlan sends webhook secret directly in `secret-key` header
- System performs string comparison against configured secrets
- No cryptographic signature calculation required

**Request format**:
```http
POST /webhook HTTP/1.1
Content-Type: application/json
secret-key: 251dead7-9c7e-4e9a-8ce0-7508330ac926

{"type": "DATA_ACCESS_REQUEST", "payload": {...}}
```

### 2. HMAC Signature Method (Fallback)
**Traditional webhook authentication** used by GitHub, Stripe, etc.

**How it works**:
- Sender calculates HMAC-SHA256 of request body using shared secret
- Sends signature in header (X-Signature-256, X-Hub-Signature-256, etc.)
- Receiver recalculates signature and compares

**Request format**:
```http
POST /webhook HTTP/1.1
Content-Type: application/json
X-Signature-256: sha256=abc123def456...

{"type": "DATA_ACCESS_REQUEST", "payload": {...}}
```

## Multi-Tenant Configuration

### Environment Variable Setup
Configure multiple secrets using comma-separated values:

```bash
# Single tenant (Atlan instance)
WEBHOOK_SECRET=251dead7-9c7e-4e9a-8ce0-7508330ac926

# Multi-tenant (multiple Atlan instances or customers)
WEBHOOK_SECRET=251dead7-9c7e-4e9a-8ce0-7508330ac926,6a04dab1-7d20-4b5a-bfb1-765ad4122b47,10e6e140-1c5f-4c3d-8b3f-9e7c4a5d6e8f

# Production example (use your actual Atlan secrets)
WEBHOOK_SECRET=prod-customer-a-secret,dev-instance-secret,staging-secret
```

### Configuration Examples

#### Development Environment
```bash
# Local development with test secrets
WEBHOOK_SECRET=dev-secret-123,test-secret-456
REQUIRE_SIGNATURE=true
```

#### Production Environment
```bash
# Production with real customer secrets
WEBHOOK_SECRET=customer-1-prod-secret,customer-2-prod-secret,internal-dev-secret
REQUIRE_SIGNATURE=true
```

#### Demo Environment
```bash
# Demo with mixed secrets for demonstrations
WEBHOOK_SECRET=demo-secret-1,demo-secret-2
REQUIRE_SIGNATURE=true
```

## Authentication Flow

### Priority Order
The system tries authentication methods in this order:

1. **secret-key header** (Atlan's method) - **PREFERRED**
2. **HMAC signature headers** (traditional method) - **FALLBACK**

### Validation Bypass
**Validation challenges always bypass authentication** to allow webhook URL verification:
- `{"atlan-webhook": "message"}`
- `{"challenge": "value"}`
- `{"verification_token": "value"}`
- Empty JSON `{}`

### Authentication Logic
```python
# Pseudocode of authentication flow
if is_validation_challenge(request_body):
    return echo_validation_challenge()

if secret_key_header in request:
    if secret_key_header in configured_secrets:
        return process_webhook(verified_with=secret_key_header)
    else:
        return 401_invalid_secret_key()

if signature_header in request:
    for secret in configured_secrets:
        if verify_hmac_signature(body, signature, secret):
            return process_webhook(verified_with=secret)
    return 401_invalid_signature()

return 401_missing_authentication()
```

## Multi-Tenant Features

### Secret Tracking
Each webhook is tracked with which secret validated it:

```json
{
    "status": "success",
    "message": "Webhook received and stored",
    "type": "DATA_ACCESS_REQUEST",
    "asset_name": "Customer_Table",
    "signature_verified": true,
    "verified_with_secret": "251dead7..."
}
```

### Configuration Endpoint
View multi-tenant status via `/config` endpoint:

```bash
curl https://access-request-api.onrender.com/config
```

Response:
```json
{
    "signature_verification_enabled": true,
    "secrets_configured": 3,
    "secret_previews": [
        "251dead7...",
        "6a04dab1...", 
        "10e6e140..."
    ],
    "webhook_file": "./data/webhooks.json",
    "multi_tenant_support": true
}
```

### Audit Trail
Each stored webhook includes audit information:
```json
{
    "type": "DATA_ACCESS_REQUEST",
    "payload": {...},
    "received_at": "2025-06-30T19:42:06Z",
    "signature_verified": true,
    "verified_with_secret": "251dead7...",
    "source_ip": "34.194.9.164"
}
```

## Use Cases

### 1. Multiple Atlan Instances
**Scenario**: Company has dev, staging, and prod Atlan instances

```bash
WEBHOOK_SECRET=dev-atlan-secret,staging-atlan-secret,prod-atlan-secret
```

Each instance sends webhooks with its own secret, all processed by the same dashboard.

### 2. Multiple Customers
**Scenario**: SaaS provider serving multiple customer Atlan instances

```bash
WEBHOOK_SECRET=customer-a-secret,customer-b-secret,customer-c-secret
```

Each customer's webhooks are authenticated separately but displayed in unified dashboard.

### 3. Mixed Webhook Sources
**Scenario**: Supporting both Atlan and other webhook sources

```bash
WEBHOOK_SECRET=atlan-secret,github-secret,custom-app-secret
```

Atlan uses secret-key header, others use HMAC signatures.

### 4. Development and Production
**Scenario**: Same codebase handling both environments

```bash
# Development
WEBHOOK_SECRET=dev-secret-1,test-secret-2

# Production  
WEBHOOK_SECRET=prod-customer-1,prod-customer-2,internal-dev
```

## Security Considerations

### Secret Management
- **Never commit secrets** to version control
- **Use environment variables** for secret storage
- **Rotate secrets periodically** for production use
- **Use different secrets** per tenant/environment

### Access Control
- **Webhook ingestion**: Fully authenticated per secret
- **Data viewing**: Currently open (demo-focused)
- **Data management**: Open DELETE endpoint (demo convenience)

### Audit and Monitoring
- **Track which secret** validated each webhook
- **Monitor for failed authentication** attempts
- **Log source IPs** for security analysis
- **Regular secret rotation** for production deployments

## Testing Multi-Tenant Setup

### Test Secret-Key Authentication
```bash
# Test with first tenant secret
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "secret-key: 251dead7-9c7e-4e9a-8ce0-7508330ac926" \
  -d '{"type": "DATA_ACCESS_REQUEST", "payload": {...}}'

# Test with second tenant secret
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "secret-key: 6a04dab1-7d20-4b5a-bfb1-765ad4122b47" \
  -d '{"type": "DATA_ACCESS_REQUEST", "payload": {...}}'
```

### Test HMAC Signature Authentication
```bash
# Calculate HMAC signature
echo -n '{"test":"payload"}' | openssl dgst -sha256 -hmac "your-secret-key"

# Send with signature
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "X-Signature-256: sha256=calculated-signature" \
  -d '{"test":"payload"}'
```

### Test Invalid Authentication
```bash
# Should return 401 - Invalid secret key
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "secret-key: invalid-secret" \
  -d '{"test":"payload"}'

# Should return 401 - Missing authentication
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test":"payload"}'
```

## Deployment Considerations

### Environment Variable Updates
**Adding new tenant**:
1. Get new webhook secret from tenant's Atlan instance
2. Update `WEBHOOK_SECRET` in Render dashboard
3. Add new secret to comma-separated list
4. No code deployment required (environment variables persist)

**Removing tenant**:
1. Remove secret from `WEBHOOK_SECRET` environment variable
2. Old webhooks from that tenant will be rejected
3. Existing stored data remains until next service restart

### Service Restart Behavior
- **Environment variables**: Persist across restarts
- **Webhook data**: Cleared on restart (ephemeral filesystem)
- **Configuration**: Automatically reloaded from environment variables

## Troubleshooting Multi-Tenant Issues

### Common Problems

#### 1. New Tenant Webhook Rejected
**Symptoms**: 401 Unauthorized for new tenant
**Solution**: 
1. Verify new secret added to `WEBHOOK_SECRET`
2. Check for typos in environment variable
3. Confirm tenant is using correct secret
4. Test with curl using exact secret

#### 2. Tenant Using Wrong Authentication Method
**Symptoms**: 401 errors despite correct secret
**Solution**:
1. Verify tenant sends `secret-key` header (Atlan method)
2. If using HMAC, ensure proper signature calculation
3. Use webhook.site to capture exact request format
4. Compare against working examples

#### 3. Secret Conflicts
**Symptoms**: Wrong tenant attribution in audit logs
**Solution**:
1. Ensure all secrets are unique
2. Check for duplicate secrets in configuration
3. Review audit logs for verification patterns

### Debugging Tools

#### Configuration Check
```bash
# View current multi-tenant configuration
curl https://access-request-api.onrender.com/config

# Expected response shows all configured secrets
{
    "secrets_configured": 3,
    "secret_previews": ["251dead7...", "6a04dab1...", "10e6e140..."],
    "multi_tenant_support": true
}
```

#### Authentication Testing
```bash
# Test each tenant secret individually
for secret in secret1 secret2 secret3; do
    echo "Testing secret: ${secret:0:8}..."
    curl -X POST localhost:8080/webhook \
        -H "Content-Type: application/json" \
        -H "secret-key: $secret" \
        -d '{"test": "multi-tenant"}' \
        -w "Status: %{http_code}\n"
done
```

## Best Practices

### Secret Management
1. **Use descriptive naming** in environment variables when possible
2. **Document which secret belongs to which tenant**
3. **Regular rotation** for production environments
4. **Separate secrets** for dev/staging/prod

### Monitoring
1. **Track secret usage** via audit logs
2. **Monitor for authentication failures** by tenant
3. **Alert on unusual patterns** (new secrets, high failure rates)
4. **Regular configuration reviews**

### Scaling
1. **Consider database storage** for high-volume multi-tenant setups
2. **Implement rate limiting** per tenant if needed
3. **Add tenant-specific dashboards** for enterprise customers
4. **Consider secret encryption** for very sensitive environments

This multi-tenant architecture provides flexibility for various deployment scenarios while maintaining security and auditability for each tenant's webhook integration. 