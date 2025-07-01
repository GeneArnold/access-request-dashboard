# 🎯 Project Context Documentation

## 📋 Project Overview

### **What We're Building**
A **Data Access Request Webhook Dashboard** - a secure web application that receives webhook notifications from Atlan (a data governance platform) when users request access to data assets, and displays this information in a beautiful, interactive dashboard.

### **Business Problem We're Solving**
The user (Gene Arnold) sells software that integrates with Atlan. When data access requests are made in Atlan, the software pushes webhook data to external systems. Gene needs:
1. A public place to **demonstrate this webhook functionality** to potential customers
2. A **visual dashboard** to show off the data in an appealing way
3. A **secure, production-ready** system that can handle real webhook traffic

### **Why This Solution**
- **FastAPI**: Chosen over Flask for better API performance, automatic documentation, and async support
- **Streamlit**: Chosen for rapid UI development and beautiful data visualization
- **Render**: Chosen for free, reliable hosting with HTTPS and GitHub integration
- **Webhook Security**: Implemented HMAC signature verification for production security

---

## 🏗️ Technical Architecture

### **System Components**
```
Atlan Software → Webhook → FastAPI API → JSON Storage → Streamlit Dashboard
     ↓                                                         ↑
Secret Key Signature ←-----------------------------------> User Interface
```

### **Services**
1. **FastAPI Backend** (`/api/`)
   - Receives webhook POST requests from Atlan
   - Validates webhook signatures using HMAC-SHA256
   - Stores webhook data to JSON file
   - Provides REST API endpoints for data retrieval
   - Runs on port 8080

2. **Streamlit Frontend** (`/ui/`)
   - Fetches data from FastAPI backend
   - Displays interactive dashboard with charts and tables
   - Provides filtering and detailed view capabilities
   - Runs on port 8502 (local) / 8501 (production)

### **Data Flow**
1. Atlan sends webhook with data access request
2. FastAPI validates signature using secret key
3. Valid webhooks stored to `data/webhooks.json`
4. Streamlit fetches data via API endpoints
5. Dashboard displays real-time webhook information

---

## 🔑 Key Configuration

### **Atlan Webhook Settings**
- **Secret Key**: `f3a225c-f1db-430d-8a73-818a9133df92`
- **Webhook URL (Local)**: `http://localhost:8080/webhook`
- **Webhook URL (Production)**: `https://access-request-api.onrender.com/webhook`

### **Environment Variables**
- `WEBHOOK_SECRET`: Atlan's secret key for signature verification
- `REQUIRE_SIGNATURE`: Enable/disable signature verification (True/False)
- `API_URL`: URL for Streamlit to connect to FastAPI (production only)
- `PORT`: Server port (auto-set by Render)
- `DATA_DIR`: Directory for webhook storage (defaults to ./data)

---

## 📁 Project Structure

```
access_request_form/
├── api/                      # FastAPI Backend
│   ├── main.py              # Main FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── render.yaml          # Render deployment config
│   └── config.env.example   # Environment variables template
├── ui/                       # Streamlit Frontend  
│   ├── streamlit_app.py     # Main Streamlit application
│   ├── requirements.txt     # Python dependencies
│   └── render.yaml          # Render deployment config
├── data/                     # Data Storage
│   ├── .gitkeep            # Ensures directory exists in git
│   └── webhooks.json       # Stored webhook data (gitignored)
├── README.md               # Main project documentation
├── DEPLOYMENT.md           # Deployment guide for Render
├── SECURITY.md            # Security implementation guide
├── CONTEXT.md             # This file - project context
├── .gitignore             # Git ignore rules
├── start_local.sh         # Local development startup script
└── idea.txt              # Original project idea/requirements
```

---

## 🔐 Security Implementation

### **Webhook Security Features**
- **HMAC-SHA256 Signature Verification**: Validates webhooks actually come from Atlan
- **Multiple Header Support**: Accepts X-Signature-256, X-Hub-Signature-256, or X-Signature
- **Environment-based Secrets**: No hardcoded secrets in repository
- **Test vs Production Endpoints**: Separate endpoints for development and production use

### **API Endpoints**
- `POST /webhook` - Secure endpoint with signature verification
- `POST /webhook/test` - Development endpoint without signature verification  
- `GET /webhooks` - Retrieve all stored webhooks
- `GET /webhooks/latest` - Get most recent webhook
- `GET /config` - View security configuration
- `DELETE /webhooks` - Clear all stored webhooks
- `GET /docs` - Auto-generated API documentation

