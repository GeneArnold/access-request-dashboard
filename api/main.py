from fastapi import FastAPI, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
import uvicorn
import hmac
import hashlib
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Webhook Receiver", description="Receives and stores webhook data")

# Configuration - Support multiple secrets for multi-tenant deployments
WEBHOOK_SECRETS_RAW = os.getenv("WEBHOOK_SECRET", "f3a225c-f1db-430d-8a73-818a9133df92")
WEBHOOK_SECRETS = [secret.strip() for secret in WEBHOOK_SECRETS_RAW.split(",") if secret.strip()]
REQUIRE_SIGNATURE = os.getenv("REQUIRE_SIGNATURE", "True").lower() == "true"

# Create data directory if it doesn't exist
# Use relative path that works both locally and in production
data_dir = os.getenv("DATA_DIR", "./data")
os.makedirs(data_dir, exist_ok=True)
WEBHOOK_FILE = os.path.join(data_dir, "webhooks.json")

class AssetDetails(BaseModel):
    guid: str
    name: str
    qualified_name: str
    url: str
    type_name: str
    connector_name: str
    database_name: str
    schema_name: str

class Approver(BaseModel):
    name: str
    comment: str
    approved_at: str
    email: str

class ApprovalDetails(BaseModel):
    is_auto_approved: bool
    approvers: List[Approver]

class FormResponse(BaseModel):
    form_title: str
    response: Dict[str, Any]

class WebhookPayload(BaseModel):
    asset_details: AssetDetails
    request_timestamp: str
    approval_details: ApprovalDetails
    requestor: str
    requestor_email: str
    requestor_comment: str
    forms: List[FormResponse]

class WebhookData(BaseModel):
    type: str
    payload: WebhookPayload

