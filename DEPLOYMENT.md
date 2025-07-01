# Deployment Guide - Access Request Webhook Dashboard

## Overview

This guide covers the complete deployment process for the dual-service webhook dashboard on Render.com, including all lessons learned and troubleshooting steps.

## Architecture

### Services Structure
- **API Service**: `access-request-api` (FastAPI webhook receiver)
- **Dashboard Service**: `access-request-dashboard` (Streamlit frontend)
- **Storage**: Ephemeral JSON files (demo-friendly)

### URLs
- **Production API**: https://access-request-api.onrender.com
- **Production Dashboard**: https://access-request-dashboard.onrender.com
- **GitHub Repository**: https://github.com/GeneArnold/access-request-dashboard

## Prerequisites

### Required Accounts
1. **GitHub Account** - For code repository
2. **Render Account** - For hosting (free tier sufficient)
3. **Atlan Instance** - For webhook integration

### Repository Setup
```bash
# Clone the repository
git clone https://github.com/GeneArnold/access-request-dashboard.git
cd access-request-dashboard

# Verify structure
ls -la
# Should show: api/, ui/, README.md, DEPLOYMENT.md, etc.
```

## API Service Deployment

### 1. Create Render Service
1. Log into **Render Dashboard**: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your **GitHub repository**
4. Configure service:
   - **Name**: `access-request-api`
   - **Environment**: `Python 3`
   - **Region**: `Ohio (US East)` (or closest to users)
   - **Branch**: `main`
   - **Root Directory**: `api`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`

### 2. Environment Variables
Set these in **Render Dashboard** → **Service** → **Environment**:

```bash
# Required - Webhook secrets (comma-separated for multi-tenant)
WEBHOOK_SECRET=251dead7-9c7e-4e9a-8ce0-7508330ac926,6a04dab1-7d20-4b5a-bfb1-765ad4122b47

# Optional - Signature verification control
REQUIRE_SIGNATURE=true

# Auto-set by Render (don't set manually)
PORT=<auto-assigned>
```

### 3. Deployment Configuration
The API service uses `api/render.yaml`:
```yaml
services:
  - type: web
    name: access-request-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python main.py"
    envVars:
      - key: PORT
        generateValue: true
      - key: WEBHOOK_SECRET
        sync: false
```

### 4. Common Deployment Issues

#### Build Failures
**Problem**: Rust compilation errors with pydantic-core
```
error: Microsoft Visual Studio C++ 14.0 is required
```

**Solution**: Update `requirements.txt` to use newer versions with pre-compiled wheels:
```txt
fastapi==0.115.6
uvicorn==0.32.1
pydantic==2.10.4
python-multipart==0.0.12
python-dotenv==1.0.1
```

#### Port Configuration
**Problem**: Service not responding
**Solution**: Ensure `main.py` uses Render's PORT environment variable:
```python
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
```

#### Environment Variable Issues
**Problem**: 500 errors on webhook requests
**Solution**: Verify `WEBHOOK_SECRET` is set in Render dashboard, not just locally

## Dashboard Service Deployment

### 1. Create Dashboard Service
1. **Render Dashboard** → **"New +"** → **"Web Service"**
2. **Same GitHub repository**
3. Configure service:
   - **Name**: `access-request-dashboard`
   - **Environment**: `Python 3`
   - **Region**: `Ohio (US East)` (same as API)
   - **Branch**: `main`
   - **Root Directory**: `ui`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`

### 2. Dashboard Configuration
The dashboard uses `ui/render.yaml`:
```yaml
services:
  - type: web
    name: access-request-dashboard
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0"
```

### 3. API Connection
Ensure dashboard connects to production API:
```python
# In streamlit_app.py
API_BASE_URL = "https://access-request-api.onrender.com"
```

## Environment Variables Management

### Production Secrets
**Critical**: Only set production webhook secrets that Atlan generates. Do NOT add test keys from webhook.site.

```bash
# Example configuration (use your actual Atlan secrets)
WEBHOOK_SECRET=your-atlan-secret-1,your-atlan-secret-2
```

### Environment Variable Persistence
- ✅ **Environment variables persist** across deployments
- ❌ **File storage does NOT persist** (ephemeral filesystem)

## Deployment Process

### Automatic Deployment
1. **Push to GitHub main branch**
2. **Render automatically detects changes**
3. **Both services rebuild and deploy** (~3-5 minutes)
4. **Webhook data is wiped** (fresh start for demos)

### Manual Deployment
1. **Render Dashboard** → **Service** → **Manual Deploy**
2. Select **latest commit** or specific commit
3. **Deploy** button

### Deployment Verification
```bash
# Test API health
curl https://access-request-api.onrender.com/
# Expected: {"message": "Webhook Receiver API is running!", "endpoints": [...]}

# Test configuration
curl https://access-request-api.onrender.com/config
# Expected: {"signature_verification_enabled": true, "secrets_configured": N, ...}

# Test dashboard
# Visit: https://access-request-dashboard.onrender.com
# Expected: "No webhook data found" message
```

