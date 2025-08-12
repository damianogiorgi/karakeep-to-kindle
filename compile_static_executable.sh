#!/bin/bash

# Static Executable Compilation Script for Kindle Bookmarks
# Creates a standalone native executable with no dependencies for Docker containers

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/venv"
PYTHON_SCRIPT="$SCRIPT_DIR/kindle_bookmarks.py"
OUTPUT_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build"
SPEC_FILE="$SCRIPT_DIR/kindle_bookmarks.spec"
EXECUTABLE_NAME="kindle-bookmarks"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
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

# Function to activate virtual environment
activate_venv() {
    log "Activating virtual environment..."
    source "$VENV_PATH/bin/activate"
    
    if [ "$VIRTUAL_ENV" != "$VENV_PATH" ]; then
        error "Failed to activate virtual environment"
        exit 1
    fi
    
    success "Virtual environment activated: $VIRTUAL_ENV"
}

# Function to install PyInstaller if not present
install_pyinstaller() {
    log "Checking PyInstaller installation..."
    
    if ! python -c "import PyInstaller" 2>/dev/null; then
        log "Installing PyInstaller..."
        pip install pyinstaller
        success "PyInstaller installed successfully"
    else
        success "PyInstaller already installed"
    fi
}

# Function to create PyInstaller spec file
create_spec_file() {
    log "Creating PyInstaller spec file..."
    
    cat > "$SPEC_FILE" << 'EOF'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['kindle_bookmarks.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json.example', '.'),
    ],
    hiddenimports=[
        'requests',
        'weasyprint',
        'ebooklib',
        'six',
        'lxml',
        'html5lib',
        'tinycss2',
        'cssselect2',
        'cairocffi',
        'cffi',
        'pyphen',
        'fonttools',
        'PIL',
        'Pillow',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'scipy',
        'pandas',
        'jupyter',
        'IPython',
        'pytest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='kindle-bookmarks',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
EOF

    success "PyInstaller spec file created: $SPEC_FILE"
}

# Function to compile the executable
compile_executable() {
    log "Starting compilation process..."
    
    # Clean previous builds
    if [ -d "$BUILD_DIR" ]; then
        log "Cleaning previous build directory..."
        rm -rf "$BUILD_DIR"
    fi
    
    if [ -d "$OUTPUT_DIR" ]; then
        log "Cleaning previous output directory..."
        rm -rf "$OUTPUT_DIR"
    fi
    
    # Run PyInstaller
    log "Running PyInstaller compilation..."
    pyinstaller --clean "$SPEC_FILE"
    
    if [ $? -eq 0 ]; then
        success "Compilation completed successfully"
    else
        error "Compilation failed"
        exit 1
    fi
}

# Function to test the executable
test_executable() {
    local executable_path="$OUTPUT_DIR/$EXECUTABLE_NAME"
    
    if [ ! -f "$executable_path" ]; then
        error "Executable not found at $executable_path"
        exit 1
    fi
    
    log "Testing executable..."
    
    # Make executable
    chmod +x "$executable_path"
    
    # Test help command
    if "$executable_path" --help >/dev/null 2>&1; then
        success "Executable test passed"
    else
        error "Executable test failed"
        exit 1
    fi
}

# Function to create Docker-ready wrapper script
create_docker_wrapper() {
    local wrapper_path="$OUTPUT_DIR/run-in-docker.sh"
    
    log "Creating Docker wrapper script..."
    
    cat > "$wrapper_path" << 'EOF'
#!/bin/bash

# Docker wrapper for kindle-bookmarks executable
# This script can be copied into Docker containers for execution

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXECUTABLE="$SCRIPT_DIR/kindle-bookmarks"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Check if executable exists
if [ ! -f "$EXECUTABLE" ]; then
    error "Executable not found at $EXECUTABLE"
    exit 1
fi

# Make sure it's executable
chmod +x "$EXECUTABLE"

# Check if config file exists
if [ ! -f "$SCRIPT_DIR/config.json" ]; then
    error "Configuration file not found at $SCRIPT_DIR/config.json"
    error "Please create config.json based on config.json.example"
    exit 1
fi

log "Starting Kindle Bookmarks compilation (Docker mode)..."

# Run the executable with Docker-friendly settings
"$EXECUTABLE" \
    --config "$SCRIPT_DIR/config.json" \
    --format html \
    --compilation \
    --cleanup

exit_code=$?

if [ $exit_code -eq 0 ]; then
    success "Kindle compilation completed successfully"
else
    error "Kindle compilation failed with exit code $exit_code"
fi

exit $exit_code
EOF

    chmod +x "$wrapper_path"
    success "Docker wrapper created: $wrapper_path"
}