def load_webhooks():
    """Load existing webhooks from file"""
    if os.path.exists(WEBHOOK_FILE):
        try:
            with open(WEBHOOK_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def save_webhook(webhook_data: dict):
    """Save webhook data to file"""
    webhooks = load_webhooks()
    
    # Add timestamp for when we received it
    webhook_data['received_at'] = datetime.now().isoformat()
    
    webhooks.append(webhook_data)
    
    with open(WEBHOOK_FILE, 'w') as f:
        json.dump(webhooks, f, indent=2)

def verify_webhook_signature(body: bytes, signature: str, secrets: List[str]) -> tuple[bool, Optional[str]]:
    """
    Verify webhook signature against multiple possible secrets
    
    Args:
        body: Raw request body as bytes
        signature: Signature from the request header
        secrets: List of possible webhook secret keys
    
    Returns:
        tuple: (is_valid: bool, matched_secret: Optional[str])
    """
    if not signature or not secrets:
        return False, None
    
    # Remove 'sha256=' prefix if present
    clean_signature = signature
    if signature.startswith('sha256='):
        clean_signature = signature[7:]
    elif signature.startswith('sha1='):
        clean_signature = signature[5:]
    
    # Try each secret
    for secret in secrets:
        try:
            # Calculate expected signature
            expected = hmac.new(
                secret.encode('utf-8'),
                body,
                hashlib.sha256
            ).hexdigest()
            
            # Use hmac.compare_digest for secure comparison
            if hmac.compare_digest(clean_signature, expected):
                return True, secret
        except Exception as e:
            print(f"Signature verification error with secret {secret[:8]}...: {e}")
            continue
    
    return False, None

@app.get("/")
async def root():
    return {"message": "Webhook Receiver API is running!", "endpoints": ["/webhook", "/webhooks", "/config", "/docs"]}

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_signature_256: Optional[str] = Header(None, alias="X-Signature-256"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    x_signature: Optional[str] = Header(None, alias="X-Signature"),
    secret_key: Optional[str] = Header(None, alias="secret-key")
):
    """Receive webhook data and store it with signature verification"""
    try:
        # Get raw body 
        raw_body = await request.body()
        
        # Parse JSON first to check for validation challenges
        try:
            json_data = json.loads(raw_body.decode('utf-8'))
            
            # Check if this is a validation challenge BEFORE signature verification
            if isinstance(json_data, dict):
                # Handle explicit validation fields
                if "challenge" in json_data:
                    return {"challenge": json_data["challenge"]}
                elif "verification_token" in json_data:
                    return {"verification_token": json_data["verification_token"]}
                elif "token" in json_data:
                    return {"token": json_data["token"]}
                elif "key" in json_data:
                    return {"key": json_data["key"]}
                # Handle Atlan-specific validation field
                elif "atlan-webhook" in json_data:
                    return {"atlan-webhook": json_data["atlan-webhook"]}
                # Handle empty JSON or very small payloads as validation challenge
                elif len(json_data) == 0 or (len(json_data) == 1 and any(k in json_data for k in ['test', 'ping', 'validation', 'check'])):
                    return {"status": "success", "message": "Validation challenge detected", "received_data": json_data}
                # If payload looks like validation (no required webhook fields), treat as validation
                elif not all(key in json_data for key in ['type', 'payload']):
                    return {"status": "success", "message": "Non-webhook payload detected - treating as validation", "received_data": json_data}
        except json.JSONDecodeError:
            # If not JSON, might be validation challenge - allow it through
            return {"status": "success", "message": "Validation successful"}
        
        # Now check signature for non-validation requests
        used_secret = None
        if REQUIRE_SIGNATURE:
            # First try secret-key header (Atlan's method)
            if secret_key:
                if secret_key in WEBHOOK_SECRETS:
                    used_secret = secret_key
                else:
                    raise HTTPException(
                        status_code=401, 
                        detail="Invalid secret key - key does not match any configured secrets"
                    )
            else:
                # Fall back to HMAC signature verification
                signature = x_signature_256 or x_hub_signature_256 or x_signature
                
                if not signature:
                    raise HTTPException(
                        status_code=401, 
                        detail="Missing authentication. Expected secret-key header or signature header (X-Signature-256, X-Hub-Signature-256, or X-Signature)"
                    )
                
                is_valid, used_secret = verify_webhook_signature(raw_body, signature, WEBHOOK_SECRETS)
                if not is_valid:
                    raise HTTPException(
                        status_code=401, 
                        detail="Invalid webhook signature - signature does not match any configured secrets"
                    )
        
        # Try to parse as webhook data
        try:
            data = WebhookData(**json_data)
        except ValueError as e:
            # If not valid webhook data, might be validation challenge
            return {
                "status": "success", 
                "message": "Validation successful",
                "received_data": json_data
            }
        
        # Convert to dict for storage
        webhook_dict = data.model_dump()
        webhook_dict['signature_verified'] = REQUIRE_SIGNATURE  # Track if signature was verified
        webhook_dict['verified_with_secret'] = used_secret[:8] + "..." if used_secret else None  # Track which secret was used (partial for security)
        
        # Save to file
        save_webhook(webhook_dict)
        
        return {
            "status": "success", 
            "message": "Webhook received and stored",
            "type": data.type,
            "asset_name": data.payload.asset_details.name,
            "signature_verified": REQUIRE_SIGNATURE,
            "verified_with_secret": used_secret[:8] + "..." if used_secret else None
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@app.get("/webhooks")
async def get_all_webhooks():
    """Get all stored webhook data"""
    webhooks = load_webhooks()
    return {"count": len(webhooks), "webhooks": webhooks}

@app.get("/webhooks/latest")
async def get_latest_webhook():
    """Get the most recent webhook"""
    webhooks = load_webhooks()
    if not webhooks:
        return {"message": "No webhooks found"}
    return webhooks[-1]

@app.delete("/webhooks")
async def clear_webhooks():
    """Clear all stored webhooks"""
    if os.path.exists(WEBHOOK_FILE):
        os.remove(WEBHOOK_FILE)
    return {"message": "All webhooks cleared"}





@app.get("/config")
async def get_config():
    """Get current webhook configuration"""
    return {
        "signature_verification_enabled": REQUIRE_SIGNATURE,
        "secrets_configured": len(WEBHOOK_SECRETS),
        "secret_previews": [secret[:8] + "..." for secret in WEBHOOK_SECRETS] if WEBHOOK_SECRETS else [],
        "webhook_file": WEBHOOK_FILE,
        "multi_tenant_support": len(WEBHOOK_SECRETS) > 1
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port) 