# 📚 SmartEmails API Reference

## Overview

The SmartEmails API provides intelligent email response generation using OpenAI's latest Responses API. This comprehensive reference covers all endpoints, request/response formats, error handling, and integration examples.

## Base Information

- **Base URL**: `https://smartemails-api.azurewebsites.net`
- **Version**: 1.0.0
- **Protocol**: HTTPS
- **Content Type**: `application/json`

## Authentication

Currently, no authentication is required. Future versions may implement API key authentication.

## Rate Limiting

- **Limit**: 100 requests per minute
- **Burst**: 10 requests per second
- **Headers**: Rate limit information is included in response headers

## Endpoints

### Health Check

Get the current health status of the API service.

#### Request

```http
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "api_key_configured": true,
  "default_model": "gpt-4o-mini",
  "teams_configured": true,
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime": "2h 45m",
  "dependencies": {
    "openai": {
      "status": "available",
      "responseTime": 250
    },
    "teams": {
      "status": "available", 
      "responseTime": 180
    }
  }
}
```

#### Status Codes

- `200 OK`: Service is healthy
- `500 Internal Server Error`: Service is unhealthy

### Compose Email Response

Generate an intelligent email response using AI.

#### Request

```http
POST /api/v1/email/compose
```

#### Request Body

```json
{
  "domain": "goldenergy.pt",
  "from": "customer@example.com",
  "to": ["support@goldenergy.pt"],
  "cc": ["manager@goldenergy.pt"],
  "subject": "Pedido de informação sobre tarifas",
  "body": "Gostaria de receber informações sobre as vossas tarifas de energia elétrica.",
  "bodyFormat": "text",
  "attachments": [
    {
      "id": "att-001",
      "name": "document.pdf",
      "contentType": "application/pdf",
      "size": 524288,
      "contentBytes": "JVBERi0xLjQKJcOkw7zDtsO4..."
    }
  ],
  "originalMailbox": "support@goldenergy.pt",
  "emailId": "email-123"
}
```

#### Response

```json
{
  "subjectPrefix": "RE:",
  "body": "<p>Estimado Cliente,</p><p>Obrigado pelo seu contacto...</p>",
  "confidence": 88,
  "language": "pt-PT",
  "attachmentsAnalyzed": ["att-001"],
  "functionsUsed": ["analyze_email_attachment"],
  "processingTime": 3.2,
  "aiModel": "gpt-4o-mini",
  "reasoning": "The customer is requesting information about energy tariffs..."
}
```

#### Status Codes

- `200 OK`: Email response generated successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## Request/Response Schemas

### EmailComposeRequest

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | ✅ | Email domain (e.g., "goldenergy.pt") |
| `from` | string | ✅ | Sender's email address |
| `to` | array[string] | ✅ | Recipient email addresses |
| `cc` | array[string] | ❌ | CC recipient addresses |
| `subject` | string | ✅ | Email subject line |
| `body` | string | ✅ | Email body content |
| `bodyFormat` | string | ✅ | Body format ("text" or "html") |
| `attachments` | array[object] | ❌ | Email attachments |
| `originalMailbox` | string | ❌ | Original mailbox |
| `emailId` | string | ❌ | Unique email identifier |

### EmailAttachment

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | ✅ | Unique attachment identifier |
| `name` | string | ✅ | Attachment filename |
| `contentType` | string | ✅ | MIME type |
| `size` | integer | ✅ | File size in bytes |
| `contentBytes` | string | ❌ | Base64 encoded content |

### EmailComposeResponse

| Field | Type | Description |
|-------|------|-------------|
| `subjectPrefix` | string | Prefix for reply subject |
| `body` | string | Generated response in HTML |
| `confidence` | integer | Confidence score (0-100) |
| `language` | string | Response language code |
| `attachmentsAnalyzed` | array[string] | Analyzed attachment IDs |
| `functionsUsed` | array[string] | AI functions called |
| `processingTime` | number | Processing time in seconds |
| `aiModel` | string | AI model used |
| `reasoning` | string | AI reasoning (if enabled) |

## Error Handling

### Error Response Format

```json
{
  "error": "Validation Error",
  "message": "Invalid email format in 'from' field",
  "details": {
    "field": "from",
    "value": "invalid-email",
    "issue": "Must be a valid email address"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "requestId": "req-123"
}
```

