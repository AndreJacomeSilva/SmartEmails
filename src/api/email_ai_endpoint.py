from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, List, Optional
import json
import asyncio
from src.models.request_models import EmailRequest, EmailResponse
from src.services.openai_service import OpenAIService
from src.services.teams_service import TeamsService
from src.services.attachment_service import AttachmentService
from src.config import tools, default_persona

router = APIRouter(prefix="/api/v1", tags=["email-ai"])

class EmailAIProcessor:
    def __init__(self):
        self.openai_service = OpenAIService()
        self.teams_service = TeamsService()
        self.attachment_service = AttachmentService()
    
    async def process_email(self, email_request: EmailRequest) -> Dict[str, Any]:
        """Main processing logic matching Power Automate flow"""
        
        # Initialize variables matching Power Automate flow
        previous_response_id = None
        function_responses = []
        final_response = None
        
        # Prepare initial system messages and user message
        system_messages = []
        messages = [
            {
                "role": "user", 
                "content": json.dumps({
                    "originalMailbox": email_request.originalMailbox,
                    "to": email_request.to,
                    "cc": email_request.cc,
                    "subject": email_request.subject,
                    "body": email_request.body,
                    "bodyFormat": email_request.bodyFormat,
                    "attachments": [att.dict() for att in email_request.attachments] if email_request.attachments else []
                })
            }
        ]
        
        # Do until loop - max 10 iterations for safety (matching Power Automate pattern)
        for iteration in range(10):
            try:
                print(f"Processing iteration {iteration + 1}")
                
                # Combine system messages, user messages, and function responses
                # This matches the Power Automate union operation:
                # @union(union(variables('SystemMessages'), variables('Messages')), variables('FunctionResponse'))
                all_input = system_messages + messages + function_responses
                
                # Call OpenAI Responses API
                response = await self.openai_service.call_openai_responses(
                    messages=all_input,
                    tools=tools,
                    previous_response_id=previous_response_id,
                    instructions=default_persona
                )
                
                print(f"OpenAI Response ID: {response.get('id')}")
                
                # Set previous response ID for next iteration
                previous_response_id = response.get("id")
                
                # Process output array
                output = response.get("output", [])
                
                # Filter for completed messages (matching Power Automate Query)
                completed_messages = [
                    item for item in output 
                    if item.get("type") == "message" and item.get("status") == "completed"
                ]
                
                if completed_messages:
                    # Get the final response (last completed message)
                    last_message = completed_messages[-1]
                    content = last_message.get("content", [])
                    if content and isinstance(content, list) and len(content) > 0:
                        final_response = content[0].get("text")
                        print(f"Found final response: {final_response[:100]}...")
                        break
                
                # Filter for completed function calls (matching Power Automate Query)
                tools_called = [
                    item for item in output
                    if item.get("type") == "function_call" and item.get("status") == "completed"
                ]
                
                if not tools_called:
                    # No function calls and no completed message - break
                    print("No function calls or completed messages found")
                    break
                
                print(f"Processing {len(tools_called)} function calls")
                
                # Clear function responses for new iteration
                function_responses = []
                
                # Process each function call (matching Power Automate For Each)
                for call in tools_called:
                    print(f"Processing function call: {call.get('name')}")
                    
                    # First append the function call (matching Power Automate logic)
                    # This matches: @removeProperty(removeProperty(removeProperty(items('For_Each_Tool_Called'),'status'),'id'),'role')
                    function_call_entry = {
                        "type": call.get("type"),
                        "name": call.get("name"),
                        "arguments": call.get("arguments"),
                        "call_id": call.get("call_id")
                    }
                    function_responses.append(function_call_entry)
                    
                    # Process the specific function
                    result = await self.process_function_call(call, email_request)
                    
                    # Add function result (matching Power Automate structure)
                    function_result_entry = {
                        "type": "function_call_output",
                        "call_id": call.get("call_id"),
                        "output": result
                    }
                    function_responses.append(function_result_entry)
                
                print(f"Completed iteration {iteration + 1}, continuing...")
                
            except Exception as e:
                error_message = f"Detalhes do erro: {str(e)}"
                print(f"Error in iteration {iteration + 1}: {error_message}")
                
                # Send error alert matching Power Automate
                await self.teams_service.send_alert(
                    error_message,
                    "SmartEmails API Error"
                )
                raise HTTPException(status_code=500, detail=error_message)
        
        if not final_response:
            error_message = "Failed to get response from AI after maximum iterations"
            await self.teams_service.send_alert(
                error_message,
                "SmartEmails API Error"
            )
            raise HTTPException(status_code=500, detail=error_message)
        
        # Parse the JSON response
        try:
            parsed_response = json.loads(final_response)
            return parsed_response
        except json.JSONDecodeError:
            # If not valid JSON, return a basic structure
            return {
                "subjectPrefix": "",
                "body": final_response,
                "confidence": 50,
                "language": "pt-PT"
            }
    
    async def process_function_call(
        self, 
        call: Dict[str, Any], 
        email_request: EmailRequest
    ) -> str:
        """Process individual function calls matching Power Automate Switch logic"""
        function_name = call.get("name")
        arguments_str = call.get("arguments", "{}")
        
        try:
            arguments = json.loads(arguments_str)
        except json.JSONDecodeError:
            arguments = {}
        
        print(f"Processing function: {function_name} with args: {arguments}")
        
        if function_name == "content_not_available":
            # Handle content_not_available case
            subject = arguments.get("Subject", "Unknown")
            
            # Send Teams alert matching Power Automate flow
            await self.teams_service.send_content_not_available_alert(
                domain=email_request.domain,
                from_email=email_request.from_email,
                subject_text=email_request.subject,
                missing_subject=subject
            )
            
            # Return success response matching Power Automate
            return json.dumps({
                "success": True,
                "description": "A equipa do NewEnergy foi avisada desta questão, sobre a qual eu (o assistente) não consegui responder."
            })
        
        elif function_name == "analyze_email_attachment":
            # Handle analyze_email_attachment case
            try:
                email_id = arguments.get("emailId")
                attachment_id = arguments.get("attachmentId")
                attachment_filename = arguments.get("attachmentFileName", "document")
                prompt = arguments.get("prompt")
                system_prompt = arguments.get("systemPrompt")
                
                if not all([email_id, attachment_id, prompt]):
                    return json.dumps({
                        "error": "Missing required parameters for analyze_email_attachment"
                    })
                
                print(f"Getting attachment content for email {email_id}, attachment {attachment_id}")
                
                # Get attachment content (matching Power Automate HTTP call)
                attachment_content = await self.attachment_service.get_attachment_content(
                    email_id=email_id,
                    attachment_id=attachment_id,
                    mailbox=email_request.originalMailbox
                )
                
                print(f"Got attachment content, size: {len(attachment_content)} bytes")
                
                # Upload file to OpenAI (matching Power Automate Upload File)
                file_id = await self.openai_service.upload_file(
                    file_content=attachment_content,
                    filename=attachment_filename
                )
                
                print(f"Uploaded file to OpenAI, file_id: {file_id}")
                
                # Analyze document (matching Power Automate Analyze Document)
                analysis_result = await self.openai_service.analyze_document(
                    file_id=file_id,
                    prompt=prompt,
                    system_prompt=system_prompt
                )
                
                print(f"Analysis complete, processing results...")
                
                # Extract completed messages from analysis (matching Power Automate Query)
                output = analysis_result.get("output", [])
                completed_messages = [
                    item for item in output
                    if item.get("type") == "message" and item.get("status") == "completed"
                ]
                
                if completed_messages:
                    content = completed_messages[-1].get("content", [])
                    if content and isinstance(content, list):
                        analysis_text = content[0].get("text", "Analysis completed")
                        
                        # Return success response matching Power Automate
                        return json.dumps({
                            "success": True,
                            "description": analysis_text
                        })
                
                return json.dumps({
                    "success": True,
                    "description": "Document analyzed successfully"
                })
                
            except Exception as e:
                error_msg = f"Failed to analyze attachment: {str(e)}"
                print(f"Error analyzing attachment: {error_msg}")
                return json.dumps({
                    "error": error_msg
                })
        
        else:
            # Default case - function not implemented
            print(f"Function {function_name} not implemented")
            
            # Send Teams alert matching Power Automate default case
            await self.teams_service.send_function_not_implemented_alert(
                domain=email_request.domain,
                from_email=email_request.from_email,
                subject=email_request.subject,
                function_name=function_name
            )
            
            # Return empty string matching Power Automate default behavior
            return ""

# Create processor instance
processor = EmailAIProcessor()

@router.post("/email/compose", response_model=EmailResponse)
async def compose_email_response(
    email_request: EmailRequest,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Process an email and generate an AI-powered response.
    This endpoint replicates the Power Automate SmartEmails flow functionality.
    
    The endpoint accepts the same input structure as the Power Automate trigger
    and implements the complete flow logic including:
    - OpenAI Responses API integration
    - Function calling for content_not_available and analyze_email_attachment
    - Teams notifications for alerts
    - Retry logic and error handling
    """
    try:
        print(f"Processing email request from {email_request.from_email} with subject: {email_request.subject}")
        result = await processor.process_email(email_request)
        print(f"Successfully processed email, confidence: {result.get('confidence', 'unknown')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        error_message = f"Unexpected error processing email: {str(e)}"
        print(error_message)
        
        # Send error alert in background
        background_tasks.add_task(
            processor.teams_service.send_alert,
            error_message,
            "SmartEmails API - Unexpected Error"
        )
        
        raise HTTPException(status_code=500, detail=error_message)
