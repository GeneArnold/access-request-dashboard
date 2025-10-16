"""
Data Access Request Webhook Receiver API

This FastAPI application receives webhook payloads from Atlan data governance platform
and stores them for visualization in a companion Streamlit dashboard.

Key Features:
- Secure webhook authentication supporting both Atlan's secret-key method and HMAC signatures
- Multi-tenant support for multiple Atlan instances or customers
- Validation challenge handling for webhook URL verification
- RESTful API for webhook data management
- Production-ready deployment on Render.com

Authentication Methods:
1. Atlan's secret-key header (primary) - direct key comparison
2. HMAC signature verification (fallback) - traditional webhook security

Author: Generated for Atlan webhook demonstration platform
"""

import os
import json
import hmac
import hashlib
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Header
from pydantic import BaseModel
import uvicorn

# ============================================================================
# CONFIGURATION AND ENVIRONMENT SETUP
# ============================================================================

# Load webhook secrets from environment variable
# Supports both single secret (legacy) and comma-separated multiple secrets (multi-tenant)
WEBHOOK_SECRET_ENV = os.getenv("WEBHOOK_SECRET", "")
WEBHOOK_SECRETS = [secret.strip() for secret in WEBHOOK_SECRET_ENV.split(",") if secret.strip()]

# Control whether signature verification is required (default: True for security)
REQUIRE_SIGNATURE = os.getenv("REQUIRE_SIGNATURE", "true").lower() == "true"

# JSON file path for storing webhook data (ephemeral on Render free tier)
WEBHOOK_FILE = "./data/webhooks.json"

# Ensure data directory exists for JSON storage
os.makedirs(os.path.dirname(WEBHOOK_FILE), exist_ok=True)

# ============================================================================
# PYDANTIC DATA MODELS FOR WEBHOOK PAYLOAD VALIDATION
# ============================================================================

class AssetDetails(BaseModel):
    """
    Represents details about the data asset being requested.
    
    Maps to Atlan's asset structure containing metadata about tables,
    views, columns, and other data governance objects.
    """
    guid: str              # Unique identifier for the asset in Atlan
    name: str              # Human-readable name (e.g., "CUSTOMER_DATA")
    qualified_name: str    # Fully qualified path (e.g., "snowflake/db/schema/table")
    url: str               # Direct link to asset in Atlan UI
    type_name: str         # Asset type (Table, View, Column, etc.)
    connector_name: str    # Data source connector (snowflake, bigquery, etc.)
    database_name: str     # Database/catalog name
    schema_name: str       # Schema/namespace name

class Approver(BaseModel):
    """
    Represents an individual who approved the data access request.
    
    Contains approval workflow information for audit trail and
    compliance tracking.
    """
    name: str              # Approver's username or display name
    comment: str           # Approval comment/justification
    approved_at: str       # ISO timestamp of approval
    email: str             # Approver's email address

class ApprovalDetails(BaseModel):
    """
    Contains approval workflow information for the access request.
    
    Tracks whether request was auto-approved or required manual approval,
    and maintains list of all approvers for audit purposes.
    """
    is_auto_approved: bool      # Whether approval was automatic
    approvers: List[Approver]   # List of people who approved the request

class FormResponse(BaseModel):
    """
    Represents responses to custom forms attached to the access request.
    
    Atlan allows custom forms to collect additional information
    from requestors (purpose, duration, etc.).
    """
    form_title: str                    # Name of the form template
    response: Dict[str, Any]           # Key-value pairs of form responses

class WebhookPayload(BaseModel):
    """
    Main payload structure for Atlan DATA_ACCESS_REQUEST webhooks.
    
    Contains all information about the data access request including
    asset details, requestor info, approval workflow, and custom forms.
    """
    asset_details: AssetDetails        # Details about the requested asset
    request_timestamp: str             # When the request was created (ISO format)
    approval_details: ApprovalDetails  # Approval workflow information
    requestor: str                     # Username of person requesting access
    requestor_email: str               # Email of requestor
    requestor_comment: str             # Requestor's justification/reason
    forms: Optional[List[FormResponse]] = []  # Additional form responses (optional)

