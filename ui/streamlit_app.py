"""
Data Access Request Analytics Dashboard

This Streamlit application provides a beautiful, real-time analytics dashboard for
visualizing data access request webhooks received from Atlan data governance platform.

Key Features:
- Real-time webhook data visualization with auto-refresh capability
- Interactive analytics with filtering and drill-down capabilities
- Professional presentation-ready charts and metrics
- Detailed request inspection with raw JSON viewer
- Demo-friendly interface perfect for customer presentations
- Responsive design for various screen sizes

Dashboard Sections:
1. Header with title and refresh controls
2. Key metrics cards (total, approved, pending requests, unique requestors)
3. Interactive filtering controls (requestor, asset type, connector)
4. Visualization charts (asset type pie chart, connector bar chart)
5. Recent requests table with status indicators
6. Detailed request inspector with expandable JSON viewer

Author: Generated for Atlan webhook demonstration platform
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any, Optional

# ============================================================================
# CONFIGURATION AND SETUP
# ============================================================================

# API connection configuration
# In production, this points to the deployed FastAPI service
# For local development, change to "http://localhost:8080"
API_BASE_URL = "https://access-request-api.onrender.com"

# Dashboard configuration
st.set_page_config(
    page_title="Data Access Request Dashboard",
    page_icon="📊",
    layout="wide",                    # Use full width for better chart presentation
    initial_sidebar_state="expanded"  # Show sidebar by default for filtering
)

# ============================================================================
# UTILITY FUNCTIONS FOR DATA PROCESSING
# ============================================================================

@st.cache_data(ttl=30)  # Cache data for 30 seconds to improve performance
def fetch_webhook_data() -> List[Dict[Any, Any]]:
    """
    Fetch webhook data from the FastAPI backend.
    
    Uses Streamlit's caching mechanism to avoid repeated API calls
    within a short time window, improving dashboard performance.
    
    Returns:
        List[Dict]: List of webhook dictionaries, or empty list if API unavailable
    """
    try:
        # Make request to the FastAPI webhooks endpoint
        response = requests.get(f"{API_BASE_URL}/webhooks", timeout=10)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        data = response.json()
        return data.get("webhooks", [])
    
    except requests.exceptions.RequestException as e:
        # Handle network errors gracefully
        st.error(f"⚠️ Unable to connect to API: {str(e)}")
        st.info("💡 The API service might be starting up (this takes ~30 seconds on Render free tier)")
        return []
    
    except Exception as e:
        # Handle unexpected errors
        st.error(f"❌ Error fetching data: {str(e)}")
        return []

def parse_webhook_data(webhooks: List[Dict]) -> pd.DataFrame:
    """
    Transform raw webhook data into a pandas DataFrame for easier analysis.
    
    Extracts key fields from nested webhook structure and flattens them
    into columns suitable for filtering, charting, and table display.
    
    Args:
        webhooks (List[Dict]): Raw webhook data from API
        
    Returns:
        pd.DataFrame: Processed data with columns for analysis
    """
    if not webhooks:
        # Return empty DataFrame with expected columns if no data
        return pd.DataFrame(columns=[
            'asset_name', 'requestor', 'requestor_email', 'asset_type', 
            'connector', 'database', 'schema', 'request_timestamp', 
            'is_approved', 'approval_status', 'approver_names', 
            'requestor_comment', 'received_at'
        ])
    
    processed_data = []
    
    for webhook in webhooks:
        try:
            # Extract payload data (main webhook content)
            payload = webhook.get('payload', {})
            asset_details = payload.get('asset_details', {})
            approval_details = payload.get('approval_details', {})
            
            # Process approval information
            approvers = approval_details.get('approvers', [])
            is_approved = len(approvers) > 0  # Has approvers = approved
            approval_status = "Approved" if is_approved else "Pending"
            approver_names = ", ".join([approver.get('name', 'Unknown') for approver in approvers])
            
            # Create flattened record for DataFrame
            record = {
                # Asset information
                'asset_name': asset_details.get('name', 'Unknown'),
                'asset_type': asset_details.get('type_name', 'Unknown'),
                'connector': asset_details.get('connector_name', 'Unknown'),
                'database': asset_details.get('database_name', 'Unknown'),
                'schema': asset_details.get('schema_name', 'Unknown'),
                'asset_url': asset_details.get('url', ''),
                
                # Requestor information
                'requestor': payload.get('requestor', 'Unknown'),
                'requestor_email': payload.get('requestor_email', ''),
                'requestor_comment': payload.get('requestor_comment', ''),
                
                # Timing information
                'request_timestamp': payload.get('request_timestamp', ''),
                'received_at': webhook.get('received_at', ''),
                
                # Approval workflow
                'is_approved': is_approved,
                'approval_status': approval_status,
                'approver_names': approver_names,
                'is_auto_approved': approval_details.get('is_auto_approved', False),
                
                # Audit information
                'signature_verified': webhook.get('signature_verified', False),
                'verified_with_secret': webhook.get('verified_with_secret', ''),
                
                # Store original webhook for detailed view
                'raw_webhook': webhook
            }
            
            processed_data.append(record)
            
        except Exception as e:
            # Skip malformed webhook data but log the error
            st.warning(f"⚠️ Skipping malformed webhook data: {str(e)}")
            continue
    
    return pd.DataFrame(processed_data)

def format_timestamp(timestamp_str: str) -> str:
    """
    Format ISO timestamp string for display in the dashboard.
    
    Converts ISO format timestamps to human-readable format,
    handling timezone information and parsing errors gracefully.
    
    Args:
        timestamp_str (str): ISO format timestamp string
        
    Returns:
        str: Formatted timestamp or original string if parsing fails
    """
    if not timestamp_str:
        return "Unknown"
    
    try:
        # Parse ISO format timestamp (with or without timezone)
        if timestamp_str.endswith('Z'):
            # UTC timezone indicator
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        else:
            dt = datetime.fromisoformat(timestamp_str)
        
        # Format for display: "Dec 30, 2024 3:42 PM"
        return dt.strftime("%b %d, %Y %I:%M %p")
    
    except (ValueError, TypeError):
        # Return original string if parsing fails
        return timestamp_str

# ============================================================================
# DASHBOARD HEADER AND TITLE
# ============================================================================

def render_header():
    """
    Render the main dashboard header with title, description, and controls.
    
    Includes auto-refresh toggle and manual refresh button for real-time updates.
    """
    # Main title with icon
    st.title("📊 Data Access Request Dashboard")
    st.markdown("**Real-time analytics for Atlan data governance webhooks**")
    
    # Create columns for header controls
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col2:
        # Auto-refresh toggle
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True, 
                                 help="Automatically refresh data every 30 seconds")
    
    with col3:
        # Manual refresh button
        if st.button("🔄 Refresh Now", help="Manually refresh data"):
            st.cache_data.clear()  # Clear cache to force data refresh
            st.rerun()  # Trigger dashboard rerun
    
    # Add auto-refresh logic
    if auto_refresh:
        # This causes the dashboard to refresh every 30 seconds
        # Note: This is a simple implementation - production dashboards might
        # use more sophisticated real-time update mechanisms
        import time
        time.sleep(30)
        st.rerun()

# ============================================================================
# KEY METRICS DISPLAY (Dashboard Overview Cards)
# ============================================================================

def render_metrics(df: pd.DataFrame):
    """
    Display key metrics in card format across the top of the dashboard.
    
    Shows high-level statistics that give users immediate insight into
    the current state of data access requests.
    
    Args:
        df (pd.DataFrame): Processed webhook data
    """
    if df.empty:
        # Show placeholder metrics when no data is available
        st.info("📭 No webhook data found. Create a data access request in Atlan to see it appear here!")
        return
    
    # Calculate key metrics
    total_requests = len(df)
    approved_requests = len(df[df['is_approved'] == True])
    pending_requests = total_requests - approved_requests
    unique_requestors = df['requestor'].nunique()
    
    # Calculate approval rate as percentage
    approval_rate = (approved_requests / total_requests * 100) if total_requests > 0 else 0
    
    # Display metrics in columns for horizontal layout
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        # Total requests with trend indicator
        st.metric(
            label="📋 Total Requests", 
            value=total_requests,
            help="Total number of data access requests received"
        )
    
    with col2:
        # Approved requests with positive color indicator
        st.metric(
            label="✅ Approved", 
            value=approved_requests,
            delta=f"{approval_rate:.1f}% rate",
            delta_color="normal",
            help="Number of approved data access requests"
        )
    
    with col3:
        # Pending requests with warning color
        st.metric(
            label="⏳ Pending", 
            value=pending_requests,
            help="Number of requests awaiting approval"
        )
    
    with col4:
        # Unique requestors metric
        st.metric(
            label="👥 Unique Requestors", 
            value=unique_requestors,
            help="Number of different people who have made requests"
        )
    
    with col5:
        # Latest request timing
        if not df.empty:
            latest_time = df['received_at'].max()
            formatted_time = format_timestamp(latest_time)
            st.metric(
                label="🕒 Latest Request", 
                value=formatted_time.split(' ')[0],  # Show date only
                delta=formatted_time.split(' ', 1)[1] if ' ' in formatted_time else '',  # Show time as delta
                help="When we received the most recent request"
            )
    
    # Add a visual separator
    st.divider()

# ============================================================================
# FILTERING CONTROLS (Sidebar)
# ============================================================================

def render_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Render filtering controls in the sidebar and apply filters to data.
    
    Provides interactive filtering capabilities for users to drill down
    into specific segments of the webhook data.
    
    Args:
        df (pd.DataFrame): Original processed data
        
    Returns:
        pd.DataFrame: Filtered data based on user selections
    """
    if df.empty:
        return df
    
    # Sidebar header
    st.sidebar.header("🔍 Filters")
    st.sidebar.markdown("Use these filters to drill down into your data")
    
    # Requestor filter (multiselect)
    requestors = st.sidebar.multiselect(
        "👤 Requestor",
        options=sorted(df['requestor'].unique()),
        default=[],  # No default selection (show all)
        help="Filter by specific requestors"
    )
    
    # Asset type filter (multiselect)
    asset_types = st.sidebar.multiselect(
        "🗂️ Asset Type",
        options=sorted(df['asset_type'].unique()),
        default=[],  # No default selection (show all)
        help="Filter by data asset types (Table, View, etc.)"
    )
    
    # Connector filter (multiselect)
    connectors = st.sidebar.multiselect(
        "🔌 Connector",
        options=sorted(df['connector'].unique()),
        default=[],  # No default selection (show all)
        help="Filter by data source connectors"
    )
    
    # Approval status filter (radio buttons)
    approval_filter = st.sidebar.radio(
        "📊 Approval Status",
        options=["All", "Approved Only", "Pending Only"],
        index=0,  # Default to "All"
        help="Filter by approval status"
    )
    
    # Time range filter (date inputs)
    st.sidebar.subheader("📅 Time Range")
    col1, col2 = st.sidebar.columns(2)
    
    # Calculate date range from data
    min_date = pd.to_datetime(df['received_at']).min().date() if not df.empty else datetime.now().date()
    max_date = pd.to_datetime(df['received_at']).max().date() if not df.empty else datetime.now().date()
    
    with col1:
        start_date = st.date_input(
            "From",
            value=min_date,
            min_value=min_date,
            max_value=max_date,
            help="Start date for filtering"
        )
    
    with col2:
        end_date = st.date_input(
            "To",
            value=max_date,
            min_value=min_date,
            max_value=max_date,
            help="End date for filtering"
        )
    
    # Apply filters to DataFrame
    filtered_df = df.copy()
    
    # Apply requestor filter
    if requestors:
        filtered_df = filtered_df[filtered_df['requestor'].isin(requestors)]
    
    # Apply asset type filter
    if asset_types:
        filtered_df = filtered_df[filtered_df['asset_type'].isin(asset_types)]
    
    # Apply connector filter
    if connectors:
        filtered_df = filtered_df[filtered_df['connector'].isin(connectors)]
    
    # Apply approval status filter
    if approval_filter == "Approved Only":
        filtered_df = filtered_df[filtered_df['is_approved'] == True]
    elif approval_filter == "Pending Only":
        filtered_df = filtered_df[filtered_df['is_approved'] == False]
    
    # Apply date range filter
    filtered_df['received_date'] = pd.to_datetime(filtered_df['received_at']).dt.date
    filtered_df = filtered_df[
        (filtered_df['received_date'] >= start_date) & 
        (filtered_df['received_date'] <= end_date)
    ]
    
    # Show filter results summary
    if len(filtered_df) != len(df):
        st.sidebar.success(f"📊 Showing {len(filtered_df)} of {len(df)} requests")
    else:
        st.sidebar.info(f"📊 Showing all {len(df)} requests")
    
    # Clear filters button
    if st.sidebar.button("🗑️ Clear All Filters"):
        st.rerun()  # Refresh to clear filters
    
    return filtered_df

