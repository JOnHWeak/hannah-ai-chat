Setup LM Studio usage with this project
======================================

1) Start local server
- Open LM Studio → Server → Start server (OpenAI-compatible)
- Base URL: http://127.0.0.1:1234/v1, API key: lm-studio
- Load model: `microsoft/phi-4-mini-reasoning` (or your custom GGUF)

2) Python client
Use `lm_client.py`:

```python
from lm_client import LMStudioClient

client = LMStudioClient()
text = client.chat(
    model="microsoft/phi-4-mini-reasoning",
    messages=[{"role":"user","content":"Xin chào"}],
    temperature=0.2,
)
print(text)
```

3) Daily pipeline
- Export rated data: `python scripts/data/export_daily_dataset.py`
- (Optional) Export SFT from ES: `python scripts/sft/es_to_sft.py`
- Train LoRA: `python scripts/train/train_lora_unsloth.py`
- Optional merge/convert: set `LLAMA_CPP_DIR` env then `python scripts/train/merge_and_convert.py`
- PowerShell automation: `scripts/daily-train.ps1` (add to Task Scheduler)