### Common Error Codes

#### 400 Bad Request

```json
{
  "error": "Validation Error",
  "message": "Missing required field: 'subject'",
  "details": {
    "field": "subject",
    "issue": "This field is required"
  }
}
```

#### 401 Unauthorized

```json
{
  "error": "Authentication Error",
  "message": "OpenAI API key not configured",
  "details": {
    "solution": "Set OPENAI_API_KEY environment variable"
  }
}
```

#### 429 Rate Limited

```json
{
  "error": "Rate Limit Exceeded",
  "message": "Too many requests. Please try again later.",
  "details": {
    "retryAfter": 60,
    "limit": "100 requests per minute"
  }
}
```

#### 500 Internal Server Error

```json
{
  "error": "Internal Server Error",
  "message": "An unexpected error occurred",
  "details": {
    "support": "Contact support@goldenergy.pt"
  }
}
```

## Function Calling

The API supports AI function calling for advanced processing:

### content_not_available

Called when the AI lacks information to provide a complete response.

**Behavior**:
- Sends notification to Teams channel
- Records missing information for knowledge base
- Returns appropriate response indicating follow-up needed

### analyze_email_attachment

Called when email attachments need analysis.

**Behavior**:
- Downloads attachment content
- Uploads file to OpenAI for analysis
- Extracts relevant information
- Incorporates analysis into response

## Integration Examples

### cURL

```bash
curl -X POST "https://smartemails-api.azurewebsites.net/api/v1/email/compose" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "goldenergy.pt",
    "from": "customer@example.com",
    "to": ["support@goldenergy.pt"],
    "subject": "Test email",
    "body": "This is a test email",
    "bodyFormat": "text"
  }'
```

### Python

```python
import requests

def send_email_for_processing(email_data):
    """Send email to SmartEmails API for processing"""
    url = "https://smartemails-api.azurewebsites.net/api/v1/email/compose"
    
    try:
        response = requests.post(url, json=email_data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error calling API: {e}")
        return None

# Example usage
email_data = {
    "domain": "goldenergy.pt",
    "from": "customer@example.com",
    "to": ["support@goldenergy.pt"],
    "subject": "Billing inquiry",
    "body": "I have a question about my bill",
    "bodyFormat": "text"
}

result = send_email_for_processing(email_data)
if result:
    print(f"Response: {result['body']}")
    print(f"Confidence: {result['confidence']}%")
```

### JavaScript

```javascript
async function processEmail(emailData) {
    const url = 'https://smartemails-api.azurewebsites.net/api/v1/email/compose';
    
    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(emailData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error processing email:', error);
        return null;
    }
}

// Example usage
const emailData = {
    domain: "goldenergy.pt",
    from: "customer@example.com",
    to: ["support@goldenergy.pt"],
    subject: "Service inquiry",
    body: "I need help with my account",
    bodyFormat: "text"
};

processEmail(emailData).then(result => {
    if (result) {
        console.log('Generated response:', result.body);
        console.log('Confidence:', result.confidence + '%');
    }
});
```

### Power Automate

```json
{
  "method": "POST",
  "uri": "https://smartemails-api.azurewebsites.net/api/v1/email/compose",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "domain": "@{triggerBody()?['domain']}",
    "from": "@{triggerBody()?['from']}",
    "to": "@{triggerBody()?['to']}",
    "cc": "@{triggerBody()?['cc']}",
    "subject": "@{triggerBody()?['subject']}",
    "body": "@{triggerBody()?['body']}",
    "bodyFormat": "@{triggerBody()?['bodyFormat']}",
    "attachments": "@{triggerBody()?['attachments']}",
    "originalMailbox": "@{triggerBody()?['originalMailbox']}",
    "emailId": "@{triggerBody()?['emailId']}"
  }
}
```

## Best Practices

### Request Optimization

1. **Validate Input**: Always validate email data before sending
2. **Handle Large Attachments**: Split large attachments or use streaming
3. **Use Appropriate Timeouts**: Set reasonable timeout values (30-60 seconds)
4. **Implement Retry Logic**: Use exponential backoff for transient errors

### Error Handling