# ============================================================================
# DATA VISUALIZATION (Charts and Graphs)
# ============================================================================

def render_charts(df: pd.DataFrame):
    """
    Render interactive charts for data visualization.
    
    Creates professional-looking charts suitable for customer presentations
    and business analysis using Plotly for interactivity.
    
    Args:
        df (pd.DataFrame): Filtered data to visualize
    """
    if df.empty:
        st.info("📊 No data to visualize. Apply different filters or wait for new webhook data.")
        return
    
    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)
    
    with col1:
        # Asset Type Distribution (Pie Chart)
        st.subheader("🗂️ Asset Type Distribution")
        
        # Count asset types
        asset_type_counts = df['asset_type'].value_counts()
        
        if not asset_type_counts.empty:
            # Create pie chart with custom colors
            fig_pie = px.pie(
                values=asset_type_counts.values,
                names=asset_type_counts.index,
                title="Requests by Asset Type",
                color_discrete_sequence=px.colors.qualitative.Set3  # Professional color palette
            )
            
            # Customize pie chart appearance
            fig_pie.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
            )
            
            # Update layout for better presentation
            fig_pie.update_layout(
                showlegend=True,
                height=400,
                font=dict(size=12),
                title_font_size=14
            )
            
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No asset type data available for visualization")
    
    with col2:
        # Connector Analysis (Bar Chart)
        st.subheader("🔌 Connector Analysis")
        
        # Count connectors
        connector_counts = df['connector'].value_counts()
        
        if not connector_counts.empty:
            # Create horizontal bar chart
            fig_bar = px.bar(
                x=connector_counts.values,
                y=connector_counts.index,
                orientation='h',
                title="Requests by Data Connector",
                color=connector_counts.values,
                color_continuous_scale='Blues'  # Professional blue gradient
            )
            
            # Customize bar chart appearance
            fig_bar.update_traces(
                hovertemplate='<b>%{y}</b><br>Requests: %{x}<extra></extra>'
            )
            
            # Update layout
            fig_bar.update_layout(
                xaxis_title="Number of Requests",
                yaxis_title="Data Connector",
                height=400,
                font=dict(size=12),
                title_font_size=14,
                coloraxis_showscale=False  # Hide color scale
            )
            
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No connector data available for visualization")
    
    # Time Series Chart (if we have enough data)
    st.subheader("📈 Request Timeline")
    
    if len(df) > 1:
        # Group by date for time series
        df['received_date'] = pd.to_datetime(df['received_at']).dt.date
        daily_counts = df.groupby('received_date').size().reset_index(name='requests')
        
        # Create time series line chart
        fig_timeline = px.line(
            daily_counts,
            x='received_date',
            y='requests',
            title="Daily Request Volume",
            markers=True  # Show markers on data points
        )
        
        # Customize timeline chart
        fig_timeline.update_traces(
            hovertemplate='<b>%{x}</b><br>Requests: %{y}<extra></extra>',
            line=dict(width=3, color='#1f77b4')  # Thicker line with professional color
        )
        
        fig_timeline.update_layout(
            xaxis_title="Date",
            yaxis_title="Number of Requests",
            height=300,
            font=dict(size=12),
            title_font_size=14
        )
        
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("📈 Time series visualization will appear when you have more data points")

