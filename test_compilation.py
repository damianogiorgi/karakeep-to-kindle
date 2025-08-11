#!/usr/bin/env python3
"""
Simple test script for compilation functionality
"""

from kindle_bookmarks import KindleBookmarksProcessor
from pathlib import Path

def test_compilation():
    processor = KindleBookmarksProcessor()
    articles = processor.get_unarchived_articles()
    
    print(f"Found {len(articles)} articles")
    
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Test HTML compilation (simplest)
    print("\n🧪 Testing HTML compilation...")
    try:
        html_file = processor.create_compilation_html(articles, output_dir)
        if html_file and html_file.exists():
            size_mb = html_file.stat().st_size / (1024 * 1024)
            print(f"✅ HTML compilation successful: {html_file.name} ({size_mb:.1f} MB)")
        else:
            print("❌ HTML compilation failed")
    except Exception as e:
        print(f"❌ HTML compilation error: {e}")
    
    # Test EPUB compilation
    print("\n🧪 Testing EPUB compilation...")
    try:
        epub_file = processor.create_compilation_epub(articles, output_dir)
        if epub_file and epub_file.exists():
            size_mb = epub_file.stat().st_size / (1024 * 1024)
            print(f"✅ EPUB compilation successful: {epub_file.name} ({size_mb:.1f} MB)")
        else:
            print("❌ EPUB compilation failed")
    except Exception as e:
        print(f"❌ EPUB compilation error: {e}")
    
    # Test PDF compilation
    print("\n🧪 Testing PDF compilation...")
    try:
        pdf_file = processor.create_compilation_pdf(articles, output_dir)
        if pdf_file and pdf_file.exists():
            size_mb = pdf_file.stat().st_size / (1024 * 1024)
            print(f"✅ PDF compilation successful: {pdf_file.name} ({size_mb:.1f} MB)")
        else:
            print("❌ PDF compilation failed")
    except Exception as e:
        print(f"❌ PDF compilation error: {e}")
    
    # Show all files created
    print(f"\n📁 Files in output directory:")
    for file in sorted(output_dir.glob("*")):
        size_mb = file.stat().st_size / (1024 * 1024)
        print(f"  - {file.name} ({size_mb:.1f} MB)")

if __name__ == "__main__":
    test_compilation()