---

## 📊 Sample Webhook Payload

The system processes Atlan "DATA_ACCESS_REQUEST" webhooks with this structure:

```json
{
  "type": "DATA_ACCESS_REQUEST",
  "payload": {
    "asset_details": {
      "guid": "b178a72f-e1a5-4326-a1ac-f6b091b4d4dd",
      "name": "INSTACART_CUSTOMER_DETAILS", 
      "qualified_name": "default/snowflake/1663703816/DBT_FOOD_BEVERAGE/POSTGRES_RDS_DEMO/INSTACART_CUSTOMER_DETAILS",
      "url": "https://snowflake-partner.atlan.com/assets/...",
      "type_name": "Table",
      "connector_name": "snowflake",
      "database_name": "DBT_FOOD_BEVERAGE",
      "schema_name": "POSTGRES_RDS_DEMO"
    },
    "request_timestamp": "2025-06-27T19:58:53Z",
    "approval_details": {
      "is_auto_approved": false,
      "approvers": [
        {
          "name": "gene.arnold",
          "comment": "You got it!",
          "approved_at": "2025-06-27T19:59:58Z", 
          "email": "gene.arnold@atlan.com"
        }
      ]
    },
    "requestor": "gene.arnold",
    "requestor_email": "gene.arnold@atlan.com",
    "requestor_comment": "",
    "forms": [
      {
        "form_title": "Data Access Request",
        "response": {
          "Dataset": "Dataset please"
        }
      }
    ]
  }
}
```

---

## 🎨 Dashboard Features

### **Metrics Display**
- Total requests count
- Approved vs pending requests  
- Unique requestors count

### **Visualizations**
- Pie chart: Requests by asset type
- Bar chart: Requests by connector type
- Time-based request trends

### **Interactive Features**
- Filter by requestor, asset type, connector
- Detailed request inspection
- Raw JSON data viewer
- Real-time data refresh
- Responsive design

### **Status Indicators**
- Color-coded approval status (green=approved, yellow=pending)
- Signature verification status
- Test vs production webhook indicators

---

## 🚀 Development Status

### **✅ Completed Features**
- [x] FastAPI webhook receiver with full security
- [x] Streamlit dashboard with all visualizations
- [x] HMAC signature verification 
- [x] Comprehensive error handling
- [x] Local development environment
- [x] Production deployment configuration
- [x] Complete documentation
- [x] Git repository setup
- [x] Environment variable management
- [x] Cross-service communication (API ↔ Dashboard)
- [x] Test endpoints for development
- [x] Auto-generated API documentation

### **🧪 Testing Status**
- [x] Local webhook security testing (signature verification working)
- [x] Test webhook data storage and retrieval
- [x] Dashboard data display and filtering
- [x] API endpoint functionality
- [x] Environment variable loading
- [x] Error handling for invalid signatures

### **📋 Ready for Production**
- [x] Render deployment configurations created
- [x] Environment variables configured
- [x] HTTPS-ready security implementation
- [x] Production file paths fixed
- [x] Auto-deployment from GitHub setup

---

## 🌐 Deployment Information

### **Hosting Platform**: Render (Free Tier)
- **API Service**: FastAPI backend
- **Dashboard Service**: Streamlit frontend  
- **Auto-deploy**: Triggered by GitHub pushes
- **HTTPS**: Automatically enabled
- **Cost**: Free (750 hours/month - enough for 24/7)

### **Production URLs** (After Deployment)
- API: `https://access-request-api.onrender.com`
- Dashboard: `https://access-request-dashboard.onrender.com`
- API Docs: `https://access-request-api.onrender.com/docs`
- Webhook Endpoint: `https://access-request-api.onrender.com/webhook`

### **Deployment Process**
1. Push code to GitHub repository
2. Create API service on Render with environment variables
3. Create Dashboard service on Render with API_URL
4. Update Atlan webhook URL to production endpoint
5. Test with real webhook traffic

---

## 🛠️ Local Development

### **Requirements**
- Python 3.8+
- Virtual environment recommended
- Git for version control

### **Quick Start Commands**
```bash
# Setup (one-time)
./start_local.sh

# Run services (separate terminals)
cd api && python main.py        # API on localhost:8080
cd ui && streamlit run streamlit_app.py  # Dashboard on localhost:8502
```

