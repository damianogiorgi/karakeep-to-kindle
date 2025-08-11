#!/usr/bin/env python3
"""
Test script to verify image caching is working properly
"""

from kindle_bookmarks import KindleBookmarksProcessor
import json

def test_image_caching():
    """Test that images are cached properly and not downloaded multiple times"""
    
    processor = KindleBookmarksProcessor()
    
    # Clear the cache to start fresh
    processor.image_cache = {}
    
    print("🧪 Testing Image Caching")
    print("=" * 50)
    
    # Test downloading the same URL multiple times
    test_url = "https://example.com/test-image.jpg"
    
    print(f"📥 First download of: {test_url}")
    result1 = processor.download_image(test_url)
    print(f"   Cache size after first download: {len(processor.image_cache)}")
    
    print(f"📥 Second download of same URL: {test_url}")
    result2 = processor.download_image(test_url)
    print(f"   Cache size after second download: {len(processor.image_cache)}")
    
    print(f"📊 Results:")
    print(f"   First result: {'Success' if result1 else 'Failed'}")
    print(f"   Second result: {'Success' if result2 else 'Failed'}")
    print(f"   Results identical: {result1 == result2}")
    print(f"   Cache working: {len(processor.image_cache) == 1}")
    
    # Show cache contents
    print(f"\n🗂️  Cache contents:")
    for key, value in processor.image_cache.items():
        value_preview = value[:50] + "..." if value and len(value) > 50 else str(value)
        print(f"   {key}: {value_preview}")

if __name__ == "__main__":
    test_image_caching()