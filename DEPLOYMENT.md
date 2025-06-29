# 🚀 Deployment Guide - Render

This guide walks you through deploying your webhook dashboard to Render for **free hosting**.

## 📋 Prerequisites

- ✅ GitHub account
- ✅ Render account (free at render.com)
- ✅ Your Atlan webhook secret key: `f3a225c-f1db-430d-8a73-818a9133df92`

## 🔧 Step 1: Push to GitHub

### 1.1 Create GitHub Repository

1. Go to [github.com](https://github.com) and create a new repository
2. Name it: `access-request-dashboard` (or your preferred name)
3. Set it to **Public** (required for Render free tier)
4. **Don't** initialize with README (we already have files)

### 1.2 Push Your Code

```bash
# Add GitHub as remote (replace with YOUR username)
git remote add origin https://github.com/YOUR_USERNAME/access-request-dashboard.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🌐 Step 2: Deploy API to Render

### 2.1 Create API Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **"New"** → **"Web Service"**
3. Connect your GitHub repository
4. Configure:

```
Name: access-request-api
Environment: Python 3
Region: Choose closest to you
Branch: main
Root Directory: api
Build Command: pip install -r requirements.txt
Start Command: python main.py
```

### 2.2 Environment Variables

Add these environment variables in Render:

```
WEBHOOK_SECRET = f3a225c-f1db-430d-8a73-818a9133df92
REQUIRE_SIGNATURE = True
```

### 2.3 Deploy

- Click **"Create Web Service"**
- Wait for deployment (5-10 minutes)
- Your API will be available at: `https://access-request-api.onrender.com`

## 📊 Step 3: Deploy Dashboard to Render

### 3.1 Create Dashboard Service

1. Click **"New"** → **"Web Service"** (again)
2. Connect the same GitHub repository
3. Configure:

```
Name: access-request-dashboard
Environment: Python 3
Region: Same as API
Branch: main
Root Directory: ui
Build Command: pip install -r requirements.txt
Start Command: streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
```

### 3.2 Environment Variables

Add this environment variable:

```
API_URL = https://access-request-api.onrender.com
```

(Use your actual API URL from Step 2)

### 3.3 Deploy

- Click **"Create Web Service"**
- Wait for deployment (5-10 minutes)
- Your dashboard will be available at: `https://access-request-dashboard.onrender.com`

## 🔗 Step 4: Connect to Atlan

### 4.1 Update Atlan Webhook Configuration

1. In Atlan, go to your webhook settings
2. Update the webhook URL to: `https://access-request-api.onrender.com/webhook`
3. Ensure the secret key matches: `f3a225c-f1db-430d-8a73-818a9133df92`

### 4.2 Test Production Webhook

1. Trigger a test webhook from Atlan
2. Check your dashboard: `https://access-request-dashboard.onrender.com`
3. Verify the data appears correctly

## 🛠️ Step 5: Verify Deployment

### 5.1 Test API Endpoints

```bash
# Check API health
curl https://access-request-api.onrender.com/

# Check configuration
curl https://access-request-api.onrender.com/config

# Check stored webhooks
curl https://access-request-api.onrender.com/webhooks
```

### 5.2 Test Dashboard

1. Open: `https://access-request-dashboard.onrender.com`
2. Verify all features work:
   - Metrics display
   - Charts render
   - Data table shows webhooks
   - Filters work properly

## 🔄 Step 6: Update and Maintain

### 6.1 Making Changes

```bash
# Make your changes locally
git add .
git commit -m "Update: description of changes"
git push

# Render will auto-deploy from GitHub
```

### 6.2 Monitor Services

- Both services auto-deploy when you push to GitHub
- Check Render dashboard for deployment logs
- Services sleep after 15 minutes of inactivity (free tier)
- First request after sleep takes ~30 seconds to wake up

## 🚨 Troubleshooting

### Common Issues

**"Build failed"**
- Check the logs in Render dashboard
- Verify requirements.txt files are correct
- Ensure Python version compatibility

**"Service unavailable"**
- Services sleep on free tier
- Wait 30 seconds for first request after inactivity
- Check if service crashed in Render logs

**"Webhook not appearing in dashboard"**
- Verify API_URL environment variable is correct
- Check API is receiving webhooks: `/webhooks` endpoint
- Ensure services can communicate (both must be deployed)

**"Invalid signature" errors**
- Verify WEBHOOK_SECRET matches Atlan exactly
- Check Atlan webhook configuration
- Test with `/webhook/test` endpoint first

## 💰 Cost Information

### Render Free Tier Includes:
- ✅ 750 hours/month (enough for 24/7 for both services)
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Auto-deploy from GitHub
- ✅ No credit card required

### Limitations:
- ⚠️ Services sleep after 15 minutes of inactivity
- ⚠️ 30-second cold start after sleeping
- ⚠️ Public repositories only
- ⚠️ Limited to 512MB RAM

## 🎯 Production URLs

After deployment, your URLs will be:

- **API**: `https://access-request-api.onrender.com`
- **Dashboard**: `https://access-request-dashboard.onrender.com` 
- **API Docs**: `https://access-request-api.onrender.com/docs`
- **Webhook Endpoint**: `https://access-request-api.onrender.com/webhook`

## 🔐 Security Notes

- ✅ HTTPS automatically enabled
- ✅ Webhook signature verification active
- ✅ Environment variables securely stored
- ✅ No secrets in repository
- ✅ API endpoints protected

Your production deployment is now **secure and ready for real webhook traffic**!

## 📞 Support

If you need help:
1. Check Render logs for detailed error messages
2. Test locally first to isolate issues
3. Verify environment variables are set correctly
4. Use `/webhook/test` endpoint for debugging 