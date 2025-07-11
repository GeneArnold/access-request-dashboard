"""
Atlan Webhook Stories App - NEW VERSION
Interactive demonstration of webhook data with playground features
"""

import streamlit as st
import json
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Atlan Webhook Demo",
    page_icon="📡",
    layout="wide"
)

# API Configuration
API_BASE_URL = "https://access-request-api.onrender.com"
LOCAL_API_URL = "http://localhost:8080"

# Mock webhook payload - fallback when no real data exists
MOCK_WEBHOOK_DATA = {
    "id": "DA-DEMO-SAMPLE",
    "source": "demo_data",
    "requestor": "Gene Arnold",
    "requestor_email": "gene.arnold@company.com", 
    "asset_details": {
        "name": "INSTACART_CUSTOMER_DETAILS",
        "type_name": "Table",
        "connector_name": "snowflake",
        "database_name": "DBT_FOOD_BEVERAGE", 
        "schema_name": "POSTGRES_RDS_DEMO",
        "qualified_name": "default/snowflake/1234567890/DBT_FOOD_BEVERAGE/POSTGRES_RDS_DEMO/INSTACART_CUSTOMER_DETAILS",
        "url": "https://snowflake-partner.atlan.com/assets/b178a72f-e1a5-4326-a1ac-f6b091b4d4dd/overview"
    },
    "form_responses": {
        "purpose": "Marketing campaign analysis for Q1 board presentation",
        "duration": "30 days",
        "business_justification": "Need customer demographics for segmentation analysis"
    },
    "timestamp": "2024-12-30T14:42:00Z"
}

@st.cache_data(ttl=10)  # Cache for 10 seconds to allow real-time updates
def fetch_webhook_data() -> Dict[str, Any]:
    """Fetch real webhook data from API, fall back to mock data"""
    
    # Try production API first, then local
    for api_url in [API_BASE_URL, LOCAL_API_URL]:
        try:
            response = requests.get(f"{api_url}/webhooks", timeout=5)
            if response.status_code == 200:
                data = response.json()
                webhooks = data.get("webhooks", [])  # Extract webhooks array from response
                if webhooks and len(webhooks) > 0:
                    return {
                        "webhooks": webhooks,
                        "source": "real_webhook",
                        "api_url": api_url,
                        "total_webhooks": len(webhooks)
                    }
        except:
            continue
    
    # No real data available, use mock
    return {
        "webhooks": [MOCK_WEBHOOK_DATA],
        "source": "demo_data", 
        "api_url": None,
        "total_webhooks": 1
    }

