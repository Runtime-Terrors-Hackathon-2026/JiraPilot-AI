# JiraPilot AI - Complete System Runner Script (Windows PowerShell)

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "           JiraPilot AI — Starting Full Stack" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# Set Paths for Runtimes
$toolsDir = "C:\Users\support\tools"
$pythonPath = "C:\Users\support\AppData\Local\Programs\Python\Python312\python.exe"

$env:JAVA_HOME = "$toolsDir\jdk-21"
$env:PATH = "$toolsDir\jdk-21\bin;$toolsDir\maven\bin;$toolsDir\node;C:\Users\support\AppData\Local\Programs\Python\Python312;C:\Users\support\AppData\Local\Programs\Python\Python312\Scripts;" + $env:PATH

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 1. Start Python AI Service on Port 8000
Write-Host "[1/3] Starting Python AI Service on port 8000..." -ForegroundColor Green
$aiProcess = Start-Process -FilePath $pythonPath -ArgumentList "-m uvicorn app.main:app --host 0.0.0.0 --port 8000" -WorkingDirectory "$scriptDir\ai-service" -PassThru

# 2. Start Java Spring Boot Backend on Port 8080
Write-Host "[2/3] Starting Spring Boot Orchestrator Backend on port 8080..." -ForegroundColor Green
$mvnCmd = "$toolsDir\maven\bin\mvn.cmd"
$backendProcess = Start-Process -FilePath $mvnCmd -ArgumentList "spring-boot:run" -WorkingDirectory "$scriptDir\backend" -PassThru

# 3. Start Frontend Vite Dev Server on Port 3000
Write-Host "[3/3] Starting React Vite Frontend on port 3000..." -ForegroundColor Green
$npmCmd = "$toolsDir\node\npm.cmd"
$frontendProcess = Start-Process -FilePath $npmCmd -ArgumentList "run dev -- --host 0.0.0.0" -WorkingDirectory "$scriptDir\frontend" -PassThru

Write-Host ""
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " All services started successfully!" -ForegroundColor Green
Write-Host " - Frontend UI:        http://localhost:3000" -ForegroundColor Yellow
Write-Host " - Backend API:        http://localhost:8080" -ForegroundColor Yellow
Write-Host " - Python AI Service:  http://localhost:8000" -ForegroundColor Yellow
Write-Host " - H2 DB Console:      http://localhost:8080/h2-console" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "Press Ctrl+C or close the terminal to stop."
