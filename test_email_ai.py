#!/usr/bin/env python3
"""
Test script for the SmartGold-SmartCompose Email AI API
Tests the new endpoint that replicates Power Automate flow functionality
"""

import asyncio
import json
import httpx
from typing import Dict, Any

# Test cases matching different scenarios from Power Automate flow
TEST_CASES = [
    {
        "name": "Simple Information Request",
        "description": "Basic customer inquiry about services",
        "request": {
            "domain": "goldenergy.pt",
            "from": "joao.silva@example.com",
            "to": ["apoio@goldenergy.pt"],
            "cc": [],
            "subject": "Informações sobre tarifas de energia",
            "body": "Bom dia,\n\nGostaria de receber informações sobre as vossas tarifas de energia elétrica para casa.\n\nObrigado,\nJoão Silva",
            "bodyFormat": "text",
            "attachments": [],
            "originalMailbox": "apoio@goldenergy.pt",
            "emailId": "test-001"
        }
    },
    {
        "name": "Billing Question",
        "description": "Customer asking about their bill",
        "request": {
            "domain": "goldenergy.pt", 
            "from": "maria.santos@example.com",
            "to": ["faturacao@goldenergy.pt"],
            "cc": [],
            "subject": "RE: Dúvida sobre fatura mensal",
            "body": "Olá,\n\nTenho uma dúvida sobre a minha fatura do mês passado. O valor parece estar mais alto que o habitual.\n\nPode ajudar-me a perceber porquê?\n\nCumprimentos,\nMaria Santos\nNº Cliente: 123456789",
            "bodyFormat": "text",
            "attachments": [],
            "originalMailbox": "faturacao@goldenergy.pt",
            "emailId": "test-002"
        }
    },
    {
        "name": "Technical Question",
        "description": "Question about a specific technical term",
        "request": {
            "domain": "goldenergy.pt",
            "from": "pedro.costa@example.com", 
            "to": ["info@goldenergy.pt"],
            "cc": [],
            "subject": "O que é o MVEG?",
            "body": "Bom dia,\n\nVi na minha fatura uma referência ao MVEG mas não sei o que significa.\n\nPodem explicar-me?\n\nObrigado,\nPedro Costa",
            "bodyFormat": "text",
            "attachments": [],
            "originalMailbox": "info@goldenergy.pt",
            "emailId": "test-003"
        }
    },
    {
        "name": "Email with Attachment",
        "description": "Email with attachment that should trigger analyze_email_attachment",
        "request": {
            "domain": "goldenergy.pt",
            "from": "ana.ferreira@example.com",
            "to": ["contratos@goldenergy.pt"],
            "cc": [],
            "subject": "Análise do meu contrato",
            "body": "Bom dia,\n\nEnvio em anexo o meu contrato para análise. Podem verificar se está tudo correto?\n\nObrigada,\nAna Ferreira",
            "bodyFormat": "text",
            "attachments": [
                {
                    "id": "att-001",
                    "name": "contrato.pdf",
                    "contentType": "application/pdf",
                    "size": 1024,
                    "contentBytes": None
                }
            ],
            "originalMailbox": "contratos@goldenergy.pt",
            "emailId": "test-004"
        }
    }
]

class EmailAITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.endpoint = f"{base_url}/api/v1/email/compose"
        
    async def test_health_check(self) -> bool:
        """Test if the server is running"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/health")
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Server is healthy - API Key: {'✅' if result.get('api_key_configured') else '❌'}")
                    return True
                else:
                    print(f"❌ Health check failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {str(e)}")
            return False
    
    async def run_single_test(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single test case"""
        print(f"\n🧪 Testing: {test_case['name']}")
        print(f"   Description: {test_case['description']}")
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.endpoint,
                    json=test_case['request'],
                    headers={"Content-Type": "application/json"}
                )
                
                result = {
                    "test_name": test_case['name'],
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response_time": response.elapsed.total_seconds(),
                    "response_data": None,
                    "error": None
                }
                
                if response.status_code == 200:
                    data = response.json()
                    result["response_data"] = data
                    
                    print(f"   ✅ Success ({response.elapsed.total_seconds():.2f}s)")
                    print(f"   📧 Subject Prefix: '{data.get('subjectPrefix', '')}'")
                    print(f"   🎯 Confidence: {data.get('confidence', 'N/A')}")
                    print(f"   🌍 Language: {data.get('language', 'N/A')}")
                    
                    body = data.get('body', '')
                    if len(body) > 200:
                        print(f"   📝 Body: {body[:200]}...")
                    else:
                        print(f"   📝 Body: {body}")
                        
                else:
                    error_text = response.text
                    result["error"] = error_text
                    print(f"   ❌ Failed: {response.status_code}")
                    print(f"   Error: {error_text}")
                
                return result
                
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ Exception: {error_msg}")
            return {
                "test_name": test_case['name'],
                "status_code": None,
                "success": False,
                "response_time": None,
                "response_data": None,
                "error": error_msg
            }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test cases"""
        print("🚀 Starting Email AI API Tests")
        print("=" * 50)
        
        # First check if server is healthy
        if not await self.test_health_check():
            return {"error": "Server is not healthy", "results": []}
        
        results = []
        successful_tests = 0
        
        for test_case in TEST_CASES:
            result = await self.run_single_test(test_case)
            results.append(result)
            
            if result["success"]:
                successful_tests += 1
            
            # Small delay between tests
            await asyncio.sleep(1)
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print(f"   Total Tests: {len(TEST_CASES)}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {len(TEST_CASES) - successful_tests}")
        print(f"   Success Rate: {(successful_tests/len(TEST_CASES)*100):.1f}%")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for result in results:
            status = "✅" if result["success"] else "❌"
            time_info = f"({result['response_time']:.2f}s)" if result['response_time'] else ""
            print(f"   {status} {result['test_name']} {time_info}")
            
            if not result["success"] and result["error"]:
                print(f"      Error: {result['error'][:100]}...")
        
        return {
            "total_tests": len(TEST_CASES),
            "successful_tests": successful_tests,
            "success_rate": successful_tests/len(TEST_CASES)*100,
            "results": results
        }

def save_results_to_file(results: Dict[str, Any], filename: str = "test_results.json"):
    """Save test results to a JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\n💾 Results saved to {filename}")

async def main():
    """Main test runner"""
    tester = EmailAITester()
    
    print("🧪 SmartGold-SmartCompose Email AI API Tester")
    print("This script tests the new endpoint that replicates Power Automate flow")
    print()
    
    # Ask user for server URL
    server_url = input("Enter server URL (default: http://localhost:8000): ").strip()
    if server_url:
        tester = EmailAITester(server_url)
    
    # Run tests
    results = await tester.run_all_tests()
    
    # Save results
    if results.get("results"):
        save_results = input("\nSave results to file? (y/N): ").lower().strip()
        if save_results == 'y':
            save_results_to_file(results)
    
    print("\n✅ Testing complete!")

if __name__ == "__main__":
    asyncio.run(main())
