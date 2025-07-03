
# API Reference

## OpenAPI Specification

The SmartGold-SmartCompose Email AI API follows OpenAPI 3.0 standards. The complete specification is available at:
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **JSON Spec**: http://localhost:8000/openapi.json

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, authentication is handled through environment variables. For production deployments, consider implementing:
- API Key authentication
- OAuth 2.0
- Azure AD integration

## Endpoints

### Email Composition

#### Compose Email Response
```http
POST /api/v1/email/compose
```

Processes an email and generates an AI-powered response using OpenAI's Responses API.

**Headers:**
```
Content-Type: application/json
```

**Request Body Schema:**
```json
{
  "domain": {
    "type": "string",
    "description": "The domain of the organization",
    "example": "goldenergy.pt"
  },
  "from": {
    "type": "string",
    "format": "email",
    "description": "Sender's email address",
    "example": "customer@example.com"
  },
  "to": {
    "type": "array",
    "items": {
      "type": "string",
      "format": "email"
    },
    "description": "Recipient email addresses",
    "example": ["support@goldenergy.pt"]
  },
  "cc": {
    "type": "array",
    "items": {
      "type": "string",
      "format": "email"
    },
    "description": "CC email addresses",
    "default": []
  },
  "subject": {
    "type": "string",
    "description": "Email subject line",
    "example": "Pedido de informação"
  },
  "body": {
    "type": "string",
    "description": "Email body content",
    "example": "Gostaria de receber informações sobre as vossas tarifas."
  },
  "bodyFormat": {
    "type": "string",
    "enum": ["html", "text"],
    "default": "html",
    "description": "Format of the email body"
  },
  "attachments": {
    "type": "array",
    "items": {
      "$ref": "#/components/schemas/EmailAttachment"
    },
    "description": "Email attachments"
  },
  "originalMailbox": {
    "type": "string",
    "format": "email",
    "description": "Original mailbox receiving the email",
    "example": "support@goldenergy.pt"
  },
  "emailId": {
    "type": "string",
    "description": "Unique identifier for the email",
    "example": "msg_123456789"
  }
}
```

**Response Schema:**
```json
{
  "subjectPrefix": {
    "type": "string",
    "description": "Prefix to add to the original subject",
    "example": "RE:"
  },
  "body": {
    "type": "string",
    "description": "Generated email response body in HTML format",
    "example": "<p>Obrigado pelo seu contacto...</p>"
  },
  "confidence": {
    "type": "integer",
    "minimum": 0,
    "maximum": 100,
    "description": "Confidence level of the AI response",
    "example": 85
  },
  "language": {
    "type": "string",
    "description": "Language code of the response",
    "example": "pt-PT"
  }
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/email/compose" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "goldenergy.pt",
    "from": "joao.silva@example.com",
    "to": ["apoio@goldenergy.pt"],
    "subject": "Informações sobre tarifas",
    "body": "Gostaria de receber informações sobre as vossas tarifas de energia.",
    "bodyFormat": "text",
    "originalMailbox": "apoio@goldenergy.pt",
    "emailId": "msg_001"
  }'
```

**Example Response:**
```json
{
  "subjectPrefix": "RE:",
  "body": "<p>Estimado João Silva,</p><p>Obrigado pelo seu interesse nas nossas tarifas de energia...</p>",
  "confidence": 85,
  "language": "pt-PT"
}
```

**Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `422` - Validation Error
- `500` - Internal Server Error

### Legacy Endpoint (Deprecated)
  "body": "string",
  "isHtml": "boolean",
  "attachments": [
    {
      "name": "string",
      "contentType": "string",
      "sizeInKB": "integer",
      "isInline": "boolean",
      "url": "string",
      "lastModifiedDateTime": "string"
    }
  ],
  "knowledgeBaseVectorStore": "string",
  "functionsPath": "string",
  "apiUrl": "string",
  "replySenderName": "string",
  "persona": "string",
  "AiModel": "string",
  "ReasoningLevel": "string",
  "receivedDateTime": "string",
  "importance": "string"
}
```

### Response Body

The response body will be a JSON object with the following structure:

```json
{
  "subjectPrefix": "string",
  "body": "string",
  "confidence": "integer",
  "language": "string"
}
```
