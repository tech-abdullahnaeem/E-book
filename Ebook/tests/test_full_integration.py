#!/usr/bin/env python3
"""
Quick end-to-end test of the improved ebook generator with tables
"""

import subprocess
import sys

def test_ebook_generation():
    print("=" * 70)
    print("TESTING IMPROVED EBOOK GENERATOR WITH TABLES")
    print("=" * 70)
    print()
    
    # Topic that will generate great tables
    topic = "Cloud Computing Platforms"
    
    print(f"📚 Topic: {topic}")
    print(f"📝 This topic should generate comparison tables, pricing tables, etc.")
    print()
    print("🚀 Starting generation...")
    print()
    
    # Run the main script with automated input
    try:
        process = subprocess.Popen(
            [sys.executable, 'ebook_agent.py'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd='/Users/abdullah/Desktop/Techinoid/Ebook'
        )
        
        # Provide automated input
        output, _ = process.communicate(input=f'{topic}\ny\n', timeout=120)
        
        print(output)
        
        if process.returncode == 0:
            print()
            print("=" * 70)
            print("✅ SUCCESS! Ebook generated with improved tables")
            print("=" * 70)
            print()
            print("📄 Generated files:")
            print("   - book.md (complete ebook)")
            print("   - cloud_computing_platforms_ebook.pdf (final PDF)")
            print("   - chapters/01_abstract.md through 05_conclusion.md")
            print()
            print("🔍 Check the PDF for professional tables with:")
            print("   - Proper alignment (text left, categories center, numbers right)")
            print("   - 4-8 rows per table")
            print("   - Descriptive captions")
            print("   - Clean, professional formatting")
        else:
            print()
            print("❌ Generation failed")
            
    except subprocess.TimeoutExpired:
        print("⏱️ Test timed out (taking longer than 2 minutes)")
        process.kill()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_ebook_generation()
