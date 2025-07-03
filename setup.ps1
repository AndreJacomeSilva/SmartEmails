# PowerShell script to setup and run SmartGold-SmartCompose Email AI API
# This script installs dependencies and starts the server

Write-Host "🚀 SmartGold-SmartCompose Email AI Setup" -ForegroundColor Green
Write-Host "=" * 50

# Check if Python is installed
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Install/upgrade pip
Write-Host "📦 Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

# Check if .env file exists
if (Test-Path ".env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found. Creating template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env" -ErrorAction SilentlyContinue
    Write-Host "Please configure your .env file with the required API keys" -ForegroundColor Yellow
}

Write-Host "`n🔧 Setup complete!" -ForegroundColor Green

# Ask if user wants to start the server
$startServer = Read-Host "Would you like to start the server now? (y/N)"

if ($startServer -eq "y" -or $startServer -eq "Y") {
    Write-Host "`n🌟 Starting server..." -ForegroundColor Green
    Write-Host "Server will be available at: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "API documentation: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
    Write-Host ""
    
    # Start the server
    python -m uvicorn src.main:app --reload --port 8000 --host 0.0.0.0
}

Write-Host "`n✅ Setup script completed!" -ForegroundColor Green
