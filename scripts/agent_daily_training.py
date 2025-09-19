#!/usr/bin/env python3
"""
Daily Training Agent - Tự động chạy daily training pipeline
"""

import os
import sys
import json
import subprocess
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class DailyTrainingAgent:
    """Agent để tự động chạy daily training"""
    
    def __init__(self, config_file: str = "agent_config.json"):
        self.project_root = Path(__file__).parent.parent
        self.config_file = self.project_root / config_file
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Load configuration
        self.config = self.load_config()
        
        self.logger.info("🤖 Daily Training Agent initialized")
    
    def setup_logging(self):
        """Setup logging cho agent"""
        log_file = self.logs_dir / f"agent_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def load_config(self) -> Dict:
        """Load configuration từ file"""
        default_config = {
            "training": {
                "base_model": "microsoft/Phi-4-mini-instruct",
                "max_seq_length": 4096,
                "output_dir": "artifacts/lora",
                "data_file": "data/daily/latest.jsonl"
            },
            "lora": {
                "r": 16,
                "alpha": 32,
                "dropout": 0.05,
                "target_modules": "all-linear"
            },
            "training_args": {
                "per_device_batch_size": 1,
                "gradient_accumulation_steps": 8,
                "num_train_epochs": 1,
                "learning_rate": 1e-4,
                "logging_steps": 10,
                "save_strategy": "epoch",
                "bf16": True
            },
            "data_sources": {
                "chat_history": {
                    "enabled": True,
                    "min_rating": 4,
                    "days_back": 1
                },
                "knowledge_base": {
                    "enabled": True,
                    "es_index": "kb_software_engineering",
                    "max_size": 500
                },
                "dataset": {
                    "enabled": True,
                    "dataset_dir": "D:/Data_set",
                    "categories": ["all"]
                }
            },
            "conversion": {
                "llama_cpp_dir": "C:/tools/llama.cpp",
                "quantization": "Q4_K_M",
                "lm_studio_deploy": True
            },
            "schedule": {
                "enabled": True,
                "time": "02:00",
                "timezone": "Asia/Ho_Chi_Minh"
            }
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.logger.info(f"✅ Loaded config from {self.config_file}")
                return config
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load config: {e}, using defaults")
        else:
            # Create default config file
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"📄 Created default config: {self.config_file}")
        
        return default_config
    
    def run_command(self, command: List[str], description: str) -> bool:
        """Chạy command và log kết quả"""
        self.logger.info(f"🔄 {description}...")
        self.logger.debug(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=True
            )
            
            self.logger.info(f"✅ {description} completed successfully")
            if result.stdout:
                self.logger.debug(f"Output: {result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ {description} failed!")
            self.logger.error(f"Error: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"❌ {description} failed with exception: {e}")
            return False
    
    def export_daily_data(self) -> bool:
        """Export daily chat data"""
        if not self.config["data_sources"]["chat_history"]["enabled"]:
            self.logger.info("⏭️  Chat history export disabled")
            return True
        
        command = [sys.executable, "scripts/data/export_daily_dataset.py"]
        return self.run_command(command, "Export daily chat data")
    
    def export_kb_data(self) -> bool:
        """Export knowledge base data"""
        if not self.config["data_sources"]["knowledge_base"]["enabled"]:
            self.logger.info("⏭️  Knowledge base export disabled")
            return True
        
        command = [sys.executable, "scripts/sft/es_to_sft.py"]
        return self.run_command(command, "Export knowledge base data")
    
    def export_dataset_data(self) -> bool:
        """Export dataset data"""
        if not self.config["data_sources"]["dataset"]["enabled"]:
            self.logger.info("⏭️  Dataset export disabled")
            return True
        
        command = [sys.executable, "scripts/ingest/import_dataset_to_kb.py"]
        return self.run_command(command, "Export dataset data")
    
    def merge_datasets(self) -> bool:
        """Merge datasets thành training data"""
        self.logger.info("🔄 Merging datasets...")
        
        try:
            daily_file = self.project_root / "data/daily/latest.jsonl"
            kb_file = self.project_root / "data/kb_es_sft.jsonl"
            dataset_file = self.project_root / "data/kb_sft.jsonl"
            
            merged_data = []
            
            # Add daily data
            if daily_file.exists():
                with open(daily_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            merged_data.append(json.loads(line))
                self.logger.info(f"📊 Added {len(merged_data)} daily samples")
            
            # Add KB data
            if kb_file.exists():
                kb_count = 0
                with open(kb_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            merged_data.append(json.loads(line))
                            kb_count += 1
                self.logger.info(f"📚 Added {kb_count} KB samples")
            
            # Add dataset data
            if dataset_file.exists():
                dataset_count = 0
                with open(dataset_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            merged_data.append(json.loads(line))
                            dataset_count += 1
                self.logger.info(f"📁 Added {dataset_count} dataset samples")
            
            # Write merged data
            merged_file = self.project_root / "data/daily/latest_merged.jsonl"
            with open(merged_file, 'w', encoding='utf-8') as f:
                for item in merged_data:
                    f.write(json.dumps(item, ensure_ascii=False) + "\n")
            
            # Update latest file
            daily_file.unlink(missing_ok=True)
            merged_file.rename(daily_file)
            
            self.logger.info(f"✅ Merged {len(merged_data)} total samples")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Dataset merge failed: {e}")
            return False
    
    def train_lora_model(self) -> bool:
        """Train LoRA model"""
        command = [sys.executable, "scripts/train/train_lora_unsloth.py"]
        return self.run_command(command, "Train LoRA model")
    
    def convert_to_gguf(self) -> bool:
        """Convert model to GGUF format"""
        llama_cpp_dir = self.config["conversion"]["llama_cpp_dir"]
        if not llama_cpp_dir or not os.path.exists(llama_cpp_dir):
            self.logger.warning("⚠️  Llama.cpp not configured, skipping GGUF conversion")
            return True
        
        command = [sys.executable, "scripts/train/merge_and_convert.py"]
        return self.run_command(command, "Convert to GGUF format")
    
    def deploy_to_lm_studio(self) -> bool:
        """Deploy model to LM Studio"""
        if not self.config["conversion"]["lm_studio_deploy"]:
            self.logger.info("⏭️  LM Studio deployment disabled")
            return True
        
        try:
            gguf_file = self.project_root / "artifacts/gguf/model.Q4_K_M.gguf"
            if not gguf_file.exists():
                self.logger.warning("⚠️  GGUF file not found, skipping LM Studio deployment")
                return True
            
            lm_studio_dir = Path(os.environ.get('LOCALAPPDATA', '')) / "LM Studio" / "models" / "phi-4-mini-reasoning-daily"
            lm_studio_dir.mkdir(parents=True, exist_ok=True)
            
            import shutil
            shutil.copy2(gguf_file, lm_studio_dir / "model.Q4_K_M.gguf")
            
            self.logger.info(f"✅ Deployed to LM Studio: {lm_studio_dir}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ LM Studio deployment failed: {e}")
            return False
    
    def check_training_prerequisites(self) -> bool:
        """Kiểm tra prerequisites trước khi training"""
        self.logger.info("🔍 Checking training prerequisites...")
        
        # Check if we have training data
        daily_file = self.project_root / "data/daily/latest.jsonl"
        if not daily_file.exists():
            self.logger.error("❌ No training data found")
            return False
        
        # Count training samples
        with open(daily_file, 'r', encoding='utf-8') as f:
            sample_count = sum(1 for line in f if line.strip())
        
        if sample_count < 5:
            self.logger.warning(f"⚠️  Very few training samples: {sample_count}")
            self.logger.warning("Consider collecting more high-rated chat interactions")
        
        self.logger.info(f"📊 Found {sample_count} training samples")
        
        # Check GPU availability
        try:
            import torch
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                self.logger.info(f"🎮 GPU available: {gpu_count} devices")
            else:
                self.logger.warning("⚠️  No GPU available, training will be slow")
        except ImportError:
            self.logger.warning("⚠️  PyTorch not available")
        
        return True
    
    def run_daily_training(self) -> bool:
        """Chạy toàn bộ daily training pipeline"""
        self.logger.info("🚀 Starting daily training pipeline")
        self.logger.info("=" * 50)
        
        start_time = datetime.now()
        
        # Step 1: Export data sources
        steps = [
            ("Export daily chat data", self.export_daily_data),
            ("Export knowledge base data", self.export_kb_data),
            ("Export dataset data", self.export_dataset_data),
            ("Merge datasets", self.merge_datasets),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                self.logger.error(f"❌ Pipeline failed at: {step_name}")
                return False
        
        # Step 2: Check prerequisites
        if not self.check_training_prerequisites():
            self.logger.error("❌ Training prerequisites not met")
            return False
        
        # Step 3: Train model
        training_steps = [
            ("Train LoRA model", self.train_lora_model),
            ("Convert to GGUF", self.convert_to_gguf),
            ("Deploy to LM Studio", self.deploy_to_lm_studio),
        ]
        
        for step_name, step_func in training_steps:
            if not step_func():
                self.logger.warning(f"⚠️  {step_name} failed, continuing...")
        
        # Calculate duration
        duration = datetime.now() - start_time
        self.logger.info(f"✅ Daily training pipeline completed in {duration}")
        
        return True
    
    def save_training_report(self, success: bool):
        """Lưu báo cáo training"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "config": self.config,
            "duration": str(datetime.now() - datetime.now())  # Will be updated
        }
        
        report_file = self.logs_dir / f"training_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"📄 Training report saved: {report_file}")


def main():
    """Main function"""
    agent = DailyTrainingAgent()
    
    try:
        success = agent.run_daily_training()
        agent.save_training_report(success)
        
        if success:
            agent.logger.info("🎉 Daily training completed successfully!")
            sys.exit(0)
        else:
            agent.logger.error("❌ Daily training failed!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        agent.logger.info("⏹️  Training interrupted by user")
        sys.exit(130)
    except Exception as e:
        agent.logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