# Function to create deployment package
create_deployment_package() {
    local package_name="kindle-bookmarks-static-$(date +%Y%m%d-%H%M%S).tar.gz"
    local package_path="$SCRIPT_DIR/$package_name"
    
    log "Creating deployment package..."
    
    # Create temporary directory for package contents
    local temp_dir=$(mktemp -d)
    local package_dir="$temp_dir/kindle-bookmarks-static"
    
    mkdir -p "$package_dir"
    
    # Copy executable and related files
    cp "$OUTPUT_DIR/$EXECUTABLE_NAME" "$package_dir/"
    cp "$OUTPUT_DIR/run-in-docker.sh" "$package_dir/"
    cp "$SCRIPT_DIR/config.json.example" "$package_dir/"
    
    # Create README for deployment
    cat > "$package_dir/README.md" << 'EOF'
# Kindle Bookmarks Static Executable

This package contains a standalone executable with no external dependencies.

## Files:
- `kindle-bookmarks` - Main executable
- `run-in-docker.sh` - Docker wrapper script
- `config.json.example` - Configuration template

## Usage:

### 1. Setup Configuration
```bash
cp config.json.example config.json
# Edit config.json with your settings
```

### 2. Run Executable
```bash
# Direct execution
./kindle-bookmarks --help

# Docker-friendly wrapper
./run-in-docker.sh
```

### 3. Docker Integration
Copy all files to your Docker container and run:
```bash
./run-in-docker.sh
```

## Node-RED Integration
Use the `run-in-docker.sh` script in your Node-RED exec nodes:
```
/path/to/run-in-docker.sh
```

The executable includes all Python dependencies and requires no runtime installation.
EOF

    # Create the package
    cd "$temp_dir"
    tar -czf "$package_path" kindle-bookmarks-static/
    
    # Cleanup
    rm -rf "$temp_dir"
    
    success "Deployment package created: $package_name"
    log "Package size: $(du -h "$package_path" | cut -f1)"
}

# Function to show compilation summary
show_summary() {
    local executable_path="$OUTPUT_DIR/$EXECUTABLE_NAME"
    
    log "=== Compilation Summary ==="
    echo "Executable: $executable_path"
    echo "Size: $(du -h "$executable_path" | cut -f1)"
    echo "Docker wrapper: $OUTPUT_DIR/run-in-docker.sh"
    echo ""
    echo "Test the executable:"
    echo "  $executable_path --help"
    echo ""
    echo "For Docker deployment:"
    echo "  1. Copy files from $OUTPUT_DIR/ to your container"
    echo "  2. Create config.json from config.json.example"
    echo "  3. Run: ./run-in-docker.sh"
    echo ""
    echo "Node-RED integration:"
    echo "  Use ./run-in-docker.sh in exec nodes"
}

# Main execution function
main() {
    log "=== Kindle Bookmarks Static Compilation Started ==="
    
    # Pre-flight checks
    check_venv
    
    # Activate virtual environment
    activate_venv
    
    # Install PyInstaller
    install_pyinstaller
    
    # Create spec file
    create_spec_file
    
    # Compile executable
    compile_executable
    
    # Test executable
    test_executable
    
    # Create Docker wrapper
    create_docker_wrapper
    
    # Create deployment package
    create_deployment_package
    
    # Show summary
    show_summary
    
    success "=== Static compilation completed successfully ==="
}

# Handle script arguments
case "${1:-}" in
    --clean)
        log "Cleaning build artifacts..."
        rm -rf "$BUILD_DIR" "$OUTPUT_DIR" "$SPEC_FILE"
        success "Cleanup completed"
        ;;
    --help|-h)
        echo "Kindle Bookmarks Static Compilation Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --clean      Clean build artifacts"
        echo "  --help, -h   Show this help message"
        echo ""
        echo "This script creates a standalone executable with no dependencies"
        echo "Perfect for Docker containers and Node-RED integration"
        ;;
    *)
        main "$@"
        ;;
esac