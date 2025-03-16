#!/usr/bin/env bash
# Conscious AI Build & Launch Script
# Version 2.1.0

set -eo pipefail

# --------------------------
# Configuration
# --------------------------
PROJECT_NAME="conscious"
PYTHON_VERSION="3.10"
VENV_DIR=".venv"
CONFIG_DIR="config"
MODEL_DIR="models"
LOG_DIR="logs"
DOCKER_IMAGE="kaleidoscopeai/conscious"
DOCKER_TAG="latest"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --------------------------
# Error Handling
# --------------------------
handle_error() {
    local line="$1"
    local message="$2"
    echo -e "${RED}Error occurred on line $line: $message${NC}" >&2
    exit 1
}

trap 'handle_error ${LINENO} "$BASH_COMMAND"' ERR

# --------------------------
# Validation Functions
# --------------------------
validate_python_version() {
    local python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    [[ "$python_version" == "$PYTHON_VERSION" ]] || {
        echo -e "${RED}Python version mismatch. Required: $PYTHON_VERSION, Found: $python_version${NC}"
        exit 1
    }
}

check_directory_structure() {
    local dirs=("$CONFIG_DIR" "$MODEL_DIR" "$LOG_DIR" "tests")
    for dir in "${dirs[@]}"; do
        [[ -d "$dir" ]] || {
            echo -e "${YELLOW}Warning: Directory $dir not found. Creating...${NC}"
            mkdir -p "$dir"
        }
    done
}

# --------------------------
# Environment Setup
# --------------------------
setup_environment() {
    echo -e "${BLUE}Setting up environment...${NC}"
    
    # Create virtual environment
    python3 -m venv "$VENV_DIR" || {
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    }
    source "$VENV_DIR/bin/activate"

    # Install dependencies using modern Python packaging
    pip install --upgrade pip wheel setuptools
    if [[ -f "pyproject.toml" ]]; then
        pip install -e .[dev]
    else
        echo -e "${YELLOW}pyproject.toml not found, falling back to requirements.txt${NC}"
        pip install -r requirements.txt
    fi

    # Check for configuration files
    if [[ ! -f "$CONFIG_DIR/settings.env" ]]; then
        echo -e "${YELLOW}Creating default environment configuration...${NC}"
        cp "$CONFIG_DIR/sample.env" "$CONFIG_DIR/settings.env" 2>/dev/null || {
            echo -e "${YELLOW}No sample.env found. Creating new settings.env${NC}"
            touch "$CONFIG_DIR/settings.env"
        }
    fi
}

# --------------------------
# Model Management
# --------------------------
download_models() {
    echo -e "${BLUE}Checking for required models...${NC}"
    if [[ -d "$MODEL_DIR" && $(ls -A "$MODEL_DIR") ]]; then
        echo -e "${GREEN}Models directory already populated${NC}"
        return
    fi

    echo -e "${YELLOW}Downloading base models...${NC}"
    python3 - <<END
from huggingface_hub import snapshot_download
import os

model_dir = os.getenv('MODEL_DIR', 'models')
os.makedirs(model_dir, exist_ok=True)

snapshot_download(
    repo_id="consciousai/conscious-base",
    local_dir=model_dir,
    resume_download=True,
    token=os.getenv('HF_TOKEN')
)
END
}

# --------------------------
# Testing & Validation
# --------------------------
run_validation_checks() {
    echo -e "${BLUE}Running system checks...${NC}"
    
    # Type checking
    echo -e "${BLUE}Running type checks...${NC}"
    mypy --config-file mypy.ini conscious/

    # Unit tests
    echo -e "${BLUE}Running unit tests...${NC}"
    pytest -v --cov=conscious --cov-report=html tests/

    # Security checks
    echo -e "${BLUE}Running security audit...${NC}"
    bandit -r conscious/

    # Code quality
    echo -e "${BLUE}Checking code style...${NC}"
    flake8 conscious/
    black --check conscious/
}

# --------------------------
# Docker Management
# --------------------------
docker_build() {
    echo -e "${BLUE}Building Docker image...${NC}"
    docker build -t "$DOCKER_IMAGE:$DOCKER_TAG" . || {
        echo -e "${RED}Docker build failed${NC}"
        exit 1
    }
}

docker_run() {
    echo -e "${BLUE}Starting Docker container...${NC}"
    docker run -it --rm \
        -p 8000:8000 \
        -v ./models:/app/models \
        -v ./logs:/app/logs \
        -v ./config:/app/config \
        "$DOCKER_IMAGE:$DOCKER_TAG"
}

# --------------------------
# Launch System
# --------------------------
launch_development() {
    echo -e "${GREEN}Starting Conscious AI in development mode...${NC}"
    uvicorn conscious.api.main:app --reload --host 0.0.0.0 --port 8000
}

launch_production() {
    echo -e "${GREEN}Starting Conscious AI in production mode...${NC}"
    gunicorn -k uvicorn.workers.UvicornWorker conscious.api.main:app \
        --bind 0.0.0.0:8000 \
        --workers 4 \
        --access-logfile -
}

# --------------------------
# Main Execution
# --------------------------
main() {
    validate_python_version
    check_directory_structure

    case "$1" in
        docker)
            docker_build
            docker_run
            ;;
        dev)
            setup_environment
            download_models
            launch_development
            ;;
        prod)
            setup_environment
            download_models
            launch_production
            ;;
        test)
            setup_environment
            run_validation_checks
            ;;
        *)
            echo -e "${BLUE}Usage: $0 [option]${NC}"
            echo "Options:"
            echo "  docker   Build and run in Docker"
            echo "  dev      Start development server"
            echo "  prod     Start production server"
            echo "  test     Run validation checks"
            exit 1
            ;;
    esac
}

main "$@"