# ============================================================================
# DATA TABLE DISPLAY (Recent Requests)
# ============================================================================

def render_data_table(df: pd.DataFrame):
    """
    Display recent requests in a formatted table with status indicators.
    
    Shows the most important information in a scannable format with
    color-coded status indicators and interactive features.
    
    Args:
        df (pd.DataFrame): Filtered data to display
    """
    st.subheader("📋 Recent Requests")
    
    if df.empty:
        st.info("📭 No requests to display. Create a data access request in Atlan to see it here!")
        return
    
    # Prepare data for display table
    display_df = df.copy()
    
    # Sort by received time (most recent first)
    display_df['received_datetime'] = pd.to_datetime(display_df['received_at'])
    display_df = display_df.sort_values('received_datetime', ascending=False)
    
    # Format timestamps for display
    display_df['Request Time'] = display_df['request_timestamp'].apply(format_timestamp)
    display_df['Received Time'] = display_df['received_at'].apply(format_timestamp)
    
    # Create status indicator column with emojis
    def get_status_indicator(row):
        if row['is_approved']:
            return "✅ Approved"
        else:
            return "⏳ Pending"
    
    display_df['Status'] = display_df.apply(get_status_indicator, axis=1)
    
    # Select and rename columns for display
    display_columns = {
        'asset_name': 'Asset Name',
        'asset_type': 'Type',
        'connector': 'Connector',
        'requestor': 'Requestor',
        'Status': 'Status',
        'Request Time': 'Requested',
        'Received Time': 'Received'
    }
    
    table_df = display_df[list(display_columns.keys())].rename(columns=display_columns)
    
    # Display the table with custom styling
    st.dataframe(
        table_df,
        use_container_width=True,
        height=400,  # Fixed height with scrolling
        column_config={
            "Asset Name": st.column_config.TextColumn(
                "Asset Name",
                help="Name of the data asset being requested",
                max_chars=50
            ),
            "Status": st.column_config.TextColumn(
                "Status",
                help="Current approval status of the request"
            ),
            "Requestor": st.column_config.TextColumn(
                "Requestor",
                help="Person who made the data access request"
            )
        }
    )
    
    # Add summary information below the table
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Showing", len(table_df), "requests")
    with col2:
        approved_count = len(df[df['is_approved'] == True])
        st.metric("Approved", approved_count, f"of {len(df)}")
    with col3:
        if len(df) > 0:
            approval_rate = (approved_count / len(df)) * 100
            st.metric("Approval Rate", f"{approval_rate:.1f}%")

