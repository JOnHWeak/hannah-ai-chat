#!/usr/bin/env python3
"""
Test script for the new Elasticsearch integration features.

This script demonstrates:
1. Searching ES with deduplication
2. Applying content guardrails
3. Auto-saving to PostgreSQL
4. Generating SFT-ready pairs
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TEST_QUERIES = [
    "clean code",
    "database design", 
    "python programming",
    "*"  # Search all
]

def test_es_categories():
    """Test getting available categories."""
    print("🔍 Testing ES Categories Endpoint...")
    
    try:
        response = requests.get(f"{BASE_URL}/es/categories")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['count']} categories: {data['categories']}")
            return data['categories']
        else:
            print(f"❌ Failed to get categories: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error getting categories: {e}")
        return []

def test_simple_search(query="clean code", save_to_postgres=False):
    """Test simple search endpoint."""
    print(f"\n🔍 Testing Simple Search: '{query}'...")
    
    try:
        params = {
            "q": query,
            "top_n": 5,
            "save": save_to_postgres
        }
        
        response = requests.get(f"{BASE_URL}/es/search-simple", params=params)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Found {data['total_results']} results across {len(data['categories_found'])} categories")
            print(f"   Categories: {data['categories_found']}")
            print(f"   Rejected by guardrails: {data['rejected_by_guardrails']}")
            if save_to_postgres:
                print(f"   Saved to PostgreSQL: {data['saved_to_postgres']}")
            return data
        else:
            print(f"❌ Search failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in simple search: {e}")
        return None

def test_comprehensive_search(query="python", categories=None, save_to_postgres=True):
    """Test comprehensive search with all features."""
    print(f"\n🚀 Testing Comprehensive Search: '{query}'...")
    
    try:
        payload = {
            "query": query,
            "top_n_per_category": 3,
            "categories": categories,
            "save_to_postgres": save_to_postgres,
            "created_by": "test_user"
        }
        
        response = requests.post(f"{BASE_URL}/es/comprehensive-search", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get("summary", {})
            metrics = summary.get("performance_metrics", {})
            
            print(f"✅ Comprehensive search completed!")
            print(f"   Features applied: {summary.get('features_applied', [])}")
            print(f"   Total found: {metrics.get('total_found', 0)}")
            print(f"   Quality filtered: {metrics.get('quality_filtered', 0)}")
            print(f"   Saved to DB: {metrics.get('saved_to_db', 0)}")
            print(f"   SFT pairs generated: {metrics.get('sft_pairs_generated', 0)}")
            print(f"   Categories processed: {metrics.get('categories_processed', 0)}")
            
            # Show sample SFT pair
            sft_pairs = data.get("sft_pairs", [])
            if sft_pairs:
                print(f"\n📝 Sample SFT pair:")
                sample = sft_pairs[0]
                print(f"   User: {sample['messages'][0]['content'][:100]}...")
                print(f"   Assistant: {sample['messages'][1]['content'][:100]}...")
                print(f"   Weight: {sample['weight']}")
                print(f"   Category: {sample['metadata']['category']}")
            
            return data
        else:
            print(f"❌ Comprehensive search failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in comprehensive search: {e}")
        return None

def test_sft_export(query="database", categories=None):
    """Test SFT export functionality."""
    print(f"\n📤 Testing SFT Export: '{query}'...")
    
    try:
        payload = {
            "query": query,
            "categories": categories,
            "top_n_per_category": 5,
            "include_metadata": True
        }
        
        response = requests.post(f"{BASE_URL}/es/export-sft", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ SFT export completed!")
            print(f"   Total pairs: {data['total_pairs']}")
            print(f"   Categories: {data['categories_found']}")
            
            # Save to file for inspection
            output_file = "test_sft_export.jsonl"
            with open(output_file, "w", encoding="utf-8") as f:
                for pair in data["sft_pairs"]:
                    f.write(json.dumps(pair, ensure_ascii=False) + "\n")
            
            print(f"   Saved to: {output_file}")
            return data
        else:
            print(f"❌ SFT export failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error in SFT export: {e}")
        return None

def main():
    """Run all tests."""
    print("🧪 Testing Elasticsearch Integration Features")
    print("=" * 50)
    
    # Test 1: Get available categories
    categories = test_es_categories()
    
    # Test 2: Simple search without saving
    test_simple_search("clean code", save_to_postgres=False)
    
    # Test 3: Simple search with saving
    test_simple_search("python", save_to_postgres=True)
    
    # Test 4: Comprehensive search with specific categories
    if categories:
        test_categories = categories[:2] if len(categories) > 2 else categories
        test_comprehensive_search("programming", categories=test_categories)
    
    # Test 5: Comprehensive search all categories
    test_comprehensive_search("software engineering", categories=None)
    
    # Test 6: SFT export
    test_sft_export("database design")
    
    print("\n✨ All tests completed!")
    print("\nTo run the API server:")
    print("  uvicorn app.main:app --reload --port 8000")
    print("\nTo view API docs:")
    print("  http://localhost:8000/docs")

if __name__ == "__main__":
    main()
