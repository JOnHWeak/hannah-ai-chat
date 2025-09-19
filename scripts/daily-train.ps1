$ErrorActionPreference = "Stop"

Set-Location "D:\hannah-ai-chat"

python scripts\data\export_daily_dataset.py

# Link newest dataset to a stable path for the trainer
$today = (Get-Date).ToString('yyyy-MM-dd')
$src = "data/daily/$today.jsonl"
$dst = "data/daily/latest.jsonl"
Copy-Item $src $dst -Force

# Optional: pull KB from Elasticsearch and create SFT file
try {
    py scripts\sft\es_to_sft.py
    if (Test-Path "data/kb_es_sft.jsonl") {
        # Merge KB SFT with daily SFT
        Get-Content "data/kb_es_sft.jsonl", "data/daily/latest.jsonl" | Set-Content "data/daily/latest_merged.jsonl"
    }
}
catch {
    Write-Host "Skip ES SFT merge: $_"
}

if (Test-Path "data/daily/latest_merged.jsonl") {
    Copy-Item "data/daily/latest_merged.jsonl" "data/daily/latest.jsonl" -Force
}

python scripts\train\train_lora_unsloth.py

# Optional: merge & convert requires llama.cpp; skip if not configured
if ($env:LLAMA_CPP_DIR) {
    python scripts\train\merge_and_convert.py
}

# Copy GGUF to LM Studio models folder if exists
$gguf = "artifacts/gguf/model.Q4_K_M.gguf"
if (Test-Path $gguf) {
    $dest = "$env:LOCALAPPDATA/LM Studio/models/phi-4-mini-reasoning-daily"
    New-Item -ItemType Directory -Force -Path $dest | Out-Null
    Copy-Item $gguf "$dest/model.Q4_K_M.gguf" -Force
}

Write-Host "Daily training pipeline finished."


