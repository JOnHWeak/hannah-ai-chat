# PowerShell script để thiết lập AI học từ dataset
# Chạy script này để import toàn bộ dữ liệu từ Data_set vào hệ thống AI

Write-Host "🚀 Setting up AI Dataset Learning System" -ForegroundColor Green
Write-Host "=" * 50 -ForegroundColor Cyan

# Kiểm tra Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python first." -ForegroundColor Red
    exit 1
}

# Kiểm tra dependencies
Write-Host "`n🔍 Checking dependencies..." -ForegroundColor Yellow
$requiredPackages = @("python-pptx", "sqlalchemy", "psycopg2-binary", "elasticsearch", "fastapi", "uvicorn")

$missingPackages = @()
foreach ($package in $requiredPackages) {
    try {
        python -c "import $($package.Replace('-', '_'))" 2>$null
        if ($LASTEXITCODE -ne 0) {
            $missingPackages += $package
        }
    } catch {
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

# Thiết lập environment variables
Write-Host "`n🔧 Setting up environment..." -ForegroundColor Yellow
$env:DATASET_DIR = "D:\Data_set"
$env:IMPORT_CREATED_BY = "dataset_import"
$env:MIN_CONTENT_LENGTH = "100"
$env:KB_CATEGORY = "academic_dataset"

Write-Host "   DATASET_DIR = $env:DATASET_DIR" -ForegroundColor Gray
Write-Host "   IMPORT_CREATED_BY = $env:IMPORT_CREATED_BY" -ForegroundColor Gray

# Kiểm tra dataset directory
if (-not (Test-Path $env:DATASET_DIR)) {
    Write-Host "❌ Dataset directory not found: $env:DATASET_DIR" -ForegroundColor Red
    Write-Host "Please make sure the Data_set folder exists at the specified path." -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Dataset directory found!" -ForegroundColor Green

# Chạy setup script
Write-Host "`n🚀 Starting dataset learning setup..." -ForegroundColor Green
python scripts/setup_dataset_learning.py

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n🎉 Setup completed successfully!" -ForegroundColor Green
    Write-Host "`n📋 What was accomplished:" -ForegroundColor Cyan
    Write-Host "   ✅ Dataset imported to knowledge base" -ForegroundColor Green
    Write-Host "   ✅ Knowledge base indexed to Elasticsearch" -ForegroundColor Green  
    Write-Host "   ✅ SFT training data generated" -ForegroundColor Green
    Write-Host "   ✅ Integration tested" -ForegroundColor Green
    
    Write-Host "`n🚀 Next Steps:" -ForegroundColor Cyan
    Write-Host "   1. Start the API server:" -ForegroundColor White
    Write-Host "      .\scripts\run_api.ps1" -ForegroundColor Gray
    Write-Host "   2. Test the chat API at:" -ForegroundColor White
    Write-Host "      http://localhost:8000/docs" -ForegroundColor Gray
    Write-Host "   3. Optional: Fine-tune the model:" -ForegroundColor White
    Write-Host "      python scripts/train/train_lora_unsloth.py" -ForegroundColor Gray
    
    Write-Host "`n💡 The AI can now learn from your dataset!" -ForegroundColor Green
    Write-Host "   Ask questions about CSI106, DSA, Database, Sorting, etc." -ForegroundColor Yellow
} else {
    Write-Host "`n❌ Setup failed! Check the error messages above." -ForegroundColor Red
    Write-Host "Common issues:" -ForegroundColor Yellow
    Write-Host "   • Database connection problems" -ForegroundColor Gray
    Write-Host "   • Elasticsearch not running" -ForegroundColor Gray
    Write-Host "   • Missing dependencies" -ForegroundColor Gray
    Write-Host "   • File permission issues" -ForegroundColor Gray
}

Write-Host "`nPress any key to continue..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