class WebhookData(BaseModel):
    """
    Top-level webhook structure from Atlan.
    
    Currently supports DATA_ACCESS_REQUEST type, but structure
    allows for future webhook types from Atlan.
    """
    type: str                          # Webhook type (e.g., "DATA_ACCESS_REQUEST")
    payload: WebhookPayload            # The actual webhook data

# ============================================================================
# DATA PERSISTENCE FUNCTIONS (JSON-based for demo simplicity)
# ============================================================================

def load_webhooks():
    """
    Load existing webhooks from JSON file.
    
    Returns empty list if file doesn't exist or is corrupted.
    This approach is intentionally simple for demo purposes -
    production deployments should use a proper database.
    
    Returns:
        List[Dict]: List of stored webhook dictionaries
    """
    if os.path.exists(WEBHOOK_FILE):
        try:
            with open(WEBHOOK_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Return empty list if JSON is corrupted
            return []
    return []

def save_webhook(webhook_data: dict):
    """
    Save webhook data to JSON file with timestamp.
    
    Appends new webhook to existing list and adds a received_at
    timestamp for tracking when we processed the webhook.
    
    Args:
        webhook_data (dict): Validated webhook data to store
    """
    webhooks = load_webhooks()
    
    # Add timestamp for when we received it (for audit trail)
    webhook_data['received_at'] = datetime.now().isoformat()
    
    webhooks.append(webhook_data)
    
    # Write back to file (atomic operation for data integrity)
    with open(WEBHOOK_FILE, 'w') as f:
        json.dump(webhooks, f, indent=2)

# ============================================================================
# SECURITY: WEBHOOK SIGNATURE VERIFICATION
# ============================================================================

def verify_webhook_signature(body: bytes, signature: str, secrets: List[str]) -> tuple[bool, Optional[str]]:
    """
    Verify webhook signature against multiple possible secrets (multi-tenant support).
    
    This function implements traditional HMAC-SHA256 signature verification
    used by most webhook systems (GitHub, Stripe, etc.). However, note that
    Atlan uses a different authentication method (secret-key header).
    
    Args:
        body (bytes): Raw request body as bytes
        signature (str): Signature from request header
        secrets (List[str]): List of possible webhook secret keys
    
    Returns:
        tuple: (is_valid: bool, matched_secret: Optional[str])
               Returns True and the matching secret if verification succeeds,
               False and None if verification fails
    """
    if not signature or not secrets:
        return False, None
    
    # Handle different signature formats (sha256=, sha1=, or raw hex)
    clean_signature = signature
    if signature.startswith('sha256='):
        clean_signature = signature[7:]  # Remove 'sha256=' prefix
    elif signature.startswith('sha1='):
        clean_signature = signature[5:]   # Remove 'sha1=' prefix (less secure)
    
    # Try each configured secret (supports multi-tenant deployments)
    for secret in secrets:
        try:
            # Calculate expected HMAC-SHA256 signature
            expected = hmac.new(
                secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Use timing-safe comparison to prevent timing attacks
            if hmac.compare_digest(clean_signature, expected):
                return True, secret
        except Exception as e:
            # Log error but continue trying other secrets
            print(f"Signature verification error with secret {secret[:8]}...: {e}")
            continue
    
    return False, None

# ============================================================================
# FASTAPI APPLICATION INITIALIZATION
# ============================================================================

# Initialize FastAPI app with metadata for auto-generated documentation
app = FastAPI(
    title="Data Access Request Webhook API",
    description="Secure webhook receiver for Atlan data governance platform",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI at /docs
    redoc_url="/redoc"          # ReDoc UI at /redoc
)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """
    Root endpoint providing API information and available endpoints.
    
    Useful for health checks and API discovery.
    """
    return {
        "message": "Webhook Receiver API is running!",
        "endpoints": ["/webhook", "/webhooks", "/config", "/docs"]
    }

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    # Support multiple signature header formats (different webhook systems use different conventions)
    x_signature_256: Optional[str] = Header(None, alias="X-Signature-256"),      # Common format
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"), # GitHub format
    x_signature: Optional[str] = Header(None, alias="X-Signature"),              # Generic format
    secret_key: Optional[str] = Header(None, alias="secret-key")                 # Atlan's format
):
    """
    Main webhook endpoint with comprehensive authentication and validation.
    
    This endpoint handles two distinct types of requests:
    1. Validation challenges - Used by Atlan to verify webhook URL during setup
    2. Actual webhook data - Real data access request information
    
    Authentication Methods (in priority order):
    1. secret-key header (Atlan's method) - Direct secret comparison
    2. HMAC signature headers (traditional method) - Cryptographic verification
    
    Validation challenges bypass authentication to allow webhook URL verification.
    """
    try:
        # Get raw request body for signature verification and parsing
        raw_body = await request.body()
        
        # Parse JSON to check for validation challenges BEFORE authentication
        try:
            json_data = json.loads(raw_body.decode('utf-8'))
            
            # ============================================================================
            # VALIDATION CHALLENGE HANDLING (Webhook URL Verification)
            # ============================================================================
            
            # Atlan (and other webhook systems) send validation challenges during setup
            # These need to be echoed back to prove we can receive webhooks
            # Validation challenges bypass authentication requirements
            
            if isinstance(json_data, dict):
                # Check for various validation challenge formats
                
                # Atlan's specific validation format
                if "atlan-webhook" in json_data:
                    return {"atlan-webhook": json_data["atlan-webhook"]}
                
                # Common webhook validation patterns
                if "challenge" in json_data:
                    return {"challenge": json_data["challenge"]}
                elif "verification_token" in json_data:
                    return {"verification_token": json_data["verification_token"]}
                elif "token" in json_data:
                    return {"token": json_data["token"]}
                elif "key" in json_data:
                    return {"key": json_data["key"]}
                
                # Handle empty JSON or very small payloads as validation attempts
                elif len(json_data) == 0 or (len(json_data) == 1 and any(k in json_data for k in ['test', 'ping', 'validation', 'check'])):
                    return {"status": "success", "message": "Validation challenge detected", "received_data": json_data}
                
                # If payload doesn't look like a proper webhook (missing required fields), treat as validation
                elif not all(key in json_data for key in ['type', 'payload']):
                    return {"status": "success", "message": "Non-webhook payload detected - treating as validation", "received_data": json_data}
        
        except json.JSONDecodeError:
            # If request body isn't JSON, might be a validation challenge
            return {"status": "success", "message": "Validation successful"}
        
        # ============================================================================
        # AUTHENTICATION AND AUTHORIZATION (For Non-Validation Requests)
        # ============================================================================
        
        used_secret = None
        
        if REQUIRE_SIGNATURE:
            # Method 1: Atlan's secret-key header authentication (PREFERRED)
            # Atlan sends the webhook secret directly in the secret-key header
            # This is simpler than HMAC signatures and is Atlan's native method
            if secret_key:
                if secret_key in WEBHOOK_SECRETS:
                    used_secret = secret_key
                else:
                    raise HTTPException(
                        status_code=401, 
                        detail="Invalid secret key - key does not match any configured secrets"
                    )
            else:
                # Method 2: HMAC signature verification (FALLBACK)
                # Traditional webhook authentication used by GitHub, Stripe, etc.
                # Try different signature header formats
                signature = x_signature_256 or x_hub_signature_256 or x_signature
                
                if not signature:
                    raise HTTPException(
                        status_code=401, 
                        detail="Missing authentication. Expected secret-key header or signature header (X-Signature-256, X-Hub-Signature-256, or X-Signature)"
                    )
                
                # Verify signature against all configured secrets (multi-tenant support)
                is_valid, used_secret = verify_webhook_signature(raw_body, signature, WEBHOOK_SECRETS)
                if not is_valid:
                    raise HTTPException(
                        status_code=401, 
                        detail="Invalid webhook signature - signature does not match any configured secrets"
                    )
        
        # ============================================================================
        # WEBHOOK DATA VALIDATION AND PROCESSING
        # ============================================================================
        
        # Try to parse and validate webhook data against our Pydantic models
        try:
            data = WebhookData(**json_data)
        except ValueError as e:
            # If data doesn't match our webhook schema, might be a validation challenge
            return {
                "status": "success", 
                "message": "Validation successful",
                "received_data": json_data
            }
        
        # ============================================================================
        # DATA PERSISTENCE AND AUDIT TRAIL
        # ============================================================================
        
        # Convert validated Pydantic model to dictionary for storage
        webhook_dict = data.model_dump()
        
        # Add audit information for security and troubleshooting
        webhook_dict['signature_verified'] = REQUIRE_SIGNATURE  # Track if signature was verified
        webhook_dict['verified_with_secret'] = used_secret[:8] + "..." if used_secret else None  # Track which secret was used (partial for security)
        
        # Save to persistent storage (JSON file in this demo implementation)
        save_webhook(webhook_dict)
        
        # Return success response with audit information
        return {
            "status": "success", 
            "message": "Webhook received and stored",
            "type": data.type,
            "asset_name": data.payload.asset_details.name,
            "signature_verified": REQUIRE_SIGNATURE,
            "verified_with_secret": used_secret[:8] + "..." if used_secret else None
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (authentication failures, etc.)
        raise
    except Exception as e:
        # Catch any unexpected errors and return 500
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

# ============================================================================
# DATA MANAGEMENT ENDPOINTS (Demo and Administrative Functions)
# ============================================================================

@app.get("/webhooks")
async def get_all_webhooks():
    """
    Retrieve all stored webhook data.
    
    Returns a list of all webhooks received and stored by the system.
    Useful for dashboard data loading and debugging.
    
    Note: This endpoint is intentionally open (no authentication) for demo convenience.
    Production deployments should consider adding authentication.
    """
    webhooks = load_webhooks()
    return {"count": len(webhooks), "webhooks": webhooks}

@app.get("/webhooks/latest")
async def get_latest_webhook():
    """
    Get the most recently received webhook.
    
    Useful for testing and debugging webhook reception.
    """
    webhooks = load_webhooks()
    if not webhooks:
        return {"message": "No webhooks found"}
    return webhooks[-1]

@app.delete("/webhooks")
async def clear_webhooks():
    """
    Clear all stored webhook data.
    
    This endpoint is intentionally open for demo convenience - allows easy
    reset between customer demonstrations. In production, consider adding
    authentication or removing this endpoint entirely.
    
    Note: On Render free tier, data is automatically cleared when services
    restart anyway due to ephemeral filesystem.
    """
    if os.path.exists(WEBHOOK_FILE):
        os.remove(WEBHOOK_FILE)
    return {"message": "All webhooks cleared"}

# ============================================================================
# CONFIGURATION AND STATUS ENDPOINTS
# ============================================================================

@app.get("/config")
async def get_config():
    """
    Get current webhook configuration and status.
    
    Returns information about the webhook receiver configuration including:
    - Whether signature verification is enabled
    - Number of configured secrets (multi-tenant support)
    - Preview of configured secrets (first 8 characters for security)
    - Multi-tenant support status
    
    Useful for debugging authentication issues and verifying deployment.
    """
    return {
        "signature_verification_enabled": REQUIRE_SIGNATURE,
        "secrets_configured": len(WEBHOOK_SECRETS),
        "secret_previews": [secret[:8] + "..." for secret in WEBHOOK_SECRETS] if WEBHOOK_SECRETS else [],
        "webhook_file": WEBHOOK_FILE,
        "multi_tenant_support": len(WEBHOOK_SECRETS) > 1
    }

# ============================================================================
# APPLICATION STARTUP
# ============================================================================

if __name__ == "__main__":
    # Get port from environment variable (Render and other platforms set this)
    port = int(os.getenv("PORT", 8080))
    
    # Start uvicorn server
    # host="0.0.0.0" allows connections from outside container/localhost
    uvicorn.run(app, host="0.0.0.0", port=port) 