# Local Trivy Security Scanning Utility for Windows PowerShell
# Runs Trivy inside a Docker container to scan the workspace without needing local installation.

$ErrorActionPreference = "Stop"

Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "       Trivy Local Workspace Security Scan          " -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan

# Check if Docker is running
try {
    $dockerCheck = docker version --format '{{.Server.Version}}'
} catch {
    Write-Host "Error: Docker is not installed or not running. Please start Docker Desktop first." -ForegroundColor Red
    Exit 1
}

# Find the workspace root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$WorkspaceRoot = (Get-Item (Join-Path $ScriptDir "..")).FullName

Write-Host "[1/3] Pulling latest Trivy Docker image..." -ForegroundColor Yellow
docker pull aquasec/trivy:latest | Out-Null

Write-Host "[2/3] Scanning entire workspace (Filesystem, Configs, Secrets)..." -ForegroundColor Yellow
docker run --rm `
  -v "${WorkspaceRoot}:/workspace" `
  -w /workspace `
  aquasec/trivy:latest fs `
  --scanners vuln,misconfig,secret `
  --severity HIGH,CRITICAL `
  --ignore-unfixed `
  --skip-dirs /workspace/ocr_pipeline/.venv,/workspace/.venv,/workspace/ocr_pipeline/__pycache__ `
  /workspace

Write-Host "[3/3] Checking if local Docker image exists for scanning..." -ForegroundColor Yellow
$imageExists = docker images -q ocr-pipeline:latest

if ($imageExists) {
    Write-Host "Scanning built local image: ocr-pipeline:latest..." -ForegroundColor Cyan
    # On Windows, mounting the docker socket may vary, but let's use standard Docker-in-Docker socket sharing
    docker run --rm `
      -v //var/run/docker.sock:/var/run/docker.sock `
      aquasec/trivy:latest image `
      --severity HIGH,CRITICAL `
      --ignore-unfixed `
      ocr-pipeline:latest
} else {
    Write-Host "Note: Local Docker image 'ocr-pipeline:latest' not found. Skip image scan." -ForegroundColor Yellow
    Write-Host "To scan the built image, first run: docker build -t ocr-pipeline:latest ocr_pipeline/" -ForegroundColor Yellow
}

Write-Host "[OK] Security scan pipeline completed!" -ForegroundColor Green
