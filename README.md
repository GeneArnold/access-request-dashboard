# 🚀 Data Access Request Webhook Dashboard

A **production-ready webhook demonstration platform** for showcasing Atlan data governance integrations. Receive, authenticate, and visualize data access requests in real-time with beautiful analytics.

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 🎯 Overview

This system demonstrates how to integrate with Atlan's webhook system to receive data access requests and display them in a gorgeous, real-time analytics dashboard. Perfect for customer demonstrations, proof-of-concepts, and showcasing webhook integration capabilities.

### ✨ Key Features

- 🔐 **Secure webhook authentication** with multiple methods (Atlan secret-key + HMAC signatures)
- 🏢 **Multi-tenant support** for multiple Atlan instances or customers
- 📊 **Real-time analytics dashboard** with interactive charts and filtering
- 🚀 **Zero-config deployment** on Render.com (free tier)
- 🎪 **Demo-friendly** with ephemeral storage and easy data reset
- 📱 **Responsive design** for presentations on any device
- 🔍 **Detailed request inspection** with raw JSON viewer

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│    Atlan    │───▶│ FastAPI Webhook │───▶│ JSON Storage │◀───│ Streamlit       │
│  Instance   │    │   Receiver      │    │  (Ephemeral) │    │   Dashboard     │
└─────────────┘    └─────────────────┘    └──────────────┘    └─────────────────┘
                         Port 8080                                   Port 8502
```

### 🌐 Live Demo

- **🎯 Dashboard**: https://access-request-dashboard.onrender.com
- **🔌 API**: https://access-request-api.onrender.com
- **📚 API Docs**: https://access-request-api.onrender.com/docs

## 🚀 Quick Start

### 1. Deploy to Render (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

**Or manually:**

1. **Fork this repository**
2. **Connect to Render**: Create account at [render.com](https://render.com)
3. **Deploy API service**:
   - New Web Service → Connect GitHub
   - Root Directory: `api`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
4. **Deploy Dashboard**:
   - New Web Service → Same repository
   - Root Directory: `ui`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run streamlit_app.py --server.port $PORT --server.address 0.0.0.0`
5. **Set environment variables** (see Configuration section)

### 2. Local Development

```bash
# Clone the repository
git clone https://github.com/GeneArnold/access-request-dashboard.git
cd access-request-dashboard

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install dependencies
pip install -r api/requirements.txt
pip install -r ui/requirements.txt

# Start API service (Terminal 1)
cd api
python main.py
# API available at: http://localhost:8080

# Start Dashboard (Terminal 2)
cd ui
streamlit run streamlit_app.py
# Dashboard available at: http://localhost:8502
```

## ⚙️ Configuration

### Environment Variables

Set these in your deployment platform (Render, Heroku, etc.):

```bash
# Required: Webhook authentication secrets (comma-separated for multi-tenant)
WEBHOOK_SECRET=your-atlan-webhook-secret-here

# Optional: Enable/disable signature verification (default: true)
REQUIRE_SIGNATURE=true

# Auto-set by platform (don't set manually)
PORT=auto-assigned-by-platform
```

#### Multi-Tenant Example
```bash
# Support multiple Atlan instances or customers
WEBHOOK_SECRET=prod-customer-a-secret,dev-instance-secret,staging-customer-b-secret
```

### Atlan Integration

1. **Get webhook secret** from your Atlan instance
2. **Configure webhook URL** in Atlan: `https://your-api-url.onrender.com/webhook`
3. **Test integration** by creating a data access request in Atlan
4. **View results** in your dashboard

## 🔐 Security & Authentication

### Atlan's Authentication Method

**Important**: Atlan uses `secret-key` header authentication, not HMAC signatures:

```http
POST /webhook HTTP/1.1
Content-Type: application/json
secret-key: your-atlan-webhook-secret

{"type": "DATA_ACCESS_REQUEST", "payload": {...}}
```

### Fallback Authentication

Also supports traditional HMAC signature authentication for other webhook sources:

```http
POST /webhook HTTP/1.1
Content-Type: application/json
X-Signature-256: sha256=hmac-signature-here

{"type": "DATA_ACCESS_REQUEST", "payload": {...}}
```

### Multi-Tenant Security

- ✅ **Individual secret validation** per tenant/customer
- ✅ **Audit trail** tracking which secret validated each webhook
- ✅ **Source identification** for security monitoring
- ✅ **Flexible secret rotation** without affecting other tenants

## 📊 Dashboard Features

### Real-Time Analytics
- **📈 Key Metrics**: Total requests, approval rates, unique requestors
- **🥧 Asset Type Distribution**: Interactive pie charts
- **📊 Connector Analysis**: Bar charts showing data source usage
- **🔍 Advanced Filtering**: By requestor, asset type, connector

### Request Management
- **📋 Recent Requests Table**: Color-coded status indicators
- **🔍 Detailed Inspector**: Full request details with JSON viewer
- **⏱️ Timestamp Tracking**: Request and approval timing
- **👥 Approval Workflow**: Approver information and comments

### Demo-Friendly Features
- **🧹 Easy Reset**: One-click data clearing for fresh demos
- **📱 Responsive Design**: Works perfectly on presentation screens
- **🎨 Beautiful UI**: Professional appearance for customer demos
- **⚡ Real-Time Updates**: Auto-refresh for live demonstrations

## 🛠️ API Endpoints

### Production Endpoints

