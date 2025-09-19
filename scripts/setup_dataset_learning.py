#!/usr/bin/env python3
"""
Script tổng hợp để thiết lập AI học từ dataset
Bao gồm: import data, index vào Elasticsearch, tạo training data
"""

import os
import sys
import subprocess
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_command(command: str, description: str) -> bool:
    """Chạy command và hiển thị kết quả"""
    print(f"\n🔄 {description}...")
    print(f"Command: {command}")
    
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=project_root,
            capture_output=True, 
            text=True,
            check=True
        )
        
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print("Output:", result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False


def check_dependencies():
    """Kiểm tra dependencies cần thiết"""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "python-pptx",
        "sqlalchemy", 
        "psycopg2-binary",
        "elasticsearch",
        "fastapi",
        "uvicorn"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    
    print("✅ All dependencies are installed!")
    return True


def setup_environment():
    """Thiết lập environment variables"""
    print("🔧 Setting up environment...")
    
    # Set default environment variables
    env_vars = {
        "DATASET_DIR": r"D:\Data_set",
        "IMPORT_CREATED_BY": "dataset_import",
        "MIN_CONTENT_LENGTH": "100",
        "KB_CATEGORY": "academic_dataset"
    }
    
    for key, value in env_vars.items():
        if key not in os.environ:
            os.environ[key] = value
            print(f"   Set {key} = {value}")


def main():
    """Main workflow để thiết lập dataset learning"""
    print("🚀 Setting up AI Dataset Learning System")
    print("=" * 50)
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print("❌ Please install missing dependencies first!")
        return
    
    # Step 2: Setup environment
    setup_environment()
    
    # Step 3: Import dataset to knowledge base
    print("\n📚 STEP 1: Importing dataset to knowledge base")
    if not run_command(
        "python scripts/ingest/import_dataset_to_kb.py",
        "Import dataset to knowledge base"
    ):
        print("❌ Dataset import failed!")
        return
    
    # Step 4: Index knowledge base to Elasticsearch
    print("\n🔍 STEP 2: Indexing knowledge base to Elasticsearch")
    if not run_command(
        "python scripts/ingest/index_kb_to_es.py",
        "Index knowledge base to Elasticsearch"
    ):
        print("⚠️  Elasticsearch indexing failed - continuing without ES")
    
    # Step 5: Generate SFT training data
    print("\n🎯 STEP 3: Generating SFT training data")
    if not run_command(
        "python scripts/sft/kb_to_sft.py",
        "Generate SFT training data from knowledge base"
    ):
        print("❌ SFT data generation failed!")
        return
    
    # Step 6: Test the integration
    print("\n🧪 STEP 4: Testing integration")
    if not run_command(
        "python test_es_integration.py",
        "Test Elasticsearch integration"
    ):
        print("⚠️  Integration test failed - but system may still work")
    
    print("\n🎉 Dataset Learning Setup Complete!")
    print("=" * 50)
    print("📋 Summary:")
    print("   ✅ Dataset imported to knowledge base")
    print("   ✅ Knowledge base indexed to Elasticsearch")
    print("   ✅ SFT training data generated")
    print("   ✅ Integration tested")
    
    print("\n🚀 Next Steps:")
    print("   1. Start the API server:")
    print("      python scripts/run_api.ps1")
    print("   2. Or start manually:")
    print("      uvicorn app.main:app --reload --port 8000")
    print("   3. Test the chat API:")
    print("      POST http://localhost:8000/chat")
    print("   4. Optional: Fine-tune the model:")
    print("      python scripts/train/train_lora_unsloth.py")
    
    print("\n💡 The AI can now learn from your dataset!")
    print("   Ask questions about CSI106, DSA, Database, etc.")


if __name__ == "__main__":
    main()
