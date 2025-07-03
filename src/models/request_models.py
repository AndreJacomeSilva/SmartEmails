from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class EmailAttachment(BaseModel):
    id: str
    name: str
    contentType: str
    size: int
    contentBytes: Optional[str] = None

class EmailRequest(BaseModel):
    """Model matching Power Automate trigger body"""
    domain: str
    from_email: str = Field(alias="from")
    to: List[str]
    cc: Optional[List[str]] = []
    subject: str
    body: str
    bodyFormat: str = "html"
    attachments: Optional[List[EmailAttachment]] = []
    originalMailbox: Optional[str] = None
    emailId: Optional[str] = None
    
    class Config:
        populate_by_name = True

class OpenAIMessage(BaseModel):
    role: str
    content: Any

class FunctionCall(BaseModel):
    id: str
    type: str = "function"
    function: Dict[str, Any]

class OpenAIRequest(BaseModel):
    model: str
    input: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: str = "auto"
    max_output_tokens: int = 4096
    temperature: Optional[float] = None
    service_tier: str = "auto"
    stream: bool = False
    reasoning: Optional[Dict[str, Any]] = None
    previous_response_id: Optional[str] = None
    parallel_tool_calls: bool = True
    instructions: Optional[str] = None
    text: Optional[Dict[str, Any]] = None

class OpenAIOutput(BaseModel):
    id: str
    type: str
    status: Optional[str] = None
    content: Optional[List[Dict[str, Any]]] = None
    role: Optional[str] = None
    name: Optional[str] = None
    arguments: Optional[str] = None
    call_id: Optional[str] = None

class OpenAIResponse(BaseModel):
    id: str
    object: str
    created_at: int
    status: str
    model: str
    output: List[OpenAIOutput]
    parallel_tool_calls: Optional[bool] = None
    previous_response_id: Optional[str] = None
    reasoning: Optional[Dict[str, Any]] = None
    service_tier: Optional[str] = None
    store: Optional[bool] = None
    temperature: Optional[float] = None
    text: Optional[Dict[str, Any]] = None
    tool_choice: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = None
    top_p: Optional[float] = None
    truncation: Optional[str] = None
    user: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EmailResponse(BaseModel):
    subjectPrefix: str = ""
    body: str
    confidence: int
    language: str = "pt-PT"
