#!/bin/bash
# Local Trivy Security Scanning Utility for Unix-like/Git-Bash environments
# Runs Trivy inside a Docker container to scan the workspace without needing local installation.

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${BLUE}       Trivy Local Workspace Security Scan          ${NC}"
echo -e "${BLUE}====================================================${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed or not running. Docker is required to run Trivy without native installation.${NC}"
    exit 1
fi

# Find the workspace root (parent folder of ocr_pipeline)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo -e "${YELLOW}[1/3] Pulling latest Trivy Docker image...${NC}"
docker pull aquasec/trivy:latest > /dev/null

echo -e "${YELLOW}[2/3] Scanning entire workspace (Filesystem, Configs, Secrets)...${NC}"
docker run --rm \
  -v "${WORKSPACE_ROOT}:/workspace" \
  -w /workspace \
  aquasec/trivy:latest fs \
  --scanners vuln,misconfig,secret \
  --severity HIGH,CRITICAL \
  --ignore-unfixed \
  --skip-dirs /workspace/ocr_pipeline/.venv,/workspace/.venv,/workspace/ocr_pipeline/__pycache__ \
  /workspace

echo -e "${YELLOW}[3/3] Checking if local Docker image exists for scanning...${NC}"
if docker image inspect ocr-pipeline:latest >/dev/null 2>&1; then
    echo -e "${BLUE}Scanning built local image: ocr-pipeline:latest...${NC}"
    docker run --rm \
      -v /var/run/docker.sock:/var/run/docker.sock \
      aquasec/trivy:latest image \
      --severity HIGH,CRITICAL \
      --ignore-unfixed \
      ocr-pipeline:latest
else
    echo -e "${YELLOW}Note: Local Docker image 'ocr-pipeline:latest' not found. Skip image scan.${NC}"
    echo -e "${YELLOW}To scan the built image, first run: docker build -t ocr-pipeline:latest ocr_pipeline/${NC}"
fi

echo -e "${GREEN}[OK] Security scan pipeline completed!${NC}"
