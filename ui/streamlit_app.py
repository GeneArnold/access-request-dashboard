import streamlit as st
import json
import os
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Data Access Requests Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .status-approved {
        color: #52c41a;
        font-weight: bold;
    }
    .status-pending {
        color: #faad14;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def load_webhook_data():
    """Load webhook data from the API or local file"""
    # Try API first (for production)
    api_url = os.getenv("API_URL", "http://localhost:8080")
    
    try:
        import requests
        response = requests.get(f"{api_url}/webhooks", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("webhooks", [])
    except Exception as e:
        print(f"Failed to load from API: {e}")
    
    # Fallback to local file (for local development)
    webhook_file = "../data/webhooks.json"
    if os.path.exists(webhook_file):
        try:
            with open(webhook_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return timestamp_str

def main():
    # Header
    st.markdown('<h1 class="main-header">📊 Data Access Requests Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    webhooks = load_webhook_data()
    
    if not webhooks:
        st.warning("No webhook data found. Make sure your FastAPI is running and receiving webhooks!")
        st.info("API Endpoint: `/webhook` - Send POST requests here")
        return
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Extract data for filtering
    requestors = list(set(w['payload']['requestor'] for w in webhooks))
    asset_types = list(set(w['payload']['asset_details']['type_name'] for w in webhooks))
    connectors = list(set(w['payload']['asset_details']['connector_name'] for w in webhooks))
    
    selected_requestor = st.sidebar.selectbox("Requestor", ["All"] + requestors)
    selected_asset_type = st.sidebar.selectbox("Asset Type", ["All"] + asset_types)
    selected_connector = st.sidebar.selectbox("Connector", ["All"] + connectors)
    
    # Filter data
    filtered_webhooks = webhooks
    if selected_requestor != "All":
        filtered_webhooks = [w for w in filtered_webhooks if w['payload']['requestor'] == selected_requestor]
    if selected_asset_type != "All":
        filtered_webhooks = [w for w in filtered_webhooks if w['payload']['asset_details']['type_name'] == selected_asset_type]
    if selected_connector != "All":
        filtered_webhooks = [w for w in filtered_webhooks if w['payload']['asset_details']['connector_name'] == selected_connector]
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Requests", len(filtered_webhooks))
    
    with col2:
        approved_count = sum(1 for w in filtered_webhooks if w['payload']['approval_details']['approvers'])
        st.metric("Approved", approved_count)
    
    with col3:
        pending_count = len(filtered_webhooks) - approved_count
        st.metric("Pending", pending_count)
    
    with col4:
        unique_requestors = len(set(w['payload']['requestor'] for w in filtered_webhooks))
        st.metric("Unique Requestors", unique_requestors)
    
    # Charts
    st.subheader("📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Requests by Asset Type
        asset_type_counts = {}
        for w in filtered_webhooks:
            asset_type = w['payload']['asset_details']['type_name']
            asset_type_counts[asset_type] = asset_type_counts.get(asset_type, 0) + 1
        
        if asset_type_counts:
            fig_pie = px.pie(
                values=list(asset_type_counts.values()),
                names=list(asset_type_counts.keys()),
                title="Requests by Asset Type"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Requests by Connector
        connector_counts = {}
        for w in filtered_webhooks:
            connector = w['payload']['asset_details']['connector_name']
            connector_counts[connector] = connector_counts.get(connector, 0) + 1
        
        if connector_counts:
            fig_bar = px.bar(
                x=list(connector_counts.keys()),
                y=list(connector_counts.values()),
                title="Requests by Connector",
                labels={'x': 'Connector', 'y': 'Count'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
    # Recent Requests Table
    st.subheader("📋 Recent Requests")
    
    # Prepare data for table
    table_data = []
    for w in filtered_webhooks[-10:]:  # Show last 10 requests
        payload = w['payload']
        approver_info = ""
        status = "Pending"
        
        if payload['approval_details']['approvers']:
            approver = payload['approval_details']['approvers'][0]
            approver_info = f"{approver['name']} - {approver['comment']}"
            status = "Approved"
        
        table_data.append({
            "Asset": payload['asset_details']['name'],
            "Type": payload['asset_details']['type_name'],
            "Requestor": payload['requestor'],
            "Status": status,
            "Approver": approver_info,
            "Requested": format_timestamp(payload['request_timestamp']),
            "Received": format_timestamp(w.get('received_at', ''))
        })
    
    df = pd.DataFrame(table_data)
    
    # Style the dataframe
    def highlight_status(val):
        if val == "Approved":
            return 'color: #52c41a; font-weight: bold'
        elif val == "Pending":
            return 'color: #faad14; font-weight: bold'
        return ''
    
    styled_df = df.style.map(highlight_status, subset=['Status'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Detailed View
    st.subheader("🔍 Detailed View")
    
    if filtered_webhooks:
        selected_index = st.selectbox(
            "Select a request to view details:",
            range(len(filtered_webhooks)),
            format_func=lambda x: f"{filtered_webhooks[x]['payload']['asset_details']['name']} - {filtered_webhooks[x]['payload']['requestor']}"
        )
        
        selected_webhook = filtered_webhooks[selected_index]
        
        # Display detailed information
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Asset Details**")
            asset = selected_webhook['payload']['asset_details']
            st.write(f"**Name:** {asset['name']}")
            st.write(f"**Type:** {asset['type_name']}")
            st.write(f"**Database:** {asset['database_name']}")
            st.write(f"**Schema:** {asset['schema_name']}")
            st.write(f"**Connector:** {asset['connector_name']}")
            
            if asset['url']:
                st.markdown(f"[View in Atlan]({asset['url']})")
        
        with col2:
            st.markdown("**Request Details**")
            payload = selected_webhook['payload']
            st.write(f"**Requestor:** {payload['requestor']}")
            st.write(f"**Email:** {payload['requestor_email']}")
            st.write(f"**Requested:** {format_timestamp(payload['request_timestamp'])}")
            
            if payload['approval_details']['approvers']:
                approver = payload['approval_details']['approvers'][0]
                st.write(f"**Approved by:** {approver['name']}")
                st.write(f"**Approval Comment:** {approver['comment']}")
                st.write(f"**Approved at:** {format_timestamp(approver['approved_at'])}")
            else:
                st.write("**Status:** Pending Approval")
        
        # Form responses
        if payload['forms']:
            st.markdown("**Form Responses**")
            for form in payload['forms']:
                st.write(f"**{form['form_title']}:**")
                for key, value in form['response'].items():
                    st.write(f"  - {key}: {value}")
        
        # Raw JSON
        with st.expander("Raw JSON Data"):
            st.json(selected_webhook)
    
    # Refresh button
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()

if __name__ == "__main__":
    main() 