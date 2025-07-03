# SmartGold-SmartEmails Documentation

Welcome to the documentation for the SmartEmails API.

This API provides a service to generate email replies based on the content of an incoming email and a knowledge base.

## Project Overview

The project is a FastAPI application that replicates the functionality of a Power Automate flow. It receives email data, processes it using an AI model, and returns a generated email reply.

## API Reference

See the API reference for details on the available endpoints and their usage.

# SmartGold-SmartCompose Email AI API

## Overview
This API provides the same functionality as the SmartEmails Power Automate Flow, implemented as a FastAPI endpoint. It uses OpenAI's new Responses API to generate intelligent email replies with support for function calling, document analysis, and Teams notifications.

## New Endpoint: `/api/v1/email/compose`

### Description
Processes an email and generates an AI-powered response using the same logic as the Power Automate flow.

### Features
- **OpenAI Responses API Integration**: Uses the latest `/v1/responses` endpoint with reasoning support
- **Function Calling**: Supports `content_not_available` and `analyze_email_attachment` functions
- **Teams Notifications**: Sends alerts to Microsoft Teams channels
- **Document Analysis**: Analyzes email attachments using OpenAI's file analysis capabilities
- **Retry Logic**: Implements exponential backoff for robust error handling
- **Power Automate Compatibility**: Accepts the same input format as the Power Automate trigger

### Request Format
```json
{
  "domain": "goldenergy.pt",
  "from": "customer@example.com",
  "to": ["support@goldenergy.pt"],
  "cc": [],
  "subject": "Email subject",
  "body": "Email body content",
  "bodyFormat": "html",
  "attachments": [
    {
      "id": "attachment-id",
      "name": "document.pdf",
      "contentType": "application/pdf",
      "size": 1024,
      "contentBytes": "base64-encoded-content"
    }
  ],
  "originalMailbox": "support@goldenergy.pt",
  "emailId": "unique-email-id"
}
```

### Response Format
```json
{
  "subjectPrefix": "RE:",
  "body": "<p>Generated email response in HTML format</p>",
  "confidence": 85,
  "language": "pt-PT"
}
```

### Configuration

#### Required Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key

#### Optional Environment Variables
- `DEFAULT_AI_MODEL`: AI model to use (default: `gpt-4o-mini`)
- `REASONING_LEVEL`: Reasoning effort level (low/medium/high)
- `OUTPUT_FORMAT`: Output format (json/text)
- `GET_ATTACHMENT_API_URL`: URL for attachment retrieval service

#### Teams Integration (Optional)
- `AZURE_TENANT_ID`: Azure tenant ID
- `AZURE_CLIENT_ID`: Azure client ID  
- `AZURE_CLIENT_SECRET`: Azure client secret
- `TEAMS_TEAM_ID`: Teams team ID for notifications
- `TEAMS_CHANNEL_ID`: Teams channel ID for notifications

### Function Handlers

#### `content_not_available`
Triggered when the AI lacks information to answer a question.
- Sends notification to Teams channel
- Records the missing information for knowledge base updates
- Returns success response with explanation

#### `analyze_email_attachment`
Triggered when email contains attachments that need analysis.
- Downloads attachment content
- Uploads file to OpenAI
- Analyzes document using AI
- Returns analysis results

### Error Handling
- Automatic retry with exponential backoff (5 attempts)
- Teams notifications for errors
- Detailed error messages in responses
- Graceful degradation when services are unavailable

### Testing

#### Setup and Test Script
```bash
# Run setup script
python setup_email_ai.py

# Run comprehensive tests
python test_email_ai.py
```

#### Manual Testing
```bash
# Start the server
python -m uvicorn src.main:app --reload --port 8000

# Test endpoint
curl -X POST "http://localhost:8000/api/v1/email/compose" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "goldenergy.pt",
    "from": "test@example.com",
    "to": ["support@goldenergy.pt"],
    "subject": "Test email",
    "body": "This is a test email",
    "bodyFormat": "text"
  }'
```

### PowerShell Setup
```powershell
# Run the setup script
.\setup.ps1
```

### API Documentation
Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

---

## Migration from Power Automate

This implementation provides a direct replacement for the Power Automate SmartEmails flow:

### Equivalent Components
| Power Automate | FastAPI Implementation |
|----------------|----------------------|
| HTTP Trigger | `/api/v1/email/compose` endpoint |
| OpenAI HTTP Action | `OpenAIService.call_openai_responses()` |
| Function Switch | `EmailAIProcessor.process_function_call()` |
| Teams Connector | `TeamsService.send_alert()` |
| Until Loop | `for iteration in range(10)` loop |
| Variables | Python variables and state management |

### Benefits of API Implementation
- **Performance**: Direct API calls vs. Power Automate overhead
- **Debugging**: Better error tracking and logging
- **Flexibility**: Easy to modify and extend functionality
- **Cost**: Potentially lower operational costs
- **Integration**: Can be called from any system that supports HTTP

### Deployment Options
- **Local Development**: Run with uvicorn
- **Docker**: Containerize for consistent deployment
- **Azure App Service**: Deploy to Azure for scalability
- **Azure Container Apps**: Serverless container deployment
