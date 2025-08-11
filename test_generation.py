#!/usr/bin/env python3
"""
Test script to generate documents for all articles without archiving
"""

from kindle_bookmarks import KindleBookmarksProcessor
import sys
from pathlib import Path

def test_all_formats():
    """Test document generation for all articles in all formats"""
    
    processor = KindleBookmarksProcessor()
    articles = processor.get_unarchived_articles()
    
    if not articles:
        print("No articles found!")
        return
    
    print(f"Found {len(articles)} articles to process")
    print("=" * 50)
    
    formats_to_test = ['html', 'pdf', 'epub']
    results = {}
    
    for format_type in formats_to_test:
        print(f"\n🔄 Testing {format_type.upper()} generation...")
        results[format_type] = []
        
        for i, article in enumerate(articles, 1):
            title = article.get('content', {}).get('title', 'Untitled')
            print(f"  [{i}/{len(articles)}] Processing: {title[:60]}...")
            
            try:
                filepath = processor.convert_to_document(article, format_type)
                if filepath and filepath.exists():
                    file_size = filepath.stat().st_size
                    results[format_type].append({
                        'title': title,
                        'filepath': filepath,
                        'size': file_size,
                        'success': True
                    })
                    print(f"    ✅ Created: {filepath.name} ({file_size/1024:.1f} KB)")
                else:
                    results[format_type].append({
                        'title': title,
                        'filepath': None,
                        'size': 0,
                        'success': False
                    })
                    print(f"    ❌ Failed to create file")
                    
            except Exception as e:
                results[format_type].append({
                    'title': title,
                    'filepath': None,
                    'size': 0,
                    'success': False,
                    'error': str(e)
                })
                print(f"    ❌ Error: {e}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 GENERATION SUMMARY")
    print("=" * 50)
    
    for format_type, format_results in results.items():
        successful = sum(1 for r in format_results if r['success'])
        total_size = sum(r['size'] for r in format_results if r['success'])
        
        print(f"\n{format_type.upper()} Format:")
        print(f"  ✅ Successful: {successful}/{len(format_results)}")
        print(f"  📁 Total size: {total_size/1024:.1f} KB")
        
        if successful > 0:
            avg_size = total_size / successful
            print(f"  📊 Average size: {avg_size/1024:.1f} KB")
            
        # Show failed ones
        failed = [r for r in format_results if not r['success']]
        if failed:
            print(f"  ❌ Failed articles:")
            for fail in failed:
                error_msg = fail.get('error', 'Unknown error')
                print(f"    - {fail['title'][:40]}... ({error_msg})")
    
    # List all generated files
    output_dir = Path("output")
    if output_dir.exists():
        all_files = list(output_dir.glob("*"))
        print(f"\n📁 All files in output directory ({len(all_files)} total):")
        for file in sorted(all_files):
            size_kb = file.stat().st_size / 1024
            print(f"  - {file.name} ({size_kb:.1f} KB)")

if __name__ == "__main__":
    try:
        test_all_formats()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during testing: {e}")
        sys.exit(1)