## Free Tier Behavior

### Service Spin-Down
**Render free tier services spin down after ~15 minutes of inactivity**

**Symptoms**:
- First request after inactivity takes 30+ seconds
- 502 Bad Gateway during spin-up
- Dashboard shows "spinning" or loading indefinitely

**Solutions**:
1. **Wait it out** - First request will be slow, subsequent requests fast
2. **Keep-alive service** - Use cron-job.org to ping API every 14 minutes
3. **Upgrade to paid** - Paid instances don't sleep

### Data Persistence
**File storage is ephemeral on free tier**:
- ✅ **Environment variables persist** across restarts
- ❌ **JSON files are wiped** on each spin-up/deployment
- ✅ **This is perfect for demos** (fresh data each time)

## Troubleshooting

### Common Issues

#### 1. Webhook 401 Unauthorized
**Symptoms**: Atlan webhook fails with 401 error in Render logs
```
INFO: 34.194.9.164:0 - "POST /webhook HTTP/1.1" 401 Unauthorized
```

**Debug Steps**:
1. **Use webhook.site** to capture exact Atlan request format
2. **Check headers** - Verify `secret-key` header is present
3. **Verify secrets** - Ensure Atlan secret matches `WEBHOOK_SECRET` config
4. **Check logs** - Render Dashboard → Service → Logs → Live tail

**Common Causes**:
- Atlan generated new secret after URL change
- Missing `secret-key` header (check Atlan configuration)
- Typo in environment variable configuration

#### 2. Dashboard Shows No Data
**Symptoms**: Dashboard loads but shows "No webhook data found"

**Possible Causes**:
1. **Service spin-down** - Data wiped when API restarted
2. **No webhooks received** - API hasn't received any valid webhooks
3. **API connection failure** - Dashboard can't reach API service

**Debug Steps**:
```bash
# Check if API has data
curl https://access-request-api.onrender.com/webhooks

# Test webhook manually
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "secret-key: your-webhook-secret" \
  -d '{"type": "DATA_ACCESS_REQUEST", "payload": {...}}'
```

#### 3. Build Failures
**Symptoms**: Deployment fails during build phase

**Common Issues**:
- **Rust compilation errors**: Update to newer package versions
- **Missing dependencies**: Check `requirements.txt` for all needed packages
- **Python version**: Ensure compatibility with Render's Python 3.x

#### 4. Cross-Service Communication
**Symptoms**: Dashboard can't fetch data from API

**Check**:
1. API service is running and responding
2. Dashboard uses correct production API URL
3. No CORS issues (FastAPI configured for cross-origin requests)

### Debugging Tools

#### Render Logs
1. **Render Dashboard** → **Service** → **Logs**
2. **Set to "Live tail"** for real-time monitoring
3. **Filter by log level** if needed

#### Webhook Testing
```bash
# Test Atlan validation
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"atlan-webhook": "Hello, humans of data! It worked. Excited to see what you build!"}'

# Test with secret-key header
curl -X POST https://access-request-api.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "secret-key: your-webhook-secret" \
  -d '{"test": "data"}'
```

#### webhook.site Integration
1. **Go to webhook.site** and get temporary URL
2. **Configure Atlan** to use webhook.site URL
3. **Capture request format** (headers, body, method)
4. **Test our endpoint** with exact same format

## Production Checklist

### Pre-Deployment
- [ ] GitHub repository is up to date
- [ ] Both services configured in Render
- [ ] Environment variables set correctly
- [ ] Latest package versions in requirements.txt

### Post-Deployment
- [ ] API service responds to health check
- [ ] Dashboard loads and shows correct UI
- [ ] Webhook validation works (test with curl)
- [ ] Multi-tenant configuration visible in /config
- [ ] Atlan webhook integration successful

### Demo Preparation
- [ ] Clear any existing webhook data
- [ ] Test complete webhook flow
- [ ] Verify dashboard analytics display correctly
- [ ] Prepare sample data access request in Atlan

## Monitoring and Maintenance

### Regular Checks
- **Weekly**: Verify both services are running
- **Before demos**: Clear webhook data and test flow
- **After Atlan updates**: Re-test webhook integration

### Performance Monitoring
- **Render Dashboard**: Service metrics and uptime
- **API Response Times**: Use curl or monitoring tools
- **Error Rates**: Check logs for 4xx/5xx errors

### Updates and Maintenance
1. **Code updates**: Push to main branch for auto-deployment
2. **Dependency updates**: Update requirements.txt as needed
3. **Environment variables**: Update in Render dashboard only

This deployment guide captures all lessons learned and should prevent common pitfalls encountered during initial deployment and ongoing maintenance. 