### **Testing Locally**
```bash
# Check API health
curl http://localhost:8080/

# Test security configuration  
curl http://localhost:8080/config

# Send test webhook (bypasses security)
curl -X POST "http://localhost:8080/webhook/test" \
     -H "Content-Type: application/json" \
     -d '{"type":"DATA_ACCESS_REQUEST", "payload":{...}}'

# View stored webhooks
curl http://localhost:8080/webhooks
```

---

## 🔧 Key Technical Decisions

### **Why FastAPI over Flask**
- Better async performance for webhook handling
- Automatic API documentation generation
- Built-in request validation with Pydantic
- Type hints and better developer experience

### **Why JSON File Storage**
- Simple for demo/prototype purposes
- Easy to inspect and debug
- No database setup required
- Can be easily replaced with proper DB later

### **Why Render over Other Platforms**
- True free tier with no credit card required
- Automatic HTTPS and custom domains
- GitHub integration for auto-deployment
- Reliable uptime and performance

### **Why Streamlit over Custom Frontend**
- Rapid development for data visualization
- Built-in responsive design
- No frontend JavaScript required
- Easy to create interactive dashboards

---

## 🚨 Current Issues & Notes

### **Known Warnings (Fixed)**
- [x] Pydantic `.dict()` deprecation → Changed to `.model_dump()`
- [x] Streamlit `applymap` deprecation → Changed to `.map()`
- [x] Streamlit `experimental_rerun` deprecation → Changed to `.rerun()`

### **Production Considerations**
- Services sleep after 15 minutes on free tier (30-second wake-up)
- Consider database upgrade for high-volume webhooks
- Add monitoring/alerting for webhook failures
- Implement log retention policies

---

## 📝 Next Steps

### **Immediate (Ready Now)**
1. Create GitHub repository
2. Deploy to Render following DEPLOYMENT.md
3. Update Atlan webhook configuration
4. Test production webhooks

### **Future Enhancements**
- Database storage (PostgreSQL/MongoDB)
- User authentication for dashboard
- Webhook retry mechanism
- Email notifications for failed webhooks
- Custom dashboard themes
- Export functionality (CSV/PDF)
- Webhook analytics and trends

---

## 🎯 Success Criteria

The project successfully meets all original requirements:

✅ **Free, safe hosting** - Render provides free HTTPS hosting  
✅ **Webhook receiver** - FastAPI securely receives Atlan webhooks  
✅ **Beautiful UI** - Streamlit dashboard with charts and interactivity  
✅ **Production ready** - Security, documentation, deployment configs complete  
✅ **Demo capability** - Live dashboard to show potential customers  

The system is **production-ready** and can handle real webhook traffic from Atlan while providing an excellent demonstration of the webhook integration capabilities.

---

## 🆘 Getting Help

### **Documentation References**
- `README.md` - General usage and local development
- `DEPLOYMENT.md` - Step-by-step deployment guide  
- `SECURITY.md` - Security implementation details
- `CONTEXT.md` - This file - complete project context

### **Quick Debug Commands**
```bash
# Check if services are running
ps aux | grep "python main.py"
ps aux | grep streamlit

# Test API health
curl http://localhost:8080/config

# View recent logs (check for errors)
tail -f api/logs/* 2>/dev/null || echo "No log files"
```

### **Common Issues**
- Port conflicts: Kill processes with `pkill -f "python main.py"`
- Module not found: Ensure virtual environment is activated
- Signature validation: Check webhook secret key matches Atlan exactly
- Dashboard not loading data: Verify API is running and accessible

This document contains everything needed to understand, develop, deploy, and maintain the Data Access Request Webhook Dashboard project. 


### Webhook Site for testing
https://webhook.site/?utm_source=json-server-dev#!/view/ae1083a0-301f-4145-8064-b71d9638a8ad/bed8fd41-ca51-4cff-9a15-9523c42734d2/1

# Data Access Request Webhook Dashboard - Complete Context

## Project Overview

This is a **webhook demonstration platform** built for showcasing Atlan data governance platform integrations. It receives webhook payloads from Atlan containing data access request information and displays them in a beautiful, real-time analytics dashboard.

**Purpose**: Customer demonstrations of webhook functionality  
**Stack**: FastAPI (webhook receiver) + Streamlit (dashboard)  
**Hosting**: Render.com (free tier)  
**Data Storage**: JSON files (ephemeral, demo-friendly)

## Architecture

### Dual-Service Architecture
```
Atlan → FastAPI Webhook Receiver → JSON Storage ← Streamlit Dashboard
         (Port 8080)                                    (Port 8502)
```

