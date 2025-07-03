import os
import json
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from src.models.request_models import OpenAIRequest, OpenAIResponse
from src.config import tools, default_persona
from datetime import datetime

class OpenAIService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.default_model = os.getenv("DEFAULT_AI_MODEL", "gpt-4o-mini")
        self.reasoning_level = os.getenv("REASONING_LEVEL", "medium")
        self.output_format = os.getenv("OUTPUT_FORMAT", "json")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=5, max=60)
    )
    async def call_openai_responses(
        self, 
        messages: List[Dict[str, Any]], 
        tools: List[Dict[str, Any]],
        previous_response_id: Optional[str] = None,
        instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call OpenAI's new /v1/responses endpoint"""
        
        # Prepare system message with instructions
        system_instructions = instructions or default_persona.format(
            current_date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Prepare request body matching Power Automate flow
        request_body = {
            "model": self.default_model,
            "max_output_tokens": 4096,
            "temperature": None if self.default_model.startswith("o") else 0,
            "tool_choice": "auto",
            "service_tier": "flex" if self.default_model.startswith("o") else "auto",
            "stream": False,
            "reasoning": {
                "effort": self.reasoning_level
            },
            "previous_response_id": previous_response_id,
            "parallel_tool_calls": True,
            "instructions": system_instructions,
            "input": messages,
            "tools": tools,
            "text": {
                "format": self.output_format
            }
        }
        
        # Remove None values to match Power Automate flow behavior
        request_body = {k: v for k, v in request_body.items() if v is not None}
        
        try:
            # Use the OpenAI client's responses API if available
            if hasattr(self.client, 'responses'):
                response = self.client.responses.create(**request_body)
                return response.model_dump()
            else:
                raise AttributeError("Responses API not available in OpenAI client")
        except Exception as e:
            # Fallback to direct HTTP call for compatibility
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept-Encoding": "gzip"
            }
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                return response.json()
    
    async def upload_file(self, file_content: bytes, filename: str) -> str:
        """Upload a file to OpenAI for analysis"""
        try:
            # Use the OpenAI client to upload file
            if hasattr(self.client.files, 'create'):
                response = self.client.files.create(
                    file=(filename, file_content),
                    purpose="assistants"
                )
                return response.id
            else:
                raise AttributeError("Files API not available")
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")
    
    async def analyze_document(
        self, 
        file_id: str, 
        prompt: str, 
        system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze a document using OpenAI Responses API"""
        
        # Prepare input with file reference
        input_messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "file",
                        "file": {
                            "id": file_id
                        }
                    }
                ]
            }
        ]
        
        # Use gpt-4.1 for document analysis as shown in Power Automate flow
        request_body = {
            "model": "gpt-4.1",
            "instructions": system_prompt or "You are a helpful assistant that analyzes documents.",
            "input": input_messages
        }
        
        try:
            if hasattr(self.client, 'responses'):
                response = self.client.responses.create(**request_body)
                return response.model_dump()
            else:
                raise AttributeError("Responses API not available")
        except Exception as e:
            # Fallback to HTTP call if needed
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                return response.json()
