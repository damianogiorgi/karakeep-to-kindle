#!/bin/bash

# Kindle Bookmarks Node-RED Integration Script
# This script sources the virtual environment, generates HTML compilation, and cleans up
# Perfect for automation with Node-RED or cron jobs

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/kindle_bookmarks.py"
CONFIG_FILE="$SCRIPT_DIR/config.json"
LOG_FILE="$SCRIPT_DIR/kindle_bookmarks.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if virtual environment exists
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        error "Virtual environment not found at $VENV_PATH"
        error "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
        exit 1
    fi
}

# Function to check if config exists
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        error "Configuration file not found at $CONFIG_FILE"
        error "Please run: python setup_config.py"
        exit 1
    fi
}

# Function to activate virtual environment
activate_venv() {
    log "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    # Verify activation
    if [ "$VIRTUAL_ENV" != "$VENV_PATH" ]; then
        error "Failed to activate virtual environment"
        exit 1
    fi
    
    success "Virtual environment activated: $VIRTUAL_ENV"
}

# Function to run the Kindle compilation
run_compilation() {
    log "Starting Kindle bookmarks compilation..."
    
    # Run the Python script with compilation mode and cleanup
    python "$PYTHON_SCRIPT" \
        --config "$CONFIG_FILE" \
        --format html \
        --compilation \
        --cleanup
    
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        success "Kindle compilation completed successfully"
        return 0
    else
        error "Kindle compilation failed with exit code $exit_code"
        return $exit_code
    fi
}

# Function to show recent log entries
show_recent_logs() {
    if [ -f "$LOG_FILE" ]; then
        log "Recent log entries:"
        echo "----------------------------------------"
        tail -n 10 "$LOG_FILE"
        echo "----------------------------------------"
    fi
}

# Function to cleanup old log files (keep last 7 days)
cleanup_logs() {
    log "Cleaning up old log files..."
    find "$SCRIPT_DIR" -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    success "Log cleanup completed"
}

# Main execution function
main() {
    log "=== Kindle Bookmarks Node-RED Script Started ==="
    log "Script directory: $SCRIPT_DIR"
    
    # Pre-flight checks
    check_venv
    check_config
    
    # Activate virtual environment
    activate_venv
    
    # Cleanup old logs first
    cleanup_logs
    
    # Run the compilation
    if run_compilation; then
        success "=== Script completed successfully ==="
        show_recent_logs
        exit 0
    else
        error "=== Script failed ==="
        show_recent_logs
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --dry-run)
        log "DRY RUN MODE - No actual processing will occur"
        check_venv
        check_config
        activate_venv
        python "$PYTHON_SCRIPT" --config "$CONFIG_FILE" --format html --compilation --dry-run
        ;;
    --help|-h)
        echo "Kindle Bookmarks Node-RED Integration Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --dry-run    Show what would be done without actually doing it"
        echo "  --help, -h   Show this help message"
        echo ""
        echo "Environment:"
        echo "  Virtual env: $VENV_PATH"
        echo "  Config file: $CONFIG_FILE"
        echo "  Log file:    $LOG_FILE"
        echo ""
        echo "This script is designed for Node-RED automation and will:"
        echo "  1. Activate the Python virtual environment"
        echo "  2. Generate HTML compilation of Karakeep articles"
        echo "  3. Send the compilation to Kindle via email"
        echo "  4. Clean up generated files"
        echo "  5. Archive processed articles"
        ;;
    *)
        main "$@"
        ;;
esac