def format_webhook_for_display(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert real webhook to display format"""
    
    # Handle real Atlan webhook structure
    if "payload" in webhook_data:
        payload = webhook_data["payload"]
        asset_details = payload.get("asset_details", {})
        
        return {
            "source": "atlan_webhook",
            "requestor": payload.get("requestor", "Unknown"),
            "requestor_email": payload.get("requestor_email", "unknown@company.com"),
            "asset_details": {
                "name": asset_details.get("name", "Unknown Asset"),
                "type_name": asset_details.get("type_name", "Unknown"),
                "connector_name": asset_details.get("connector_name", "unknown"),
                "database_name": asset_details.get("database_name", ""),
                "schema_name": asset_details.get("schema_name", ""),
                "qualified_name": asset_details.get("qualified_name", ""),
                "url": asset_details.get("url", "#")
            },
            "form_responses": extract_form_responses(payload.get("forms", [])),
            "timestamp": payload.get("request_timestamp", webhook_data.get("timestamp", "")),
            "approval_details": payload.get("approval_details", {}),
            "raw_webhook": webhook_data
        }
    
    # Handle demo/mock data or other formats
    if isinstance(webhook_data, dict):
        # Ensure we always return a proper structure
        return {
            "source": webhook_data.get("source", "unknown"),
            "requestor": webhook_data.get("requestor", "Unknown"),
            "requestor_email": webhook_data.get("requestor_email", "unknown@company.com"),
            "asset_details": webhook_data.get("asset_details", {
                "name": "Unknown Asset",
                "type_name": "Unknown",
                "connector_name": "unknown",
                "database_name": "",
                "schema_name": "",
                "qualified_name": "",
                "url": "#"
            }),
            "form_responses": webhook_data.get("form_responses", extract_form_responses(webhook_data.get("forms", []))),
            "timestamp": webhook_data.get("timestamp", ""),
            "approval_details": webhook_data.get("approval_details", {}),
            "raw_webhook": webhook_data
        }
    
    # Fallback for unexpected data types
    return {
        "source": "unknown", 
        "requestor": "Unknown",
        "requestor_email": "unknown@company.com",
        "asset_details": {
            "name": "Data Error",
            "type_name": "Unknown",
            "connector_name": "unknown",
            "database_name": "",
            "schema_name": "",
            "qualified_name": "",
            "url": "#"
        },
        "form_responses": {"Error": "Could not parse webhook data"},
        "timestamp": "",
        "approval_details": {},
        "raw_webhook": webhook_data
    }

def extract_form_responses(forms: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Extract all form responses dynamically from Atlan form data"""
    if not forms:
        return {"No form data": "No forms submitted"}
    
    all_responses = {}
    
    for form in forms:
        form_title = form.get("form_title", "Unknown Form")
        response = form.get("response", {})
        
        if response:
            # Add form title as a prefix for clarity
            for key, value in response.items():
                # Handle list values (like ["Red"])
                if isinstance(value, list):
                    display_value = ", ".join(str(v) for v in value)
                else:
                    display_value = str(value)
                
                # Use form title + field name for unique keys
                field_key = f"{form_title} - {key}" if len(forms) > 1 else key
                all_responses[field_key] = display_value
        else:
            all_responses[f"{form_title}"] = "No response data"
    
    return all_responses if all_responses else {"No form responses": "No data available"}

def extract_approval_details(approval_details: Dict[str, Any]) -> str:
    """Extract all approval details dynamically from Atlan approval data"""
    if not approval_details:
        return "No approval details available"
    
    approval_text = ""
    
    # Show auto-approval status
    is_auto_approved = approval_details.get('is_auto_approved', 'Unknown')
    approval_text += f"Auto Approved: {is_auto_approved}\n"
    
    # Show approvers with all their details
    approvers = approval_details.get('approvers', [])
    if approvers:
        approval_text += f"\nApprovers ({len(approvers)}):\n"
        for i, approver in enumerate(approvers, 1):
            approval_text += f"  {i}. {approver.get('name', 'Unknown')}\n"
            
            # Show all available approver fields dynamically
            for key, value in approver.items():
                if key != 'name':  # Already showed name above
                    # Format timestamps nicely
                    if 'at' in key.lower() and isinstance(value, str) and 'T' in value:
                        try:
                            from datetime import datetime
                            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                            formatted_value = dt.strftime("%Y-%m-%d %H:%M:%S UTC")
                        except:
                            formatted_value = value
                    else:
                        formatted_value = value
                    
                    # Format key names nicely
                    display_key = key.replace('_', ' ').title()
                    approval_text += f"     {display_key}: {formatted_value}\n"
        
    else:
        approval_text += "\nNo approvers found"
    
    # Show any other top-level approval fields
    for key, value in approval_details.items():
        if key not in ['is_auto_approved', 'approvers']:
            display_key = key.replace('_', ' ').title()
            approval_text += f"\n{display_key}: {value}"
    
    return approval_text.strip()

def get_form_summary_for_table(forms: List[Dict[str, Any]]) -> str:
    """Get a short summary of form responses for table display"""
    if not forms:
        return "No form data"
    
    responses = extract_form_responses(forms)
    
    # Get the first meaningful response for table summary
    for key, value in responses.items():
        if value and value != "No data available":
            return f"{key}: {value}"[:50] + ("..." if len(f"{key}: {value}") > 50 else "")
    
    return "Form submitted"

def create_webhooks_table(webhooks: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a pandas DataFrame for the webhooks table"""
    
    # Create table data
    table_data = []
    
    for i, webhook in enumerate(webhooks):
        formatted = format_webhook_for_display(webhook)
        
        # Extract time for display
        timestamp = formatted.get('timestamp', '')
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                time_display = dt.strftime("%Y-%m-%d %H:%M")
            except:
                time_display = timestamp[:16] if len(timestamp) > 16 else timestamp
        else:
            time_display = "Unknown"
        
        table_data.append({
            "#": i + 1,
            "Timestamp": time_display,
            "Requestor": formatted.get('requestor', 'Unknown'),
            "Asset Name": formatted['asset_details'].get('name', 'Unknown'),
            "Asset Type": formatted['asset_details'].get('type_name', 'Unknown'),
            "Connector": formatted['asset_details'].get('connector_name', 'unknown'),
            "Purpose": get_form_summary_for_table(webhook.get("payload", {}).get("forms", []))
        })
    
    return pd.DataFrame(table_data)

def main():
    st.title("📡 Atlan Webhook Data - NEW STORIES APP")
    
    # Fetch real webhook data
    webhook_result = fetch_webhook_data()
    all_webhooks = webhook_result["webhooks"]
    data_source = webhook_result["source"]
    api_url = webhook_result["api_url"]
    total_webhooks = webhook_result["total_webhooks"]
    
    # Show data source status
    if data_source == "real_webhook":
        st.success(f"📡 **LIVE DATA** - Connected to API: {api_url}")
        st.markdown(f"**{total_webhooks} total webhook(s) received**")
        if st.button("🔄 Refresh Data"):
            st.cache_data.clear()
            st.rerun()
    else:
        st.warning("📋 **DEMO DATA** - No real webhooks received yet")
        st.markdown("*Submit a data access request in Atlan to see real webhook data here*")
    
    st.markdown("**This is exactly what Atlan sends to your webhook endpoint**")
    st.markdown("---")
    
    # Interactive webhook table
    st.markdown("### 📋 Data Access Requests")
    
    if total_webhooks > 0 and all_webhooks:
        # Create table
        df = create_webhooks_table(all_webhooks)
        
        # Display the table
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Webhook selector (using the same pattern as the working dashboard)
        webhook_options = []
        for idx, webhook in enumerate(all_webhooks):
            formatted = format_webhook_for_display(webhook)
            # Create readable option string
            option = f"#{idx + 1}: {formatted['asset_details'].get('name', 'Unknown')} - {formatted.get('requestor', 'Unknown')}"
            webhook_options.append((option, idx, webhook))
        
        if webhook_options:
            # Dropdown to select webhook
            selected_option = st.selectbox(
                "Select a webhook to view details:",
                options=webhook_options,
                format_func=lambda x: x[0],  # Display the readable string
                help="Choose a specific webhook to see detailed information"
            )
            
            if selected_option:
                selected_webhook = selected_option[2]  # Get the actual webhook data
                webhook_data = format_webhook_for_display(selected_webhook)
            else:
                # Default to first webhook if none selected
                webhook_data = format_webhook_for_display(all_webhooks[0])
        else:
            # No webhooks available, use demo data
            webhook_data = format_webhook_for_display(MOCK_WEBHOOK_DATA)
    else:
        # Fallback to demo data
        webhook_data = format_webhook_for_display(MOCK_WEBHOOK_DATA)
        st.markdown("*No webhook data available - showing demo data*")
        st.markdown("---")
    
    # Main data presentation (existing detailed view)
    st.markdown("### 🎯 Asset Information")
    asset = webhook_data['asset_details']
    
    # Create organized sections
    st.code(f"""
Asset Name: {asset['name']}
Asset Type: {asset['type_name']}
Connector: {asset['connector_name']}
Database: {asset.get('database_name', 'N/A')}
Schema: {asset.get('schema_name', 'N/A')}
Qualified Name: {asset.get('qualified_name', 'N/A')}
URL: {asset.get('url', 'N/A')}
    """)
    
    st.markdown("### 👤 Request Information")
    st.code(f"""
Requestor: {webhook_data['requestor']}
Email: {webhook_data['requestor_email']}
Timestamp: {webhook_data['timestamp']}
    """)
    
    st.markdown("### 📝 Form Responses")
    form = webhook_data['form_responses']
    
    # Dynamic form display - handle any form structure
    if form:
        form_text = ""
        for field_name, field_value in form.items():
            form_text += f"{field_name}: {field_value}\n"
        
        if form_text.strip():
            st.code(form_text.strip())
        else:
            st.code("No form data available")
    else:
        st.code("No form responses submitted")
    
    # Show approval details if available
    if "approval_details" in webhook_data and webhook_data["approval_details"]:
        approval = webhook_data["approval_details"]
        st.markdown("### ✅ Approval Details")
        st.code(extract_approval_details(approval))
    
    st.markdown("### 📄 Complete JSON Payload")
    if data_source == "real_webhook" and "raw_webhook" in webhook_data:
        st.json(webhook_data["raw_webhook"])
    else:
        st.json(webhook_data)
    
    # Fun interactive section - starts closed
    with st.expander("🎮 Interactive Integration Playground", expanded=False):
        st.markdown("**🚀 Art of the Possible - Interactive Demo**")
        
        # Row 1: Approval workflow simulation
        st.markdown("##### 🔄 Automated Workflow Triggers")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("✅ Auto-Approve", type="primary"):
                st.balloons()
                st.success("🎉 Request approved!")
        
        with col2:
            if st.button("📧 Send Alerts"):
                st.success("📨 Slack notification sent!")
                st.info("📩 Email to data steward sent!")
        
        with col3:
            if st.button("🔍 Risk Analysis"):
                st.warning("⚠️ Medium risk detected")
                st.info("🛡️ Additional review required")
        
        with col4:
            if st.button("🎯 Route Request"):
                st.success("📍 Routed to Security Team")
        
        st.divider()
        
        # Row 2: Configuration controls
        st.markdown("##### ⚙️ Smart Configuration")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            approval_type = st.selectbox(
                "Approval Path:",
                ["Automatic", "Manager Review", "Security Review", "Legal Review"]
            )
            
            auto_expire = st.checkbox("⏰ Auto-expire access", value=True)
            send_reminders = st.checkbox("🔔 Send reminders", value=True)
        
        with col2:
            connector_rules = st.multiselect(
                "Connector-specific rules:",
                ["Snowflake PII Check", "S3 Encryption Required", "DB Audit Log", "VPN Required"],
                default=["Snowflake PII Check"]
            )
            
            notification_channels = st.multiselect(
                "Notification channels:",
                ["Email", "Slack", "Teams", "ServiceNow", "Jira"],
                default=["Email", "Slack"]
            )
        
        with col3:
            access_duration = st.slider("Max access duration (days):", 1, 365, 30)
            
            risk_threshold = st.select_slider(
                "Risk tolerance:",
                options=["Low", "Medium", "High", "Critical"],
                value="Medium"
            )
        
        st.divider()
        
        # Row 3: Real-time processing simulation
        st.markdown("##### ⚡ Real-time Processing")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Smart Routing Rules**")
            
            processing_steps = [
                "✅ Webhook received",
                "✅ Data parsed",
                "✅ Asset classification",
                "🔄 Policy evaluation...",
                "⏳ Pending approval"
            ]
            
            for step in processing_steps:
                st.markdown(f"• {step}")
        
        with col2:
            st.markdown("**📊 Integration Status**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Requests Today", str(total_webhooks), f"↑ {total_webhooks}")
                st.metric("Avg Response", "2.1 min", "↓ 0.3 min")
            
            with col_b:
                auto_approved = max(0, total_webhooks - 1)
                st.metric("Auto-Approved", str(auto_approved), f"↑ {auto_approved}")
                manual_review = total_webhooks - auto_approved
                st.metric("Manual Review", str(manual_review), f"↓ {manual_review}")
        
        st.divider()
        
        # Row 4: Integration examples
        st.markdown("##### 🔗 Quick Integrations")
        
        integration_cols = st.columns(5)
        
        with integration_cols[0]:
            if st.button("🎫 Create Jira"):
                st.toast("🎫 Jira ticket created!", icon="✅")
        
        with integration_cols[1]:
            if st.button("📋 Log to SIEM"):
                st.toast("🔐 SIEM event logged!", icon="✅")
        
        with integration_cols[2]:
            if st.button("☁️ Provision AWS"):
                st.toast("☁️ AWS environment spun up!", icon="✅")
        
        with integration_cols[3]:
            if st.button("📈 Update Dashboard"):
                st.toast("📊 Metrics updated!", icon="✅")
        
        with integration_cols[4]:
            if st.button("🔄 Sync to CRM"):
                st.toast("💼 CRM record updated!", icon="✅")
        
        # Fun status indicator
        if st.button("🎮 Simulate Full Workflow"):
            with st.spinner("Processing webhook data..."):
                import time
                time.sleep(1)
            
            st.success("🎉 Complete workflow executed!")
            
            # Show a quick summary using real data
            st.info(f"""
            **Workflow Summary:**
            • Asset: {webhook_data['asset_details']['name']}
            • Requestor: {webhook_data['requestor']}
            • Action: {approval_type}
            • Notifications: {', '.join(notification_channels) if notification_channels else 'None'}
            • Duration: {access_duration} days
            """)
    
    # API Status section
    if data_source == "real_webhook":
        with st.expander("🔧 API Status & Controls", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Connection Status**")
                st.success(f"✅ Connected to: {api_url}")
                st.info(f"📡 Total webhooks received: {total_webhooks}")
                
                if st.button("🧹 Clear All Webhook Data"):
                    try:
                        response = requests.delete(f"{api_url}/webhooks")
                        if response.status_code == 200:
                            st.success("🗑️ All webhook data cleared!")
                            st.cache_data.clear()
                            st.rerun()
                        else:
                            st.error("Failed to clear data")
                    except:
                        st.error("Could not connect to API")
            
            with col2:
                st.markdown("**🔗 API Endpoints**")
                st.code(f"""
Webhook endpoint: {api_url}/webhook
Get all data: {api_url}/webhooks  
Latest webhook: {api_url}/webhooks/latest
Configuration: {api_url}/config
API docs: {api_url}/docs
                """)
    
    st.markdown("---")
    st.markdown("**🎪 Demo Environment** • *Real-time webhook integration with Atlan*")

if __name__ == "__main__":
    main() 