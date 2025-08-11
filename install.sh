#!/bin/bash

echo "=== Kindle Bookmarks Installation ==="
echo

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

echo "✅ Python 3 found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment and install dependencies
echo "📦 Installing dependencies..."
source venv/bin/activate

pip install --upgrade pip > /dev/null 2>&1
pip install requests

# Try to install optional dependencies
echo "📦 Installing optional dependencies for PDF/EPUB generation..."
pip install weasyprint 2>/dev/null && echo "✅ weasyprint installed (PDF support)" || echo "⚠️  weasyprint not installed (will use HTML fallback)"
pip install ebooklib 2>/dev/null && echo "✅ ebooklib installed (EPUB support)" || echo "⚠️  ebooklib not installed (will use HTML fallback)"

echo
echo "🎉 Installation complete!"
echo
echo "Next steps:"
echo "1. Run: python setup_config.py (to configure your settings)"
echo "2. Test: source venv/bin/activate && python kindle_bookmarks.py --dry-run"
echo "3. Run: source venv/bin/activate && python kindle_bookmarks.py"
echo
echo "Note: Always activate the virtual environment before running:"
echo "source venv/bin/activate"