```python
import time
import random

def call_api_with_retry(email_data, max_retries=3):
    """Call API with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                "https://smartemails-api.azurewebsites.net/api/v1/email/compose",
                json=email_data,
                timeout=30
            )
            
            if response.status_code == 429:
                # Rate limited, wait and retry
                delay = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                continue
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            
            # Wait before retry
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
    
    return None
```

### Performance Optimization

1. **Connection Pooling**: Use connection pools for multiple requests
2. **Async Processing**: Use async HTTP clients for concurrent requests
3. **Caching**: Cache responses for similar requests
4. **Monitoring**: Monitor response times and error rates

## SDK Examples

### Python SDK

```python
class SmartEmailsClient:
    def __init__(self, base_url="https://smartemails-api.azurewebsites.net"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def compose_email(self, email_data):
        """Compose email response"""
        url = f"{self.base_url}/api/v1/email/compose"
        response = self.session.post(url, json=email_data)
        response.raise_for_status()
        return response.json()
    
    def health_check(self):
        """Check API health"""
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

# Usage
client = SmartEmailsClient()
result = client.compose_email({
    "domain": "goldenergy.pt",
    "from": "customer@example.com",
    "to": ["support@goldenergy.pt"],
    "subject": "Test",
    "body": "Test message",
    "bodyFormat": "text"
})
```

## Testing

### Unit Tests

```python
import unittest
from unittest.mock import patch, Mock

class TestSmartEmailsAPI(unittest.TestCase):
    
    @patch('requests.post')
    def test_compose_email_success(self, mock_post):
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "subjectPrefix": "RE:",
            "body": "<p>Test response</p>",
            "confidence": 90,
            "language": "pt-PT"
        }
        mock_post.return_value = mock_response
        
        # Test request
        email_data = {
            "domain": "goldenergy.pt",
            "from": "test@example.com",
            "to": ["support@goldenergy.pt"],
            "subject": "Test",
            "body": "Test message",
            "bodyFormat": "text"
        }
        
        result = compose_email(email_data)
        
        # Assertions
        self.assertEqual(result['confidence'], 90)
        self.assertEqual(result['language'], 'pt-PT')
        mock_post.assert_called_once()
```

### Integration Tests

```python
def test_end_to_end_flow():
    """Test complete email processing flow"""
    # Health check
    health = requests.get("https://smartemails-api.azurewebsites.net/health")
    assert health.status_code == 200
    
    # Compose email
    email_data = {
        "domain": "goldenergy.pt",
        "from": "integration.test@example.com",
        "to": ["support@goldenergy.pt"],
        "subject": "Integration Test",
        "body": "This is an integration test",
        "bodyFormat": "text"
    }
    
    response = requests.post(
        "https://smartemails-api.azurewebsites.net/api/v1/email/compose",
        json=email_data
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result['confidence'] > 0
    assert result['language'] in ['pt-PT', 'en-US']
```

## Monitoring and Observability

### Health Monitoring

```python
def monitor_api_health():
    """Monitor API health continuously"""
    while True:
        try:
            response = requests.get(
                "https://smartemails-api.azurewebsites.net/health",
                timeout=10
            )
            
            if response.status_code == 200:
                health_data = response.json()
                if health_data['status'] == 'healthy':
                    print(f"✅ API healthy - Uptime: {health_data['uptime']}")
                else:
                    print(f"⚠️ API unhealthy: {health_data['issues']}")
            else:
                print(f"❌ Health check failed: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
        
        time.sleep(60)  # Check every minute
```

### Performance Metrics

```python
def measure_api_performance():
    """Measure API response times"""
    times = []
    
    for i in range(10):
        start_time = time.time()
        
        try:
            response = requests.post(
                "https://smartemails-api.azurewebsites.net/api/v1/email/compose",
                json={
                    "domain": "goldenergy.pt",
                    "from": "perf.test@example.com",
                    "to": ["support@goldenergy.pt"],
                    "subject": f"Performance Test {i+1}",
                    "body": "Performance testing message",
                    "bodyFormat": "text"
                }
            )
            
            if response.status_code == 200:
                end_time = time.time()
                times.append(end_time - start_time)
                
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"Average response time: {avg_time:.2f}s")
        print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")
```

---

For more information, visit the [GitHub repository](https://github.com/AndreJacomeSilva/SmartEmails) or contact support@goldenergy.pt.
