from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import openai
import json
from .services.email_generation import generate_email_reply
from .settings import settings
from .api.email_ai_endpoint import router as email_ai_router  # Import the new email AI endpoint

client = openai.OpenAI(api_key=settings.openai_api_key)

app = FastAPI(
    title="SmartGold-SmartCompose",
    description="A FastAPI application to replicate the Power Automate flow for generating email replies.",
    version="0.1.0"
)

# Include the new email AI router
app.include_router(email_ai_router)

class Attachment(BaseModel):
    name: str
    contentType: str
    sizeInKB: int
    isInline: bool
    url: Optional[str] = None
    lastModifiedDateTime: Optional[str] = None

class EmailInput(BaseModel):
    domain: str
    projectDescription: Optional[str] = None
    language: Optional[str] = None
    from_email: str = Field(..., alias='from')
    to: Optional[str] = None
    cc: Optional[str] = None
    subject: str
    body: str
    isHtml: bool
    attachments: Optional[List[Attachment]] = None
    knowledgeBaseVectorStore: Optional[str] = None
    functionsPath: str
    apiUrl: str
    replySenderName: Optional[str] = None
    persona: Optional[str] = None
    AiModel: Optional[str] = None  # Added missing attribute
    ReasoningLevel: Optional[str] = None  # Added missing attribute
    receivedDateTime: Optional[str] = None
    importance: Optional[str] = None

class EmailResponse(BaseModel):
    subjectPrefix: Optional[str] = None
    body: str
    confidence: int
    language: str

@app.get("/health")
async def health_check():
    """Health check endpoint to verify service status."""
    try:
        # Check if OpenAI client is configured
        api_key_configured = settings.openai_api_key != "not_configured"
        
        return {
            "status": "healthy",
            "api_key_configured": api_key_configured,
            "default_model": settings.default_ai_model,
            "timestamp": "2025-07-02T00:00:00Z"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-07-02T00:00:00Z"
        }

@app.post("/generate_reply", response_model=EmailResponse)
async def generate_reply(email_input: EmailInput):
    try:
        # Validate OpenAI API key
        if settings.openai_api_key == "not_configured":
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key not configured. Please check your .env file."
            )
        
        response = await generate_email_reply(email_input, client)
        
        # Validate response structure
        if not response or 'body' not in response:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from email generation service"
            )
        
        return response

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