| Method | Endpoint | Description | Authentication |
|--------|----------|-------------|----------------|
| `POST` | `/webhook` | **Main webhook receiver** | ✅ Required |
| `GET` | `/webhooks` | List all webhooks | ❌ Open |
| `GET` | `/webhooks/latest` | Get most recent webhook | ❌ Open |
| `GET` | `/config` | View configuration | ❌ Open |
| `DELETE` | `/webhooks` | Clear all data | ❌ Open (demo-friendly) |
| `GET` | `/docs` | Interactive API documentation | ❌ Open |

### Testing Endpoints

```bash
# Test webhook authentication
curl -X POST https://your-api-url.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -H "secret-key: your-webhook-secret" \
  -d '{"type": "DATA_ACCESS_REQUEST", "payload": {...}}'

# Test validation challenge (Atlan setup)
curl -X POST https://your-api-url.onrender.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"atlan-webhook": "Hello, humans of data! It worked. Excited to see what you build!"}'

# Check configuration
curl https://your-api-url.onrender.com/config

# Clear demo data
curl -X DELETE https://your-api-url.onrender.com/webhooks
```

## 💾 Data Storage

### Ephemeral Storage (Perfect for Demos!)

- **📁 Storage Method**: JSON files on local filesystem
- **♻️ Auto-Reset**: Data clears when services restart (every ~15 minutes on free tier)
- **🎪 Demo Benefits**: Fresh start for each demonstration, no customer data mixing
- **🔄 Manual Reset**: Use `DELETE /webhooks` endpoint anytime

### Persistence Options (When Needed)

For production use with persistent storage:

1. **🗄️ Database Integration**: PostgreSQL, MySQL (Render offers free tiers)
2. **☁️ Cloud Storage**: AWS S3, Google Cloud Storage
3. **🔥 Firebase/Supabase**: Real-time database options
4. **💾 Persistent Disks**: Available on Render paid tiers

## 🎪 Demo Usage

### Perfect for Customer Demonstrations

1. **🧹 Start Clean**: Data automatically resets or use DELETE endpoint
2. **🔗 Configure Atlan**: Point webhook to your secure endpoint
3. **📝 Create Request**: Make data access request in Atlan
4. **✨ Show Magic**: Real-time webhook appears in beautiful dashboard
5. **📊 Explore Analytics**: Filter, drill down, show JSON details
6. **🔄 Reset for Next Demo**: Automatic or manual data clearing

### Presentation Tips

- **📺 Full Screen**: Dashboard designed for projector/screen sharing
- **⚡ Real-Time**: Create live requests during presentations
- **🎨 Visual Appeal**: Professional charts and metrics for business audiences
- **🔍 Technical Deep-Dive**: Raw JSON viewer for technical audiences

## 🚨 Troubleshooting

### Common Issues

#### Webhook Authentication Failures
```
Error: 401 Unauthorized from Atlan
```
**Solutions:**
1. Verify `secret-key` header is being sent by Atlan
2. Check `WEBHOOK_SECRET` environment variable matches Atlan
3. Use webhook.site to capture exact request format
4. Confirm Atlan is using latest webhook secret

#### Dashboard Shows No Data
```
"No webhook data found" message
```
**Solutions:**
1. Check if API service is running and responding
2. Verify webhook authentication is working (test with curl)
3. Service may have restarted (data clears automatically)
4. Check API logs for webhook receipt confirmation

#### Service Spinning/Slow Response
```
502 Bad Gateway or long loading times
```
**Solutions:**
1. **Render Free Tier**: Services sleep after 15 minutes, first request takes 30+ seconds
2. **Just wait**: Subsequent requests will be fast
3. **Keep-alive**: Use cron service to ping API every 14 minutes
4. **Upgrade**: Paid tiers don't sleep

### Debug Tools

```bash
# Check service health
curl https://your-api-url.onrender.com/

# View current configuration
curl https://your-api-url.onrender.com/config

# Test authentication
curl -X POST https://your-api-url.onrender.com/webhook \
  -H "secret-key: test-secret" \
  -d '{"test": "data"}'

# Check webhook data
curl https://your-api-url.onrender.com/webhooks
```

## 📚 Documentation

- **[🚀 Deployment Guide](DEPLOYMENT.md)** - Complete deployment instructions
- **[🏢 Multi-Tenant Guide](MULTI_TENANT.md)** - Multi-customer setup
- **[🔒 Security Guide](SECURITY.md)** - Security considerations
- **[🧠 AI Context](CONTEXT.md)** - Complete system context for AI assistants

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help

1. **📖 Check Documentation**: Start with relevant guide above
2. **🐛 Common Issues**: Review troubleshooting section
3. **🔍 Search Issues**: Check existing GitHub issues
4. **💬 Create Issue**: Detailed bug reports or feature requests

### What to Include in Issues

- **Environment**: Local development vs deployed (Render/etc)
- **Error Messages**: Full error text and HTTP status codes
- **Request Format**: What you're sending to the webhook
- **Expected vs Actual**: What should happen vs what does happen
- **Steps to Reproduce**: Detailed reproduction steps

## 🏷️ Tags

`webhook` `atlan` `data-governance` `fastapi` `streamlit` `dashboard` `analytics` `render` `multi-tenant` `demo` `real-time`

---

**Built with ❤️ for the data governance community**

**⭐ Star this repo if it helps with your Atlan integrations!** 