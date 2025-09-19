$ErrorActionPreference = "Stop"
Set-Location "D:\hannah-ai-chat"
py -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000


