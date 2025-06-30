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

