#!/usr/bin/env python3
"""
Test script để kiểm tra AI có thể học từ dataset không
"""

import requests
import json
import time
from typing import Dict, List


class DatasetLearningTester:
    """Test class để kiểm tra khả năng học của AI từ dataset"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id = f"test_session_{int(time.time())}"
    
    def test_chat_endpoint(self, question: str) -> Dict:
        """Test chat endpoint với câu hỏi"""
        url = f"{self.base_url}/chat"
        payload = {
            "message": question,
            "user_id": "test_user",
            "session_id": self.session_id,
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def test_es_search(self, query: str) -> Dict:
        """Test Elasticsearch search endpoint"""
        url = f"{self.base_url}/es/search-simple"
        params = {
            "q": query,
            "top_n": 5,
            "save": False
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def test_knowledge_base_search(self, query: str) -> Dict:
        """Test knowledge base search"""
        url = f"{self.base_url}/es/comprehensive-search"
        payload = {
            "query": query,
            "top_n_per_category": 3,
            "categories": None,  # Search all categories
            "save_to_postgres": False,
            "created_by": "test_user"
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def run_dataset_tests(self) -> Dict:
        """Chạy tất cả tests cho dataset learning"""
        print("🧪 Testing Dataset Learning Capabilities")
        print("=" * 50)
        
        # Test questions dựa trên nội dung dataset
        test_questions = [
            "What is data structure?",
            "Explain sorting algorithms",
            "What are trees in computer science?",
            "How does hashing work?",
            "What is recursion?",
            "Explain database design",
            "What is CSI106 about?",
            "How do graphs work in algorithms?",
            "What are stacks and queues?",
            "Explain complexity analysis"
        ]
        
        results = {
            "chat_tests": [],
            "es_search_tests": [],
            "kb_search_tests": [],
            "summary": {}
        }
        
        # Test 1: Chat endpoint
        print("\n📝 Testing Chat Endpoint...")
        for i, question in enumerate(test_questions[:3], 1):  # Test first 3 questions
            print(f"   Test {i}: {question}")
            result = self.test_chat_endpoint(question)
            results["chat_tests"].append({
                "question": question,
                "result": result
            })
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
            else:
                print(f"      ✅ Response length: {len(result.get('answer', ''))} chars")
            time.sleep(1)  # Avoid rate limiting
        
        # Test 2: ES Search
        print("\n🔍 Testing Elasticsearch Search...")
        for i, query in enumerate(["data structure", "sorting", "database"], 1):
            print(f"   Test {i}: Searching for '{query}'")
            result = self.test_es_search(query)
            results["es_search_tests"].append({
                "query": query,
                "result": result
            })
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
            else:
                total_results = result.get("total_results", 0)
                print(f"      ✅ Found {total_results} results")
            time.sleep(1)
        
        # Test 3: Knowledge Base Search
        print("\n📚 Testing Knowledge Base Search...")
        for i, query in enumerate(["CSI106", "algorithms", "trees"], 1):
            print(f"   Test {i}: KB search for '{query}'")
            result = self.test_knowledge_base_search(query)
            results["kb_search_tests"].append({
                "query": query,
                "result": result
            })
            
            if "error" in result:
                print(f"      ❌ Error: {result['error']}")
            else:
                categories_found = result.get("categories_found", [])
                sft_pairs = len(result.get("sft_pairs", []))
                print(f"      ✅ Found {len(categories_found)} categories, {sft_pairs} SFT pairs")
            time.sleep(1)
        
        # Generate summary
        results["summary"] = self._generate_summary(results)
        return results
    
    def _generate_summary(self, results: Dict) -> Dict:
        """Generate test summary"""
        summary = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "features_working": [],
            "features_failing": []
        }
        
        # Count chat tests
        for test in results["chat_tests"]:
            summary["total_tests"] += 1
            if "error" not in test["result"]:
                summary["passed_tests"] += 1
                summary["features_working"].append("chat_endpoint")
            else:
                summary["failed_tests"] += 1
                summary["features_failing"].append("chat_endpoint")
        
        # Count ES search tests
        for test in results["es_search_tests"]:
            summary["total_tests"] += 1
            if "error" not in test["result"]:
                summary["passed_tests"] += 1
                if "elasticsearch_search" not in summary["features_working"]:
                    summary["features_working"].append("elasticsearch_search")
            else:
                summary["failed_tests"] += 1
                if "elasticsearch_search" not in summary["features_failing"]:
                    summary["features_failing"].append("elasticsearch_search")
        
        # Count KB search tests
        for test in results["kb_search_tests"]:
            summary["total_tests"] += 1
            if "error" not in test["result"]:
                summary["passed_tests"] += 1
                if "knowledge_base_search" not in summary["features_working"]:
                    summary["features_working"].append("knowledge_base_search")
            else:
                summary["failed_tests"] += 1
                if "knowledge_base_search" not in summary["features_failing"]:
                    summary["features_failing"].append("knowledge_base_search")
        
        return summary
    
    def print_detailed_results(self, results: Dict):
        """In kết quả chi tiết"""
        print("\n📊 DETAILED TEST RESULTS")
        print("=" * 50)
        
        summary = results["summary"]
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']} ✅")
        print(f"Failed: {summary['failed_tests']} ❌")
        
        if summary["features_working"]:
            print(f"\n✅ Working Features:")
            for feature in summary["features_working"]:
                print(f"   • {feature}")
        
        if summary["features_failing"]:
            print(f"\n❌ Failing Features:")
            for feature in summary["features_failing"]:
                print(f"   • {feature}")
        
        # Sample responses
        print(f"\n💬 Sample Chat Responses:")
        for i, test in enumerate(results["chat_tests"][:2], 1):
            if "error" not in test["result"]:
                answer = test["result"].get("answer", "")[:200]
                print(f"   Q{i}: {test['question']}")
                print(f"   A{i}: {answer}...")
                print()
        
        # ES Search results
        print(f"\n🔍 Sample ES Search Results:")
        for i, test in enumerate(results["es_search_tests"][:2], 1):
            if "error" not in test["result"]:
                total_results = test["result"].get("total_results", 0)
                print(f"   Query {i}: '{test['query']}' -> {total_results} results")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if summary["passed_tests"] == summary["total_tests"]:
            print("   🎉 All tests passed! Your AI is ready to learn from the dataset.")
            print("   📚 The AI can now answer questions about CSI106, DSA, Database, etc.")
        elif summary["passed_tests"] > 0:
            print("   ⚠️  Some features are working. Check failing components:")
            if "chat_endpoint" in summary["features_failing"]:
                print("   • Check if the API server is running")
            if "elasticsearch_search" in summary["features_failing"]:
                print("   • Check if Elasticsearch is running and indexed")
            if "knowledge_base_search" in summary["features_failing"]:
                print("   • Check database connection and knowledge base data")
        else:
            print("   ❌ No tests passed. Please check:")
            print("   • API server is running (python scripts/run_api.ps1)")
            print("   • Database is set up correctly")
            print("   • Elasticsearch is running")
            print("   • Dataset was imported successfully")


def main():
    """Main test function"""
    print("🚀 Dataset Learning Test Suite")
    print("=" * 50)
    
    # Check if API server is running
    try:
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print("✅ API server is running")
    except:
        print("❌ API server is not running!")
        print("Please start it with: python scripts/run_api.ps1")
        return
    
    # Run tests
    tester = DatasetLearningTester()
    results = tester.run_dataset_tests()
    
    # Print results
    tester.print_detailed_results(results)
    
    # Save results to file
    with open("test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: test_results.json")


if __name__ == "__main__":
    main()
