#!/usr/bin/env python3
"""
Agent Monitoring Script - Theo dõi trạng thái Daily Training Agent
"""

import os
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import sys


class AgentMonitor:
    """Class để monitor Daily Training Agent"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.logs_dir = self.project_root / "logs"
        self.artifacts_dir = self.project_root / "artifacts"
        self.data_dir = self.project_root / "data"
        
        # Tạo logs directory nếu chưa có
        self.logs_dir.mkdir(exist_ok=True)
    
    def check_training_data(self) -> dict:
        """Kiểm tra dữ liệu training"""
        status = {
            "daily_data": {"exists": False, "count": 0, "latest": None},
            "kb_data": {"exists": False, "count": 0},
            "merged_data": {"exists": False, "count": 0}
        }
        
        # Check daily data
        daily_dir = self.data_dir / "daily"
        if daily_dir.exists():
            daily_files = list(daily_dir.glob("*.jsonl"))
            status["daily_data"]["exists"] = True
            status["daily_data"]["count"] = len(daily_files)
            
            if daily_files:
                latest_file = max(daily_files, key=os.path.getctime)
                status["daily_data"]["latest"] = latest_file.name
        
        # Check KB data
        kb_file = self.data_dir / "kb_es_sft.jsonl"
        if kb_file.exists():
            status["kb_data"]["exists"] = True
            with open(kb_file, 'r', encoding='utf-8') as f:
                status["kb_data"]["count"] = sum(1 for _ in f)
        
        # Check merged data
        merged_file = self.data_dir / "daily" / "latest.jsonl"
        if merged_file.exists():
            status["merged_data"]["exists"] = True
            with open(merged_file, 'r', encoding='utf-8') as f:
                status["merged_data"]["count"] = sum(1 for _ in f)
        
        return status
    
    def check_model_artifacts(self) -> dict:
        """Kiểm tra model artifacts"""
        status = {
            "lora_model": {"exists": False, "size": 0},
            "merged_model": {"exists": False, "size": 0},
            "gguf_model": {"exists": False, "size": 0},
            "lm_studio_deployment": {"exists": False, "size": 0}
        }
        
        # Check LoRA model
        lora_dir = self.artifacts_dir / "lora"
        if lora_dir.exists():
            status["lora_model"]["exists"] = True
            status["lora_model"]["size"] = sum(
                f.stat().st_size for f in lora_dir.rglob('*') if f.is_file()
            ) / (1024 * 1024)  # MB
        
        # Check merged model
        merged_dir = self.artifacts_dir / "hf_merged"
        if merged_dir.exists():
            status["merged_model"]["exists"] = True
            status["merged_model"]["size"] = sum(
                f.stat().st_size for f in merged_dir.rglob('*') if f.is_file()
            ) / (1024 * 1024)  # MB
        
        # Check GGUF model
        gguf_file = self.artifacts_dir / "gguf" / "model.Q4_K_M.gguf"
        if gguf_file.exists():
            status["gguf_model"]["exists"] = True
            status["gguf_model"]["size"] = gguf_file.stat().st_size / (1024 * 1024)  # MB
        
        # Check LM Studio deployment
        lm_studio_path = Path(os.environ.get('LOCALAPPDATA', '')) / "LM Studio" / "models" / "phi-4-mini-reasoning-daily"
        if lm_studio_path.exists():
            status["lm_studio_deployment"]["exists"] = True
            status["lm_studio_deployment"]["size"] = sum(
                f.stat().st_size for f in lm_studio_path.rglob('*') if f.is_file()
            ) / (1024 * 1024)  # MB
        
        return status
    
    def check_dependencies(self) -> dict:
        """Kiểm tra dependencies"""
        status = {
            "python_packages": {},
            "external_tools": {},
            "services": {}
        }
        
        # Check Python packages
        required_packages = [
            "unsloth", "transformers", "datasets", "trl", 
            "torch", "sqlalchemy", "elasticsearch", "fastapi"
        ]
        
        for package in required_packages:
            try:
                __import__(package)
                status["python_packages"][package] = "✅ Installed"
            except ImportError:
                status["python_packages"][package] = "❌ Missing"
        
        # Check external tools
        llama_cpp_dir = os.environ.get("LLAMA_CPP_DIR")
        if llama_cpp_dir and os.path.exists(llama_cpp_dir):
            status["external_tools"]["llama_cpp"] = "✅ Available"
        else:
            status["external_tools"]["llama_cpp"] = "❌ Not configured"
        
        # Check services
        try:
            # Check database connection
            from database import SessionLocal
            db = SessionLocal()
            db.close()
            status["services"]["database"] = "✅ Connected"
        except Exception as e:
            status["services"]["database"] = f"❌ Error: {str(e)[:50]}"
        
        try:
            # Check Elasticsearch
            import requests
            response = requests.get("http://localhost:9200/_cluster/health", timeout=5)
            if response.status_code == 200:
                status["services"]["elasticsearch"] = "✅ Connected"
            else:
                status["services"]["elasticsearch"] = "❌ Not responding"
        except Exception:
            status["services"]["elasticsearch"] = "❌ Not available"
        
        return status
    
    def check_recent_activity(self) -> dict:
        """Kiểm tra hoạt động gần đây"""
        status = {
            "last_training": None,
            "recent_chats": 0,
            "high_rated_chats": 0
        }
        
        # Check last training time
        lora_dir = self.artifacts_dir / "lora"
        if lora_dir.exists():
            model_files = list(lora_dir.glob("*.bin")) + list(lora_dir.glob("*.safetensors"))
            if model_files:
                latest_model = max(model_files, key=os.path.getctime)
                status["last_training"] = datetime.fromtimestamp(
                    latest_model.stat().st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")
        
        # Check recent chats (last 24h)
        try:
            from database import SessionLocal
            from models import ChatHistory
            from datetime import datetime, timedelta
            
            db = SessionLocal()
            since = datetime.utcnow() - timedelta(days=1)
            
            recent_chats = db.query(ChatHistory).filter(
                ChatHistory.created_at >= since
            ).count()
            
            high_rated_chats = db.query(ChatHistory).filter(
                ChatHistory.created_at >= since,
                ChatHistory.rating >= 4
            ).count()
            
            status["recent_chats"] = recent_chats
            status["high_rated_chats"] = high_rated_chats
            
            db.close()
            
        except Exception as e:
            status["recent_chats"] = f"Error: {str(e)[:50]}"
            status["high_rated_chats"] = f"Error: {str(e)[:50]}"
        
        return status
    
    def run_health_check(self) -> dict:
        """Chạy health check toàn diện"""
        print("🔍 Agent Health Check")
        print("=" * 50)
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "training_data": self.check_training_data(),
            "model_artifacts": self.check_model_artifacts(),
            "dependencies": self.check_dependencies(),
            "recent_activity": self.check_recent_activity()
        }
        
        return health_status
    
    def print_status_report(self, status: dict):
        """In báo cáo trạng thái"""
        print(f"\n📊 AGENT STATUS REPORT - {status['timestamp']}")
        print("=" * 60)
        
        # Training Data Status
        print("\n📚 Training Data:")
        td = status["training_data"]
        print(f"   Daily data: {'✅' if td['daily_data']['exists'] else '❌'} "
              f"({td['daily_data']['count']} files)")
        if td['daily_data']['latest']:
            print(f"   Latest: {td['daily_data']['latest']}")
        
        print(f"   KB data: {'✅' if td['kb_data']['exists'] else '❌'} "
              f"({td['kb_data']['count']} entries)")
        print(f"   Merged data: {'✅' if td['merged_data']['exists'] else '❌'} "
              f"({td['merged_data']['count']} entries)")
        
        # Model Artifacts Status
        print("\n🤖 Model Artifacts:")
        ma = status["model_artifacts"]
        print(f"   LoRA model: {'✅' if ma['lora_model']['exists'] else '❌'} "
              f"({ma['lora_model']['size']:.1f} MB)")
        print(f"   Merged model: {'✅' if ma['merged_model']['exists'] else '❌'} "
              f"({ma['merged_model']['size']:.1f} MB)")
        print(f"   GGUF model: {'✅' if ma['gguf_model']['exists'] else '❌'} "
              f"({ma['gguf_model']['size']:.1f} MB)")
        print(f"   LM Studio: {'✅' if ma['lm_studio_deployment']['exists'] else '❌'} "
              f"({ma['lm_studio_deployment']['size']:.1f} MB)")
        
        # Dependencies Status
        print("\n🔧 Dependencies:")
        deps = status["dependencies"]
        for package, status_text in deps["python_packages"].items():
            print(f"   {package}: {status_text}")
        
        for tool, status_text in deps["external_tools"].items():
            print(f"   {tool}: {status_text}")
        
        for service, status_text in deps["services"].items():
            print(f"   {service}: {status_text}")
        
        # Recent Activity
        print("\n📈 Recent Activity:")
        ra = status["recent_activity"]
        if ra["last_training"]:
            print(f"   Last training: {ra['last_training']}")
        else:
            print(f"   Last training: ❌ Never")
        
        print(f"   Recent chats (24h): {ra['recent_chats']}")
        print(f"   High-rated chats (24h): {ra['high_rated_chats']}")
        
        # Overall Health Score
        total_checks = 0
        passed_checks = 0
        
        # Count checks
        for category in ["training_data", "model_artifacts", "dependencies"]:
            for item in status[category].values():
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, bool):
                            total_checks += 1
                            if value:
                                passed_checks += 1
                        elif isinstance(value, str) and "✅" in value:
                            total_checks += 1
                            passed_checks += 1
        
        health_score = (passed_checks / total_checks * 100) if total_checks > 0 else 0
        
        print(f"\n🎯 Overall Health Score: {health_score:.1f}%")
        
        if health_score >= 80:
            print("🟢 Agent Status: HEALTHY")
        elif health_score >= 60:
            print("🟡 Agent Status: WARNING")
        else:
            print("🔴 Agent Status: CRITICAL")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if not td['daily_data']['exists']:
            print("   • Run daily training to generate training data")
        if not ma['lora_model']['exists']:
            print("   • Train LoRA model with current data")
        if not ma['gguf_model']['exists']:
            print("   • Convert model to GGUF format")
        if isinstance(ra['high_rated_chats'], int) and ra['high_rated_chats'] < 5:
            print("   • Need more high-rated chat interactions")
        
        return health_score
    
    def save_status_report(self, status: dict, filename: str = None):
        """Lưu báo cáo trạng thái"""
        if filename is None:
            filename = f"agent_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_path = self.logs_dir / filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Status report saved: {report_path}")
        return report_path


def main():
    """Main function"""
    monitor = AgentMonitor()
    
    # Run health check
    status = monitor.run_health_check()
    
    # Print status report
    health_score = monitor.print_status_report(status)
    
    # Save report
    monitor.save_status_report(status)
    
    # Exit with appropriate code
    if health_score >= 80:
        sys.exit(0)  # Success
    elif health_score >= 60:
        sys.exit(1)  # Warning
    else:
        sys.exit(2)  # Critical


if __name__ == "__main__":
    main()
