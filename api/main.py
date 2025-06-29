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

# Configuration
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "f3a225c-f1db-430d-8a73-818a9133df92")  # Your Atlan secret key
REQUIRE_SIGNATURE = os.getenv("REQUIRE_SIGNATURE", "True").lower() == "true"

# Create data directory if it doesn't exist
os.makedirs("../data", exist_ok=True)
WEBHOOK_FILE = "../data/webhooks.json"

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

def verify_webhook_signature(body: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature from Atlan
    
    Args:
        body: Raw request body as bytes
        signature: Signature from the request header
        secret: Your webhook secret key
    
    Returns:
        bool: True if signature is valid
    """
    if not signature:
        return False
    
    try:
        # Remove 'sha256=' prefix if present
        if signature.startswith('sha256='):
            signature = signature[7:]
        elif signature.startswith('sha1='):
            signature = signature[5:]
        
        # Calculate expected signature
        expected = hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()
        
        # Use hmac.compare_digest for secure comparison
        return hmac.compare_digest(signature, expected)
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

@app.get("/")
async def root():
    return {"message": "Webhook Receiver API is running!", "endpoints": ["/webhook", "/webhooks", "/docs"]}

@app.post("/webhook")
async def receive_webhook(
    request: Request,
    x_signature_256: Optional[str] = Header(None, alias="X-Signature-256"),
    x_hub_signature_256: Optional[str] = Header(None, alias="X-Hub-Signature-256"),
    x_signature: Optional[str] = Header(None, alias="X-Signature")
):
    """Receive webhook data and store it with signature verification"""
    try:
        # Get raw body for signature verification
        raw_body = await request.body()
        
        # Check signature if required
        if REQUIRE_SIGNATURE:
            # Try different signature header formats
            signature = x_signature_256 or x_hub_signature_256 or x_signature
            
            if not signature:
                raise HTTPException(
                    status_code=401, 
                    detail="Missing signature header. Expected X-Signature-256, X-Hub-Signature-256, or X-Signature"
                )
            
            if not verify_webhook_signature(raw_body, signature, WEBHOOK_SECRET):
                raise HTTPException(
                    status_code=401, 
                    detail="Invalid webhook signature"
                )
        
        # Parse JSON data
        try:
            json_data = json.loads(raw_body.decode('utf-8'))
            data = WebhookData(**json_data)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid webhook data format: {str(e)}")
        
        # Convert to dict for storage
        webhook_dict = data.model_dump()
        webhook_dict['signature_verified'] = REQUIRE_SIGNATURE  # Track if signature was verified
        
        # Save to file
        save_webhook(webhook_dict)
        
        return {
            "status": "success", 
            "message": "Webhook received and stored",
            "type": data.type,
            "asset_name": data.payload.asset_details.name,
            "signature_verified": REQUIRE_SIGNATURE
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

@app.post("/webhook/test")
async def receive_test_webhook(data: WebhookData):
    """Test endpoint that bypasses signature verification"""
    try:
        # Convert to dict for storage
        webhook_dict = data.model_dump()
        webhook_dict['signature_verified'] = False  # Mark as test data
        webhook_dict['test_webhook'] = True
        
        # Save to file
        save_webhook(webhook_dict)
        
        return {
            "status": "success", 
            "message": "Test webhook received and stored (no signature verification)",
            "type": data.type,
            "asset_name": data.payload.asset_details.name,
            "signature_verified": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing test webhook: {str(e)}")

@app.get("/config")
async def get_config():
    """Get current webhook configuration"""
    return {
        "signature_verification_enabled": REQUIRE_SIGNATURE,
        "secret_key_configured": bool(WEBHOOK_SECRET),
        "secret_key_preview": WEBHOOK_SECRET[:8] + "..." if WEBHOOK_SECRET else None,
        "webhook_file": WEBHOOK_FILE
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080) 