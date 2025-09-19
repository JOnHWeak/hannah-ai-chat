# 🤖 Agent Quick Start Guide

## 🚀 Chạy Agent Daily Training

### Cách 1: Tự Động (Khuyến nghị)
```powershell
.\scripts\run-agent.ps1 -Full
```

### Cách 2: Từng Bước
```powershell
# 1. Kiểm tra trạng thái
.\scripts\run-agent.ps1 -Monitor

# 2. Chạy training
.\scripts\run-agent.ps1 -Training
```

### Cách 3: Python Agent
```bash
python scripts/agent_daily_training.py
```

## 📊 Monitoring Agent

```bash
# Kiểm tra health status
python scripts/monitor_agent.py

# Hoặc dùng PowerShell
.\scripts\run-agent.ps1 -Monitor
```

## ⚙️ Cấu Hình Agent

Tạo file `agent_config.json`:

```json
{
  "training": {
    "base_model": "microsoft/Phi-4-mini-instruct",
    "output_dir": "artifacts/lora"
  },
  "data_sources": {
    "chat_history": {"enabled": true, "min_rating": 4},
    "knowledge_base": {"enabled": true},
    "dataset": {"enabled": true}
  },
  "conversion": {
    "lm_studio_deploy": true
  }
}
```

## 🎯 Agent Sẽ Làm Gì?

1. **📊 Export Data:** Chat history, Knowledge base, Dataset
2. **🔄 Merge Data:** Gộp tất cả thành training data
3. **🎯 Train LoRA:** Fine-tune model với Unsloth
4. **🔄 Convert:** Chuyển sang GGUF format
5. **🎮 Deploy:** Deploy vào LM Studio

## 📈 Kết Quả

- ✅ **LoRA Model:** `artifacts/lora/`
- ✅ **GGUF Model:** `artifacts/gguf/model.Q4_K_M.gguf`
- ✅ **LM Studio:** Tự động deploy
- ✅ **Logs:** `logs/agent_YYYYMMDD.log`

## 🚨 Troubleshooting

### Lỗi: "No training data"
```bash
# Kiểm tra chat có rating
python -c "from database import SessionLocal; from models import ChatHistory; db = SessionLocal(); print(db.query(ChatHistory).filter(ChatHistory.rating >= 4).count())"
```

### Lỗi: "CUDA out of memory"
```bash
# Giảm batch size trong config
"per_device_batch_size": 1,
"gradient_accumulation_steps": 16
```

### Lỗi: "Dependencies missing"
```bash
pip install unsloth transformers datasets trl torch
```

## 📅 Schedule Agent (Windows Task Scheduler)

1. Mở Task Scheduler (`taskschd.msc`)
2. Create Task → Name: "AI Daily Training Agent"
3. Triggers → Daily at 2:00 AM
4. Actions → Program: `PowerShell.exe`
5. Arguments: `-ExecutionPolicy Bypass -File "D:\hannah-ai-chat\hannah-ai-chat\scripts\run-agent.ps1" -Training`

## 🎉 Kết Quả Cuối Cùng

Sau khi agent chạy thành công:

- 🤖 **AI được train daily** từ dữ liệu mới
- 📚 **Học từ chat interactions** có rating cao
- 🎯 **Cải thiện performance** theo thời gian
- 🚀 **Tự động deploy** model mới

---

💡 **Tip:** Chạy `.\scripts\run-agent.ps1 -Monitor` để kiểm tra trạng thái agent trước khi training!
