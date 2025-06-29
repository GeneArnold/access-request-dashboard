# Data Access Request Dashboard

A FastAPI + Streamlit application that receives webhook data and displays it in a beautiful dashboard.

## 🏗️ Architecture

```
Webhook Sender → FastAPI API (receives/stores) → Streamlit UI (displays data)
```

- **FastAPI**: Receives webhooks at `/webhook` endpoint and stores to JSON file
- **Streamlit**: Beautiful dashboard to visualize and filter webhook data
- **Storage**: JSON file (easily replaceable with database later)

## 🚀 Local Development

### Prerequisites

- Python 3.8+
- pip or conda

### Setup

1. **Clone and navigate to project**
   ```bash
   cd access_request_form
   ```

2. **Set up virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install API dependencies**
   ```bash
   cd api
   pip install -r requirements.txt
   cd ..
   ```

4. **Install UI dependencies**
   ```bash
   cd ui
   pip install -r requirements.txt
   cd ..
   ```

### Running Locally

**Terminal 1 - Start FastAPI server:**
```bash
cd api
python main.py
```
- API will run at: http://localhost:8080
- Auto-generated docs: http://localhost:8080/docs

**Terminal 2 - Start Streamlit dashboard:**
```bash
cd ui
streamlit run streamlit_app.py
```
- Dashboard will run at: http://localhost:8501

### Testing the Webhook

**Option 1: Using curl**
```bash
curl -X POST "http://localhost:8080/webhook" \
     -H "Content-Type: application/json" \
     -d '{
       "type": "DATA_ACCESS_REQUEST",
       "payload": {
         "asset_details": {
           "guid": "test-guid-123",
           "name": "TEST_TABLE",
           "qualified_name": "default/test/table",
           "url": "https://example.com/asset",
           "type_name": "Table",
           "connector_name": "snowflake",
           "database_name": "TEST_DB",
           "schema_name": "TEST_SCHEMA"
         },
         "request_timestamp": "2024-01-15T10:30:00Z",
         "approval_details": {
           "is_auto_approved": false,
           "approvers": [
             {
               "name": "john.doe",
               "comment": "Approved for testing",
               "approved_at": "2024-01-15T10:35:00Z",
               "email": "john.doe@company.com"
             }
           ]
         },
         "requestor": "jane.smith",
         "requestor_email": "jane.smith@company.com",
         "requestor_comment": "Need access for analysis",
         "forms": [
           {
             "form_title": "Access Request Form",
             "response": {
               "Purpose": "Data analysis for Q1 report"
             }
           }
         ]
       }
     }'
```

**Option 2: Using the FastAPI docs**
1. Go to http://localhost:8080/docs
2. Click on `/webhook` POST endpoint
3. Click "Try it out"
4. Paste the JSON payload and execute

## 🚀 Deployment to Render

### Step 1: Push to GitHub

1. **Initialize git repo** (if not already done)
   ```bash
   git init
   git add .
   git commit -m "Initial commit: FastAPI + Streamlit webhook receiver"
   ```

2. **Create GitHub repository** and push
   ```bash
   git remote add origin https://github.com/yourusername/access_request_form.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy FastAPI to Render

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `access-request-api`
   - **Environment**: `Python 3`
   - **Build Command**: `cd api && pip install -r requirements.txt`
   - **Start Command**: `cd api && python main.py`
   - **Plan**: `Free`

### Step 3: Deploy Streamlit to Render

1. Click "New" → "Web Service" again
2. Connect the same GitHub repository
3. Configure:
   - **Name**: `access-request-dashboard`
   - **Environment**: `Python 3`
   - **Build Command**: `cd ui && pip install -r requirements.txt`
   - **Start Command**: `cd ui && streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Plan**: `Free`

### Step 4: Update File Paths for Production

After deployment, you'll need to update the file paths since Render might handle directories differently:

1. **Edit `api/main.py`**: Change `../data/webhooks.json` to `./data/webhooks.json`
2. **Edit `ui/streamlit_app.py`**: Change `../data/webhooks.json` to `./data/webhooks.json`
3. **Commit and push changes**

## 📊 Features

### FastAPI Features
- ✅ Webhook endpoint at `/webhook`
- ✅ Data validation using Pydantic models
- ✅ Auto-generated API documentation
- ✅ Get all webhooks: `/webhooks`
- ✅ Get latest webhook: `/webhooks/latest`
- ✅ Clear all data: `DELETE /webhooks`

### Streamlit Dashboard Features
- ✅ Beautiful, responsive UI
- ✅ Real-time metrics (Total, Approved, Pending requests)
- ✅ Interactive charts (Asset types, Connectors)
- ✅ Advanced filtering (Requestor, Asset Type, Connector)
- ✅ Detailed request view with all metadata
- ✅ Raw JSON data inspection
- ✅ Recent requests table with status highlighting

## 🔧 Configuration

### Environment Variables (Optional)
- `WEBHOOK_FILE`: Path to JSON storage file (default: `../data/webhooks.json`)
- `API_HOST`: FastAPI host (default: `0.0.0.0`)
- `API_PORT`: FastAPI port (default: `8080`)

### Production Considerations
- Replace JSON file storage with a proper database (PostgreSQL, MongoDB)
- Add authentication for the dashboard
- Implement webhook signature verification
- Add rate limiting
- Set up monitoring and logging

## 🐛 Troubleshooting

**Issue**: Streamlit shows "No webhook data found"
- **Solution**: Make sure FastAPI is running and has received webhooks

**Issue**: API not receiving webhooks
- **Solution**: Check firewall settings and ensure webhook sender can reach your endpoint

**Issue**: File path errors in production
- **Solution**: Update file paths from `../data/` to `./data/` for Render deployment

## 🚀 Next Steps

1. **Test locally**: Run both services and send test webhooks
2. **Deploy to Render**: Follow deployment steps above
3. **Configure your webhook sender**: Point to your Render API URL
4. **Monitor**: Watch the dashboard populate with real data!

Your webhook endpoint will be: `https://your-api-name.onrender.com/webhook` 