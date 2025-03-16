#!/bin/bash
# setup_and_run.sh - Automate environment setup, testing, and application launch

# Exit immediately on errors (except where we handle them manually)
# (We will handle certain errors to allow the script to continue appropriately)
#set -e

# Log all output to a file for debugging and record-keeping
LOG_FILE="setup_and_run.log"
exec > >(tee -a "$LOG_FILE") 2>&1

echo "=== Starting Setup and Run Script ==="
echo "Timestamp: $(date)"

# Step 1: Create a virtual environment
echo "=== Step 1: Setting up Python virtual environment ==="
if ! command -v python3 &> /dev/null; then
  echo "ERROR: python3 is not installed or not in PATH." 
  exit 1
fi
echo "Creating Python virtual environment 'venv'..."
python3 -m venv venv
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to create virtual environment. Exiting."
  exit 1
fi

# Activate the virtual environment
# shellcheck disable=SC1091  # (suppress warning for sourcing an untracked file)
source venv/bin/activate
if [ $? -ne 0 ]; then
  echo "ERROR: Failed to activate virtual environment. Exiting."
  exit 1
fi
echo "Virtual environment activated."

# Step 2: Install Python dependencies
echo "=== Step 2: Installing dependencies from requirements.txt ==="
if [ -f requirements.txt ]; then
  echo "Installing required packages with pip..."
  pip install --upgrade pip  # upgrade pip to latest to avoid issues
  pip install -r requirements.txt
  if [ $? -ne 0 ]; then
    echo "pip install encountered an error. Retrying with --upgrade for pip and dependencies..."
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt || { 
      echo "ERROR: Failed to install dependencies from requirements.txt. Exiting."; 
      exit 1; 
    }
  fi
  echo "All dependencies installed."
else
  echo "WARNING: requirements.txt not found. Skipping dependency installation."
fi

# Ensure code quality tools are installed (in case they weren't listed in requirements)
echo "Ensuring Black, autoflake, and flake8 are installed..."
if ! command -v black &> /dev/null || ! command -v autoflake &> /dev/null || ! command -v flake8 &> /dev/null; then
  pip install black autoflake flake8
fi

# Step 3: Code cleanup and formatting
echo "=== Step 3: Cleaning up code (autoflake, Black) and linting (flake8) ==="
echo "Running autoflake to remove unused imports/variables..."
autoflake --remove-all-unused-imports --remove-unused-variables -ri .
if [ $? -ne 0 ]; then
  echo "WARNING: autoflake encountered issues. Please check the output above."
fi

echo "Running Black to format the code..."
black .
if [ $? -ne 0 ]; then
  echo "WARNING: Black encountered an error (possibly syntax issues)."
  # Not exiting here to allow flake8 to run and tests to catch issues
fi

echo "Running flake8 for coding style and potential errors..."
flake8
if [ $? -ne 0 ]; then
  echo "NOTE: flake8 reported issues. Review the output above for details."
fi

# (Optional) Check for syntax errors in all Python files
echo "Checking for Python syntax errors with compileall..."
python -m compileall -q .
if [ $? -ne 0 ]; then
  echo "ERROR: Syntax errors detected in the code. Please fix them before running the application."
  deactivate 2>/dev/null
  exit 1
fi
echo "No syntax errors detected."

# Step 4: Environment configuration
echo "=== Step 4: Configuring environment variables ==="
if [ -f .env ]; then
  echo "Loading environment variables from .env file..."
  set -o allexport
  source .env
  set +o allexport
  echo "Environment variables loaded."
else
  echo "No .env file found. Skipping environment variable load."
fi
# (If any config file updates are needed based on environment, do them here.)

# Step 5: Run tests
echo "=== Step 5: Running test suite ==="
if [ -d tests ] || [ -d test ]; then
  echo "Executing tests to verify functionality..."
  TEST_CMD=""
  if command -v pytest &> /dev/null; then
    TEST_CMD="pytest -q"   # -q for concise output (remove if detailed output is preferred)
  else
    # Fall back to unittest if pytest is not available
    TEST_CMD="python -m unittest discover -v"
  fi

  $TEST_CMD
  TEST_RESULT=$?
  if [ $TEST_RESULT -ne 0 ]; then
    echo "WARNING: Some tests failed. Please review the above output for details."
    # Proceeding despite test failures (you may choose to exit here instead)
  else
    echo "All tests passed successfully."
  fi
else
  echo "No tests directory found. Skipping test execution."
fi

# Step 6: Launch the application
echo "=== Step 6: Starting the application ==="
if [ -f app/main.py ]; then
  echo "Running: python app/main.py"
  python app/main.py
elif [ -f main.py ]; then
  echo "Running: python main.py"
  python main.py
else
  echo "ERROR: Application entry point not found. Please adjust the script to use the correct startup command."
  deactivate 2>/dev/null
  exit 1
fi

# Deactivate the virtual environment when the application exits
deactivate 2>/dev/null

echo "=== Setup and Run Script completed ==="
