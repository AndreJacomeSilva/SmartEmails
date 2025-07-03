#!/usr/bin/env python3
"""
Setup script for SmartGold-SmartCompose Email AI API
This script helps configure and test the new email AI endpoint
"""

import os
import sys
import json
import asyncio
import httpx
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'openai',
        'httpx',
        'tenacity',
        'msgraph-sdk',
        'azure-identity',
        'python-multipart'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_environment_variables():
    """Check if required environment variables are configured"""
    env_file = Path(__file__).parent / ".env"
    
    if not env_file.exists():
        print("❌ .env file not found")
        return False
    
    required_vars = [
        'OPENAI_API_KEY'
    ]
    
    optional_vars = [
        'DEFAULT_AI_MODEL',
        'REASONING_LEVEL',
        'OUTPUT_FORMAT',
        'AZURE_TENANT_ID',
        'AZURE_CLIENT_ID', 
        'AZURE_CLIENT_SECRET',
        'TEAMS_TEAM_ID',
        'TEAMS_CHANNEL_ID',
        'GET_ATTACHMENT_API_URL'
    ]
    
    print("📋 Environment Configuration Check:")
    
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == f"your_{var.lower()}_here":
            missing_required.append(var)
            print(f"  ❌ {var}: Not configured")
        else:
            print(f"  ✅ {var}: Configured")
    
    for var in optional_vars:
        value = os.getenv(var)
        if not value or value.startswith("your_"):
            print(f"  ⚠️  {var}: Not configured (optional)")
        else:
            print(f"  ✅ {var}: Configured")
    
    if missing_required:
        print(f"\n❌ Missing required environment variables: {', '.join(missing_required)}")
        return False
    
    return True

def create_sample_request():
    """Create a sample request for testing"""
    return {
        "domain": "goldenergy.pt",
        "from": "customer@example.com",
        "to": ["support@goldenergy.pt"],
        "cc": [],
        "subject": "Pedido de informação sobre fatura",
        "body": "Bom dia,\n\nGostaria de receber informações sobre a minha última fatura.\n\nObrigado,\nJoão Silva",
        "bodyFormat": "text",
        "attachments": [],
        "originalMailbox": "support@goldenergy.pt",
        "emailId": "test-email-123"
    }

async def test_endpoint():
    """Test the new email AI endpoint"""
    print("🧪 Testing Email AI Endpoint...")
    
    sample_request = create_sample_request()
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/api/v1/email/compose",
                json=sample_request,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Endpoint test successful!")
                print(f"  - Subject Prefix: {result.get('subjectPrefix', '')}")
                print(f"  - Confidence: {result.get('confidence', 'N/A')}")
                print(f"  - Language: {result.get('language', 'N/A')}")
                print(f"  - Body Preview: {result.get('body', '')[:100]}...")
                return True
            else:
                print(f"❌ Endpoint test failed with status {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
    except httpx.ConnectError:
        print("❌ Could not connect to server. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Endpoint test failed: {str(e)}")
        return False

def print_usage_examples():
    """Print usage examples"""
    print("\n📚 Usage Examples:")
    print("\n1. Start the server:")
    print("   python -m uvicorn src.main:app --reload --port 8000")
    
    print("\n2. Test with curl:")
    sample_request = create_sample_request()
    curl_data = json.dumps(sample_request, indent=2)
    print(f"""   curl -X POST "http://localhost:8000/api/v1/email/compose" \\
     -H "Content-Type: application/json" \\
     -d '{curl_data}'""")
    
    print("\n3. API Documentation:")
    print("   http://localhost:8000/docs")
    
    print("\n4. Health Check:")
    print("   http://localhost:8000/health")

def main():
    """Main setup and test function"""
    print("🚀 SmartGold-SmartCompose Email AI Setup")
    print("=" * 50)
    
    # Load environment variables
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    env_ok = check_environment_variables()
    
    if not env_ok:
        print("\n⚠️  Some environment variables are not configured.")
        print("The API will still work but some features may be limited.")
    
    # Print usage examples
    print_usage_examples()
    
    # Ask if user wants to test
    if env_ok:
        print("\n" + "=" * 50)
        test_now = input("Would you like to test the endpoint now? (y/N): ").lower().strip()
        
        if test_now == 'y':
            print("\nMake sure the server is running first:")
            print("python -m uvicorn src.main:app --reload --port 8000")
            input("\nPress Enter when the server is ready...")
            
            # Run the test
            asyncio.run(test_endpoint())
    
    print("\n✅ Setup complete!")

if __name__ == "__main__":
    main()
