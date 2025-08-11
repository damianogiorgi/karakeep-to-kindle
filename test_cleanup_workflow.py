#!/usr/bin/env python3
"""
Test script to demonstrate the complete workflow with cleanup functionality
"""

from kindle_bookmarks import KindleBookmarksProcessor
from pathlib import Path
import tempfile
import os

def test_cleanup_workflow():
    """Test the complete cleanup workflow"""
    
    print("🧪 Testing Cleanup Workflow")
    print("=" * 50)
    
    # Create a temporary config for testing
    processor = KindleBookmarksProcessor()
    
    # Create some test files to simulate the workflow
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create test files
    test_files = []
    for i in range(3):
        test_file = output_dir / f"test_article_{i+1}.epub"
        test_file.write_text(f"Test content for article {i+1}")
        test_files.append(test_file)
        print(f"📄 Created test file: {test_file.name}")
    
    print(f"\n📁 Files before cleanup: {len(list(output_dir.glob('*')))} files")
    
    # Test individual file cleanup
    print("\n🧹 Testing individual file cleanup...")
    for i, test_file in enumerate(test_files[:2]):  # Clean up first 2 files
        result = processor.cleanup_file(test_file)
        print(f"   {'✅' if result else '❌'} Cleanup file {i+1}: {result}")
    
    print(f"\n📁 Files after individual cleanup: {len(list(output_dir.glob('*')))} files")
    
    # Test directory cleanup
    print("\n🧹 Testing directory cleanup...")
    cleaned_count = processor.cleanup_output_directory()
    print(f"   📊 Cleaned up {cleaned_count} remaining files")
    
    print(f"\n📁 Files after directory cleanup: {len(list(output_dir.glob('*')))} files")
    
    print("\n✅ Cleanup workflow test completed!")
    print("\n💡 Usage examples:")
    print("   # With cleanup (recommended for automation)")
    print("   python kindle_bookmarks.py --compilation --format epub --cleanup")
    print("\n   # Without cleanup (default, for manual review)")
    print("   python kindle_bookmarks.py --compilation --format epub")

if __name__ == "__main__":
    test_cleanup_workflow()