# ============================================================================
# DETAILED REQUEST INSPECTOR
# ============================================================================

def render_request_inspector(df: pd.DataFrame):
    """
    Provide detailed inspection of individual webhook requests.
    
    Allows users to drill down into specific requests to see all
    available metadata and the raw webhook JSON.
    
    Args:
        df (pd.DataFrame): Filtered data containing requests to inspect
    """
    st.subheader("🔍 Request Inspector")
    
    if df.empty:
        st.info("📭 No requests available for inspection")
        return
    
    # Request selector
    request_options = []
    for idx, row in df.iterrows():
        # Create readable option string
        request_time = format_timestamp(row['received_at'])
        option = f"{row['asset_name']} - {row['requestor']} ({request_time})"
        request_options.append((option, idx))
    
    if request_options:
        # Dropdown to select request
        selected_option = st.selectbox(
            "Select a request to inspect:",
            options=request_options,
            format_func=lambda x: x[0],  # Display the readable string
            help="Choose a specific request to see detailed information"
        )
        
        if selected_option:
            selected_idx = selected_option[1]
            selected_request = df.loc[selected_idx]
            
            # Display detailed information in expandable sections
            
            # Basic Information
            with st.expander("📋 Basic Information", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Asset Details:**")
                    st.write(f"• Name: {selected_request['asset_name']}")
                    st.write(f"• Type: {selected_request['asset_type']}")
                    st.write(f"• Connector: {selected_request['connector']}")
                    st.write(f"• Database: {selected_request['database']}")
                    st.write(f"• Schema: {selected_request['schema']}")
                    
                    # Asset URL link if available
                    if selected_request.get('asset_url'):
                        st.markdown(f"• [🔗 View in Atlan]({selected_request['asset_url']})")
                
                with col2:
                    st.write("**Request Details:**")
                    st.write(f"• Requestor: {selected_request['requestor']}")
                    st.write(f"• Email: {selected_request['requestor_email']}")
                    st.write(f"• Status: {'✅ Approved' if selected_request['is_approved'] else '⏳ Pending'}")
                    st.write(f"• Requested: {format_timestamp(selected_request['request_timestamp'])}")
                    st.write(f"• Received: {format_timestamp(selected_request['received_at'])}")
            
            # Approval Information
            with st.expander("✅ Approval Details"):
                if selected_request['is_approved']:
                    st.success("This request has been approved!")
                    st.write(f"**Approvers:** {selected_request['approver_names']}")
                    if selected_request['is_auto_approved']:
                        st.info("This request was auto-approved")
                else:
                    st.warning("This request is pending approval")
                
                # Show requestor comment if available
                if selected_request['requestor_comment']:
                    st.write("**Requestor Comment:**")
                    st.write(f"_{selected_request['requestor_comment']}_")
            
            # Security Information
            with st.expander("🔒 Security & Audit"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Authentication:**")
                    verified = selected_request.get('signature_verified', False)
                    st.write(f"• Signature Verified: {'✅ Yes' if verified else '❌ No'}")
                    
                    secret_used = selected_request.get('verified_with_secret', '')
                    if secret_used:
                        st.write(f"• Verified with Secret: {secret_used}")
                
                with col2:
                    st.write("**Metadata:**")
                    st.write(f"• Webhook Type: DATA_ACCESS_REQUEST")
                    st.write(f"• Processing Time: {format_timestamp(selected_request['received_at'])}")
            
            # Raw JSON Data
            with st.expander("🗄️ Raw Webhook Data"):
                st.write("**Complete webhook payload as received from Atlan:**")
                
                # Pretty print the JSON with syntax highlighting
                raw_webhook = selected_request.get('raw_webhook', {})
                st.json(raw_webhook)
                
                # Option to download raw data
                json_str = json.dumps(raw_webhook, indent=2)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_str,
                    file_name=f"webhook_{selected_request['asset_name']}_{selected_request['received_at'][:10]}.json",
                    mime="application/json",
                    help="Download the complete webhook data as JSON file"
                )

# ============================================================================
# MAIN DASHBOARD APPLICATION
# ============================================================================

def main():
    """
    Main dashboard application function.
    
    Orchestrates the entire dashboard layout and data flow:
    1. Renders header and controls
    2. Fetches and processes data
    3. Applies filters
    4. Displays metrics, charts, tables, and inspector
    
    This function ties together all the dashboard components into
    a cohesive, interactive analytics experience.
    """
    # Render dashboard header with title and controls
    render_header()
    
    # Fetch webhook data from API
    with st.spinner("🔄 Loading webhook data..."):
        webhook_data = fetch_webhook_data()
    
    # Process raw webhook data into DataFrame
    df = parse_webhook_data(webhook_data)
    
    # Display key metrics at the top
    render_metrics(df)
    
    # Apply filters and get filtered data
    if not df.empty:
        filtered_df = render_filters(df)
    else:
        filtered_df = df
    
    # Main content area with tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📋 Data Table", "🔍 Inspector"])
    
    with tab1:
        # Analytics tab with charts and visualizations
        render_charts(filtered_df)
    
    with tab2:
        # Data table tab with recent requests
        render_data_table(filtered_df)
    
    with tab3:
        # Request inspector tab for detailed analysis
        render_request_inspector(filtered_df)
    
    # Footer with system information
    with st.expander("ℹ️ System Information"):
        st.write("**Dashboard Information:**")
        st.write(f"• API Endpoint: {API_BASE_URL}")
        st.write(f"• Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"• Total Requests in Database: {len(df)}")
        if len(filtered_df) != len(df):
            st.write(f"• Filtered Requests Shown: {len(filtered_df)}")
        
        st.write("**Built for Atlan Data Governance Platform**")
        st.write("This dashboard demonstrates real-time webhook integration capabilities.")

# ============================================================================
# APPLICATION ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run the main dashboard application
    main() 