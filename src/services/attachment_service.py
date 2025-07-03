import os
import httpx
from typing import Dict, Any, Optional
import base64

class AttachmentService:
    def __init__(self):
        self.get_attachment_api = os.getenv("GET_ATTACHMENT_API_URL")
    
    async def get_attachment_content(
        self, 
        email_id: str, 
        attachment_id: str,
        mailbox: Optional[str] = None
    ) -> bytes:
        """Get attachment content from email service - matching Power Automate flow"""
        if not self.get_attachment_api:
            raise ValueError("GET_ATTACHMENT_API_URL not configured")
        
        request_body = {
            "emailId": email_id,
            "attachmentId": attachment_id
        }
        
        if mailbox:
            request_body["mailbox"] = mailbox
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.get_attachment_api,
                json=request_body,
                headers={"content-type": "application/json"}
            )
            response.raise_for_status()
            
            # Parse response - expecting same format as Power Automate
            result = response.json()
            content_bytes = result.get("contentBytes", "")
            
            if content_bytes:
                return base64.b64decode(content_bytes)
            else:
                raise ValueError("No content bytes returned from attachment API")
    
    async def get_attachment_info(
        self,
        email_id: str,
        attachment_id: str,
        mailbox: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get attachment metadata"""
        if not self.get_attachment_api:
            raise ValueError("GET_ATTACHMENT_API_URL not configured")
        
        request_body = {
            "emailId": email_id,
            "attachmentId": attachment_id
        }
        
        if mailbox:
            request_body["mailbox"] = mailbox
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                self.get_attachment_api,
                json=request_body,
                headers={"content-type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
