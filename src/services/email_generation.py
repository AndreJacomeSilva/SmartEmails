import json
import openai
from typing import List, Optional, Dict, Any
from ..config import default_persona, tools
from ..settings import settings
from .utils import content_not_available, analyze_email_attachment

def extract_confidence_from_response(response_content: str) -> int:
    """Extract confidence score from AI response or calculate based on response quality."""
    try:
        # Try to parse as JSON first
        if response_content.strip().startswith('{'):
            parsed = json.loads(response_content)
            if 'confidence' in parsed:
                return int(parsed['confidence'])
        
        # Fallback: calculate confidence based on response length and content
        if len(response_content) > 100:
            return 85
        elif len(response_content) > 50:
            return 70
        else:
            return 50
    except:
        return 75  # Default confidence

async def generate_email_reply(email_input: Any, client: openai.OpenAI):
    try:
        system_messages = [
            {"role": "system", "content": email_input.persona or default_persona}
        ]

        email_object = {
            "emailId": None,  # Assuming emailId is not available in the input
            "from": email_input.from_email,
            "to": email_input.to,
            "cc": email_input.cc,
            "subject": email_input.subject,
            "attachments": email_input.attachments,
            "body": email_input.body,
            "isHtml": email_input.isHtml,
            "receivedDateTime": email_input.receivedDateTime
        }

        messages = [
            {"role": "user", "content": f"Analisa e processa o seguinte email:\n {email_object}"}
        ]

        # Use the correct attribute name from the model
        model_to_use = email_input.AiModel or settings.default_ai_model

        response = client.chat.completions.create(
            model=model_to_use,
            messages=system_messages + messages,
            tools=tools,
            tool_choice="auto",
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            available_functions = {
                "content_not_available": content_not_available,
                "analyze_email_attachment": analyze_email_attachment,
            }
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_to_call = available_functions.get(function_name)
                
                if function_to_call:
                    try:
                        function_args = json.loads(tool_call.function.arguments)
                        function_response = function_to_call(**function_args)
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": function_response,
                            }
                        )
                    except json.JSONDecodeError as e:
                        # Handle JSON parsing error
                        messages.append(
                            {
                                "tool_call_id": tool_call.id,
                                "role": "tool",
                                "name": function_name,
                                "content": json.dumps({"error": f"Failed to parse arguments: {str(e)}"}),
                            }
                        )
                else:
                    # Call external API for other functions
                    # This is a placeholder for the actual implementation
                    messages.append(
                        {
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps({"success": True, "description": "This is a dummy response from the external API."}),
                        }
                    )
            
            second_response = client.chat.completions.create(
                model=model_to_use,
                messages=messages,
            )
            
            final_content = second_response.choices[0].message.content
            confidence = extract_confidence_from_response(final_content)
            
            return {
                "body": final_content,
                "confidence": confidence,
                "language": email_input.language or "pt-PT"  # Default to Portuguese
            }

        final_content = response_message.content
        confidence = extract_confidence_from_response(final_content)
        
        return {
            "body": final_content,
            "confidence": confidence,
            "language": email_input.language or "pt-PT"  # Default to Portuguese
        }
        
    except Exception as e:
        # Return error response with low confidence
        return {
            "body": f"Erro ao gerar resposta: {str(e)}",
            "confidence": 0,
            "language": email_input.language or "pt-PT"
        }