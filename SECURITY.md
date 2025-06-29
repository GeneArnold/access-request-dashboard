# 🔐 Webhook Security Guide

## Overview

Your FastAPI app now includes robust webhook security to ensure that only legitimate webhooks from Atlan can trigger your application. This prevents malicious actors from sending fake webhook data.

## 🔑 How Webhook Security Works

### 1. Secret Key
- Atlan generates a unique secret key for your webhook
- This key is shared between Atlan and your application
- **Your key**: `f3a225c-f1db-430d-8a73-818a9133df92`

### 2. Signature Generation
When Atlan sends a webhook, it:
1. Takes your webhook payload (JSON data)
2. Creates a signature using HMAC-SHA256 with your secret key
3. Sends the signature in a header (usually `X-Signature-256`)

### 3. Signature Verification
Your app:
1. Receives the webhook payload and signature
2. Generates its own signature using the same method
3. Compares the signatures - if they match, the webhook is legitimate

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in your `api/` directory:

```bash
# Copy from config.env.example
cp api/config.env.example api/.env
```

Edit `api/.env`:
```env
# Your actual Atlan webhook secret key
WEBHOOK_SECRET=f3a225c-f1db-430d-8a73-818a9133df92

# Enable signature verification in production
REQUIRE_SIGNATURE=True
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `WEBHOOK_SECRET` | Your Atlan key | Secret key from Atlan webhook config |
| `REQUIRE_SIGNATURE` | `True` | Enable/disable signature verification |

## 🛡️ Security Levels

### Production Mode (Recommended)
```env
REQUIRE_SIGNATURE=True
WEBHOOK_SECRET=your-actual-atlan-secret-key
```
- ✅ Full signature verification
- ✅ Rejects unsigned webhooks
- ✅ Maximum security

### Development/Testing Mode
```env
REQUIRE_SIGNATURE=False
```
- ⚠️ No signature verification
- ⚠️ Accepts any webhook data
- ⚠️ Use only for testing

## 📡 API Endpoints

### Secure Webhook (Production)
- **URL**: `POST /webhook`
- **Security**: Requires valid signature
- **Use**: Production Atlan webhooks

### Test Webhook (Development)
- **URL**: `POST /webhook/test`
- **Security**: No signature required
- **Use**: Manual testing and development

### Configuration Check
- **URL**: `GET /config`
- **Returns**: Current security settings
- **Use**: Verify your configuration

## 🧪 Testing Your Security

### 1. Check Configuration
```bash
curl http://localhost:8080/config
```

### 2. Test Without Signature (Should Fail in Production)
```bash
curl -X POST "http://localhost:8080/webhook" \
     -H "Content-Type: application/json" \
     -d '{"type":"DATA_ACCESS_REQUEST", "payload": {...}}'
```

### 3. Test With Valid Signature
Use Atlan's webhook test feature or the `/webhook/test` endpoint.

## 🔧 Atlan Configuration

### In Atlan's Webhook Settings:

1. **URL**: Set to your deployed API endpoint
   - Local: `http://localhost:8080/webhook`
   - Production: `https://your-app.onrender.com/webhook`

2. **Secret**: Use the key shown in your Atlan interface
   - Copy the key exactly as shown
   - Update your `.env` file with this key

3. **Headers**: Atlan automatically adds signature headers
   - `X-Signature-256` (preferred)
   - `X-Hub-Signature-256` (GitHub style)
   - `X-Signature` (fallback)

## 🚨 Security Best Practices

### ✅ DO
- **Always use HTTPS in production**
- **Keep your secret key private**
- **Enable signature verification (`REQUIRE_SIGNATURE=True`)**
- **Use environment variables for secrets**
- **Regularly rotate your secret keys**
- **Monitor failed webhook attempts**

### ❌ DON'T
- **Never commit secret keys to git**
- **Don't disable signature verification in production**
- **Don't use HTTP in production**
- **Don't share your secret key**
- **Don't hardcode secrets in source code**

## 🔄 Key Rotation

To rotate your webhook secret:

1. **Generate new key in Atlan**
2. **Update your `.env` file**
3. **Restart your application**
4. **Test with a sample webhook**

## 🐛 Troubleshooting

### Common Issues

**"Invalid webhook signature"**
- Check that your secret key matches Atlan exactly
- Ensure the key has no extra spaces or characters
- Verify Atlan is sending the signature header

**"Missing signature header"**
- Atlan might not be configured to send signatures
- Check Atlan's webhook configuration
- Try using the test endpoint first

**"Webhook verification error"**
- Check server logs for detailed error messages
- Verify your secret key is correct
- Ensure HTTPS is working properly

## 📝 Example .env File

```env
# Production Configuration
WEBHOOK_SECRET=f3a225c-f1db-430d-8a73-818a9133df92
REQUIRE_SIGNATURE=True

# Optional: Custom settings
# WEBHOOK_FILE=../data/webhooks.json
```

## 🔍 Monitoring

Your app logs will show:
- ✅ Successful webhook verifications
- ❌ Failed signature verifications
- 📝 Configuration status on startup

Monitor these logs to ensure your webhook security is working correctly.

---

**Remember**: This security setup ensures that only Atlan can send webhooks to your application, protecting against malicious requests and ensuring data integrity. 