**API Service**: https://access-request-api.onrender.com  
**Dashboard**: https://access-request-dashboard.onrender.com

### Key Components
1. **FastAPI Webhook Receiver** (`api/main.py`) - Secure webhook endpoint with signature verification
2. **Streamlit Dashboard** (`ui/streamlit_app.py`) - Real-time analytics and data visualization
3. **JSON Storage** (`./data/webhooks.json`) - Simple file-based storage for demos

## Critical Security Learnings

### Atlan Authentication Method ⚠️ CRITICAL
**Atlan does NOT use HMAC signatures** like most webhook systems. Instead:

- **Uses**: `secret-key` header with direct key comparison
- **Header**: `secret-key: <webhook-secret-guid>`
- **Verification**: Direct string matching against configured secrets

**This was discovered after extensive debugging** - do NOT attempt to implement HMAC signature verification for Atlan webhooks.

### Multi-Tenant Support
The system supports multiple webhook secrets via comma-separated environment variable:
```bash
WEBHOOK_SECRET="secret1,secret2,secret3"
```

Each webhook is tracked with which secret validated it for audit purposes.

### Authentication Flow
1. **Validation Challenges**: Bypass all security (allows Atlan to validate webhook URLs)
2. **Real Webhooks**: Require either:
   - `secret-key` header (Atlan's method) - **PREFERRED**
   - HMAC signature headers (traditional method) - **FALLBACK**

### Validation Challenge Formats
Atlan sends different validation formats during webhook setup:
- `{"atlan-webhook": "Hello, humans of data! It worked. Excited to see what you build!"}`
- `{"challenge": "value"}`
- `{"verification_token": "value"}`
- `{"token": "value"}`
- `{"key": "value"}`
- Empty JSON `{}`

**All validation challenges are echoed back** to complete Atlan's webhook registration.

## Webhook Payload Structure

### Real Data Access Request
```json
{
    "type": "DATA_ACCESS_REQUEST",
    "payload": {
        "asset_details": {
            "guid": "asset-guid",
            "name": "Asset Name",
            "qualified_name": "database/schema/table",
            "url": "https://atlan-instance.com/assets/...",
            "type_name": "Table|View|Column|etc",
            "connector_name": "snowflake|bigquery|etc",
            "database_name": "database_name",
            "schema_name": "schema_name"
        },
        "request_timestamp": "2025-06-30T19:42:06Z",
        "approval_details": {
            "is_auto_approved": false,
            "approvers": [
                {
                    "name": "approver.name",
                    "comment": "approval comment",
                    "approved_at": "2025-06-30T19:42:32Z",
                    "email": "approver@company.com"
                }
            ]
        },
        "requestor": "requestor.name",
        "requestor_email": "requestor@company.com", 
        "requestor_comment": "reason for access",
        "forms": [
            {
                "form_title": "Data Access Request",
                "response": {
                    "Dataset": "specific dataset requested"
                }
            }
        ]
    }
}
```

## API Endpoints

### Production Endpoints
- `POST /webhook` - **Main webhook receiver** (secure with signature verification)
- `GET /webhooks` - Retrieve all stored webhooks
- `GET /webhooks/latest` - Get most recent webhook
- `GET /config` - View current configuration (shows multi-tenant status)
- `DELETE /webhooks` - Clear all stored data (**intentionally open for demos**)
- `GET /docs` - Auto-generated Swagger documentation

### Security Model
- **Webhook Ingestion**: Fully secured with signature verification
- **Data Management**: Intentionally open for demo convenience
- **Multi-tenant**: Supports multiple Atlan instances/customers

## Deployment and Infrastructure

### Render.com Free Tier Behavior
**Critical Understanding**: Render's free tier has **ephemeral filesystem storage**

**What Happens**:
1. Services spin down after ~15 minutes of inactivity
2. When they spin back up, filesystem resets to deployment state
3. **All webhook data is lost** (stored in JSON files)

**This is PERFECT for demos**:
- ✅ Fresh start for each demo session
- ✅ No customer data mixing between demos  
- ✅ No cleanup required between demonstrations
- ✅ Simple reset mechanism (just wait for spin-down)

### Environment Variables (Persistent)
Environment variables **persist across deployments**:
- `WEBHOOK_SECRET` - Comma-separated webhook secrets
- `REQUIRE_SIGNATURE` - Enable/disable signature verification (default: true)
- `PORT` - Service port (auto-set by Render)

### GitHub Integration
- **Repository**: https://github.com/GeneArnold/access-request-dashboard
- **Auto-deployment**: Render automatically deploys on main branch pushes
- **Deployment time**: ~3-5 minutes

## Dashboard Features

### Real-time Analytics
- **Metrics**: Total requests, approved/pending counts, unique requestors
- **Charts**: Asset types (pie chart), connectors (bar chart)
- **Filtering**: By requestor, asset type, connector
- **Details**: Full request inspection with raw JSON viewer

### UI Components
- Color-coded status indicators (green=approved, yellow=pending)
- Responsive design for demos on various screen sizes
- Auto-refresh capability
- Interactive data exploration

## Development and Testing

### Local Development
```bash
# API (port 8080)
cd api && python main.py

# Dashboard (port 8502) 
cd ui && python -m streamlit run streamlit_app.py
```

### Testing Webhook Security
```bash
# Test secret-key authentication (Atlan method)
curl -X POST localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "secret-key: your-webhook-secret" \
  -d '{"type": "DATA_ACCESS_REQUEST", "payload": {...}}'

# Test validation challenges
curl -X POST localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{"atlan-webhook": "validation message"}'
```

### Debugging Failed Webhooks
1. **Check Render logs**: Dashboard → Service → Logs → Live tail
2. **Use webhook.site**: Capture exact request format from Atlan
3. **Verify secrets**: Ensure webhook secret matches configuration
4. **Check headers**: Confirm `secret-key` header is present

## Known Limitations and Design Decisions

### Intentional Limitations (Demo-Focused)
- **Ephemeral storage**: Data disappears on service restart (good for demos)
- **Open DELETE endpoint**: Anyone can clear data (demo convenience)
- **No user authentication**: Dashboard is publicly viewable (demo accessibility)
- **File-based storage**: Simple JSON files instead of database (demo simplicity)

### Technical Limitations
- **Render free tier**: Services spin down after inactivity
- **No persistence**: Data doesn't survive deployments
- **Single webhook type**: Only handles DATA_ACCESS_REQUEST currently

## Future Enhancement Options

### Persistence Options (When Needed)
1. **Database**: PostgreSQL, MySQL (Render offers free database tiers)
2. **Cloud Storage**: AWS S3, Google Cloud Storage
3. **External Services**: Firebase, Supabase
4. **Render Persistent Disks**: Available on paid tiers

### Security Enhancements (If Required)
1. **API Key Protection**: For DELETE and management endpoints
2. **Dashboard Authentication**: User login system
3. **Rate Limiting**: Prevent webhook spam
4. **IP Whitelisting**: Restrict webhook sources

### Feature Enhancements
1. **Multiple Webhook Types**: Support beyond DATA_ACCESS_REQUEST
2. **Advanced Analytics**: Time-series analysis, trends
3. **Export Functionality**: CSV, PDF report generation
4. **Notification System**: Email/Slack alerts for new requests

## Integration Testing History

### Successful Integration Tests
- ✅ Atlan webhook validation using `{"atlan-webhook": "message"}`
- ✅ Multi-tenant authentication with multiple secrets
- ✅ Real data access request processing and display
- ✅ Dashboard real-time updates via API polling
- ✅ Signature verification bypass for validation challenges
- ✅ Both `secret-key` header and HMAC signature methods

### Failed Approaches (Do Not Retry)
- ❌ **HMAC signature verification for Atlan** - Atlan uses direct secret-key headers
- ❌ **Test endpoints in production** - Removed for security cleanup
- ❌ **Expecting consistent webhook secrets** - Atlan generates new secrets per URL change
- ❌ **Database persistence on free tier** - Render free tier is ephemeral by design

## Demo Script and Customer Presentation

### Typical Demo Flow
1. **Show clean dashboard** (no data)
2. **Configure Atlan webhook** pointing to secure endpoint
3. **Create data access request** in Atlan
4. **Show real-time webhook** appearing in dashboard
5. **Demonstrate analytics** and filtering capabilities
6. **Clear data** for next demo (DELETE endpoint)

### Key Selling Points
- ✅ **Real-time integration** with Atlan
- ✅ **Secure webhook processing** with signature verification
- ✅ **Multi-tenant support** for enterprise customers
- ✅ **Beautiful analytics dashboard** for business users
- ✅ **Easy deployment** and management
- ✅ **Flexible storage options** for production use

This context document should enable any AI assistant to understand the complete system architecture, security model, deployment behavior, and lessons learned during development.

