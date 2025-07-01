"""
Simple Atlan Webhook Data Demo

This demonstrates what data you receive from Atlan webhooks.
Shows REAL webhook data when available, falls back to demo data.
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
                webhooks = response.json()
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
            "id": f"DA-{webhook_data.get('timestamp', '')[:10]}",
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
            "form_responses": {
                "purpose": extract_form_purpose(payload.get("forms", [])),
                "duration": "As specified in request",
                "business_justification": payload.get("requestor_comment", "See approval details")
            },
            "timestamp": payload.get("request_timestamp", webhook_data.get("timestamp", "")),
            "approval_details": payload.get("approval_details", {}),
            "raw_webhook": webhook_data
        }
    
    # Handle demo/mock data or other formats
    if isinstance(webhook_data, dict):
        # Ensure we always return a proper structure
        return {
            "id": webhook_data.get("id", "Unknown"),
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
            "form_responses": webhook_data.get("form_responses", {
                "purpose": "No purpose specified",
                "duration": "Unknown",
                "business_justification": "No justification provided"
            }),
            "timestamp": webhook_data.get("timestamp", ""),
            "approval_details": webhook_data.get("approval_details", {}),
            "raw_webhook": webhook_data
        }
    
    # Fallback for unexpected data types
    return {
        "id": "Unknown",
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
        "form_responses": {
            "purpose": "Error parsing webhook data",
            "duration": "Unknown", 
            "business_justification": "Data parsing error"
        },
        "timestamp": "",
        "approval_details": {},
        "raw_webhook": webhook_data
    }

def extract_form_purpose(forms: List[Dict[str, Any]]) -> str:
    """Extract purpose from Atlan form responses"""
    if not forms:
        return "Data access request submitted"
    
    for form in forms:
        response = form.get("response", {})
        if response:
            # Look for common purpose fields
            for key in ["purpose", "Purpose", "Dataset", "Reason", "Business Justification"]:
                if key in response:
                    return response[key]
    
    return "Data access request submitted"

def create_webhooks_table(webhooks: List[Dict[str, Any]]) -> pd.DataFrame:
    """Create a pandas DataFrame for the webhooks table"""
    
    table_data = []
    for i, webhook in enumerate(webhooks):
        formatted = format_webhook_for_display(webhook)
        
        # Extract time for sorting (most recent first)
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
            "Index": i,
            "Timestamp": time_display,
            "Requestor": formatted.get('requestor', 'Unknown'),
            "Asset Name": formatted['asset_details'].get('name', 'Unknown'),
            "Asset Type": formatted['asset_details'].get('type_name', 'Unknown'),
            "Connector": formatted['asset_details'].get('connector_name', 'unknown'),
            "Purpose": formatted['form_responses'].get('purpose', 'No purpose specified')[:50] + "..." if len(formatted['form_responses'].get('purpose', '')) > 50 else formatted['form_responses'].get('purpose', 'No purpose specified')
        })
    
    # Sort by timestamp descending (most recent first)
    df = pd.DataFrame(table_data)
    if not df.empty:
        # Sort by index descending to show most recent webhooks first
        df = df.sort_values('Index', ascending=False).reset_index(drop=True)
    
    return df

def main():
    st.title("📡 Atlan Webhook Data")
    
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
        
        # Initialize session state for selected row - ensure it's within bounds
        if 'selected_webhook_index' not in st.session_state:
            st.session_state.selected_webhook_index = 0  # Default to first row
        
        # Ensure selected index is within bounds
        if st.session_state.selected_webhook_index >= len(all_webhooks):
            st.session_state.selected_webhook_index = 0
        
        # Display the table with click functionality
        st.markdown("*Click on any row to view detailed webhook data below*")
        
        # Create clickable table using columns
        header_cols = st.columns([1, 2, 2, 3, 1.5, 1.5, 4])
        header_labels = ["#", "Timestamp", "Requestor", "Asset Name", "Asset Type", "Connector", "Purpose"]
        
        for i, (col, label) in enumerate(zip(header_cols, header_labels)):
            col.markdown(f"**{label}**")
        
        # Add visual separator
        st.markdown("---")
        
        # Display each row as clickable buttons
        for idx, row in df.iterrows():
            row_cols = st.columns([1, 2, 2, 3, 1.5, 1.5, 4])
            
            # Determine if this row is selected
            webhook_index = row['Index']
            is_selected = st.session_state.selected_webhook_index == webhook_index
            
            # Style for selected row
            button_type = "primary" if is_selected else "secondary"
            
            with row_cols[0]:
                if st.button(f"{idx + 1}", key=f"select_{webhook_index}", type=button_type):
                    st.session_state.selected_webhook_index = webhook_index
                    st.rerun()
            
            # Display row data
            for i, col_name in enumerate(["Timestamp", "Requestor", "Asset Name", "Asset Type", "Connector", "Purpose"]):
                with row_cols[i + 1]:
                    if is_selected:
                        st.markdown(f"**{row[col_name]}**")
                    else:
                        st.markdown(f"{row[col_name]}")
        
        st.markdown("---")
        
        # Get selected webhook data - with bounds checking
        if 0 <= st.session_state.selected_webhook_index < len(all_webhooks):
            selected_webhook = all_webhooks[st.session_state.selected_webhook_index]
            webhook_data = format_webhook_for_display(selected_webhook)
            
            # Show which request is being displayed
            if total_webhooks > 1:
                st.info(f"📊 Displaying webhook #{st.session_state.selected_webhook_index + 1} of {total_webhooks}")
        else:
            # Fallback if index is out of bounds
            webhook_data = format_webhook_for_display(all_webhooks[0])
            st.session_state.selected_webhook_index = 0
    
    else:
        # Fallback to demo data
        webhook_data = format_webhook_for_display(MOCK_WEBHOOK_DATA)
        st.markdown("*No webhook data available - showing demo data*")
        st.markdown("---")
    
    # Main data presentation (existing detailed view)
    st.markdown("### 🎯 Asset Information")
    asset = webhook_data['asset_details']
    
    # Create organized sections
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.code(f"""
Asset Name: {asset['name']}
Type: {asset['type_name']}
Database: {asset['database_name']}
Schema: {asset['schema_name']}
Connector: {asset['connector_name']}
Qualified Name: {asset['qualified_name']}
        """)
    
    with col2:
        if asset.get('url') and asset['url'] != "#":
            st.markdown(f"[🔗 View in Atlan]({asset['url']})")
            st.markdown("*Direct link to asset in Atlan catalog*")
        else:
            st.markdown("🔗 Atlan URL")
            st.markdown("*Available in real webhook data*")
    
    st.markdown("### 👤 Request Information")
    st.code(f"""
Request ID: {webhook_data.get('id', 'Unknown')}
Requestor: {webhook_data['requestor']}
Email: {webhook_data['requestor_email']}
Timestamp: {webhook_data['timestamp']}
    """)
    
    st.markdown("### 📝 Form Responses")
    form = webhook_data['form_responses']
    st.code(f"""
Purpose: {form['purpose']}
Duration: {form['duration']}
Business Justification: {form['business_justification']}
    """)
    
    # Show approval details if available (real webhook data)
    if data_source == "real_webhook" and "approval_details" in webhook_data:
        approval = webhook_data["approval_details"]
        if approval:
            st.markdown("### ✅ Approval Details")
            st.code(f"""
Auto-approved: {approval.get('is_auto_approved', 'Unknown')}
Approvers: {len(approval.get('approvers', []))} person(s)
            """)
            
            # Show approver details
            for i, approver in enumerate(approval.get('approvers', [])):
                st.markdown(f"**Approver {i+1}:**")
                st.code(f"""
Name: {approver.get('name', 'Unknown')}
Email: {approver.get('email', 'Unknown')}  
Comment: {approver.get('comment', 'No comment')}
Approved at: {approver.get('approved_at', 'Unknown')}
                """)
    
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