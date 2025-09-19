# PowerShell script để chạy Daily Training Agent
# Script này sẽ tự động chạy toàn bộ quy trình daily training

param(
    [switch]$Monitor,      # Chỉ chạy monitoring
    [switch]$Training,     # Chỉ chạy training
    [switch]$Full,         # Chạy cả monitoring và training
    [string]$Config = "agent_config.json"  # Config file
)

Write-Host "🤖 Daily Training Agent" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Set working directory
Set-Location "D:\hannah-ai-chat\hannah-ai-chat"

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

# Default action if no parameters
if (-not $Monitor -and -not $Training -and -not $Full) {
    $Full = $true
}

# Function to run monitoring
function Run-Monitoring {
    Write-Host "`n🔍 Running Agent Monitoring..." -ForegroundColor Yellow
    try {
        python scripts/monitor_agent.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Monitoring completed successfully" -ForegroundColor Green
        }
        elseif ($LASTEXITCODE -eq 1) {
            Write-Host "⚠️  Monitoring completed with warnings" -ForegroundColor Yellow
        }
        else {
            Write-Host "❌ Monitoring found critical issues" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Monitoring failed: $_" -ForegroundColor Red
    }
}

# Function to run training
function Run-Training {
    Write-Host "`n🚀 Running Daily Training..." -ForegroundColor Yellow
    try {
        python scripts/agent_daily_training.py
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Training completed successfully" -ForegroundColor Green
        }
        else {
            Write-Host "❌ Training failed" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "❌ Training failed: $_" -ForegroundColor Red
    }
}

# Function to check dependencies
function Check-Dependencies {
    Write-Host "`n🔧 Checking dependencies..." -ForegroundColor Yellow
    
    $requiredPackages = @(
        "unsloth", "transformers", "datasets", "trl", 
        "torch", "sqlalchemy", "elasticsearch", "fastapi"
    )
    
    $missingPackages = @()
    foreach ($package in $requiredPackages) {
        try {
            python -c "import $($package.Replace('-', '_'))" 2>$null
            if ($LASTEXITCODE -ne 0) {
                $missingPackages += $package
            }
        }
        catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "❌ Missing packages: $($missingPackages -join ', ')" -ForegroundColor Red
        Write-Host "Installing missing packages..." -ForegroundColor Yellow
        pip install $missingPackages
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ Failed to install packages!" -ForegroundColor Red
            exit 1
        }
    }
    
    Write-Host "✅ All dependencies are ready!" -ForegroundColor Green
}

# Function to show agent status
function Show-AgentStatus {
    Write-Host "`n📊 Agent Status Summary:" -ForegroundColor Cyan
    
    # Check if training data exists
    $dailyData = "data/daily/latest.jsonl"
    if (Test-Path $dailyData) {
        $sampleCount = (Get-Content $dailyData | Measure-Object -Line).Lines
        Write-Host "   📚 Training data: ✅ $sampleCount samples" -ForegroundColor Green
    }
    else {
        Write-Host "   📚 Training data: ❌ Not found" -ForegroundColor Red
    }
    
    # Check if LoRA model exists
    $loraModel = "artifacts/lora"
    if (Test-Path $loraModel) {
        Write-Host "   🤖 LoRA model: ✅ Available" -ForegroundColor Green
    }
    else {
        Write-Host "   🤖 LoRA model: ❌ Not found" -ForegroundColor Red
    }
    
    # Check if GGUF model exists
    $ggufModel = "artifacts/gguf/model.Q4_K_M.gguf"
    if (Test-Path $ggufModel) {
        $sizeMB = [math]::Round((Get-Item $ggufModel).Length / 1MB, 1)
        Write-Host "   🔄 GGUF model: ✅ $sizeMB MB" -ForegroundColor Green
    }
    else {
        Write-Host "   🔄 GGUF model: ❌ Not found" -ForegroundColor Red
    }
    
    # Check LM Studio deployment
    $lmStudioPath = "$env:LOCALAPPDATA\LM Studio\models\phi-4-mini-reasoning-daily"
    if (Test-Path $lmStudioPath) {
        Write-Host "   🎮 LM Studio: ✅ Deployed" -ForegroundColor Green
    }
    else {
        Write-Host "   🎮 LM Studio: ❌ Not deployed" -ForegroundColor Red
    }
}

# Function to show help
function Show-Help {
    Write-Host "`n📖 Usage Examples:" -ForegroundColor Cyan
    Write-Host "   .\scripts\run-agent.ps1 -Monitor     # Chỉ chạy monitoring" -ForegroundColor Gray
    Write-Host "   .\scripts\run-agent.ps1 -Training    # Chỉ chạy training" -ForegroundColor Gray
    Write-Host "   .\scripts\run-agent.ps1 -Full        # Chạy cả monitoring và training" -ForegroundColor Gray
    Write-Host "   .\scripts\run-agent.ps1              # Mặc định chạy Full" -ForegroundColor Gray
    Write-Host ""
    Write-Host "📋 What each mode does:" -ForegroundColor Cyan
    Write-Host "   Monitor:   Kiểm tra trạng thái agent và dependencies" -ForegroundColor Gray
    Write-Host "   Training:  Chạy daily training pipeline" -ForegroundColor Gray
    Write-Host "   Full:      Chạy monitoring trước, sau đó training" -ForegroundColor Gray
}

# Main execution
try {
    # Check dependencies first
    Check-Dependencies
    
    # Show current status
    Show-AgentStatus
    
    # Execute based on parameters
    if ($Monitor) {
        Run-Monitoring
    }
    elseif ($Training) {
        Run-Training
    }
    elseif ($Full) {
        Run-Monitoring
        Write-Host "`n⏳ Waiting 5 seconds before training..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        Run-Training
    }
    
    # Show final status
    Write-Host "`n📊 Final Status:" -ForegroundColor Cyan
    Show-AgentStatus
    
    Write-Host "`n🎉 Agent execution completed!" -ForegroundColor Green
    Write-Host "📄 Check logs in: logs/" -ForegroundColor Gray
    Write-Host "📊 Check artifacts in: artifacts/" -ForegroundColor Gray
    
}
catch {
    Write-Host "`n❌ Agent execution failed: $_" -ForegroundColor Red
    Write-Host "📄 Check logs for details: logs/" -ForegroundColor Gray
    exit 1
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
