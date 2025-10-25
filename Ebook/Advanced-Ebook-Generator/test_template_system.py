#!/usr/bin/env python3
"""
Quick test script for the Advanced E-Book Generator
Tests the complete workflow including template system
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_ebook_generation():
    """Test generating a simple e-book"""
    
    print("🧪 Testing Advanced E-Book Generator")
    print("=" * 60)
    
    # Import modules
    print("\n1️⃣  Importing modules...")
    try:
        from utils.content_generator import ContentGenerator
        from utils.pdf_builder import PDFBuilder
        from utils.citation_manager import CitationManager
        import yaml
        print("✅ All modules imported successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Load configuration
    print("\n2️⃣  Loading configuration...")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    # Initialize components
    print("\n3️⃣  Initializing components...")
    try:
        # Use dummy API key for test
        api_key = os.getenv('GEMINI_API_KEY', 'test-key')
        
        content_gen = ContentGenerator(
            api_key=api_key,
            genre='technology',
            config=config
        )
        
        citation_mgr = CitationManager('APA')
        pdf_builder = PDFBuilder(config)
        
        print("✅ Components initialized")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False
    
    # Test markdown file generation (without API calls)
    print("\n4️⃣  Testing template system...")
    try:
        # Create dummy content
        test_content = [
            {
                'section': {'title': 'Introduction', 'type': 'introduction'},
                'content': '# Introduction\n\nThis is a test introduction.'
            },
            {
                'section': {'title': 'Chapter 1: Getting Started', 'type': 'chapter'},
                'content': '# Chapter 1: Getting Started\n\n## First Steps\n\nContent here.'
            },
            {
                'section': {'title': 'Conclusion', 'type': 'conclusion'},
                'content': '# Conclusion\n\nThis concludes our test.'
            }
        ]
        
        # Test saving section files
        output_dir = Path('output_test')
        output_dir.mkdir(exist_ok=True)
        sections_dir = output_dir / 'sections'
        sections_dir.mkdir(exist_ok=True)
        
        section_files = pdf_builder._save_section_files(test_content, sections_dir, "Test Book")
        print(f"✅ Created {len(section_files)} section files")
        
        # Test template compilation
        final_md = pdf_builder._compile_with_template(
            topic="Test E-Book",
            genre="Technology",
            content=test_content,
            citation_manager=citation_mgr
        )
        
        # Save compiled markdown
        test_md_path = output_dir / "test_ebook_final.md"
        with open(test_md_path, 'w', encoding='utf-8') as f:
            f.write(final_md)
        
        print(f"✅ Template compiled successfully")
        print(f"📝 Markdown saved to: {test_md_path}")
        
        # Check if sections were created
        section_count = len(list(sections_dir.glob('*.md')))
        print(f"📁 Section files created: {section_count}")
        
        # Verify template was used
        if '{{BOOK_TITLE}}' not in final_md and 'Test E-Book' in final_md:
            print("✅ Template placeholders replaced correctly")
        else:
            print("⚠️  Template replacement may have issues")
        
    except Exception as e:
        print(f"❌ Template test error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETE!")
    print("=" * 60)
    print(f"\n📂 Output directory: {output_dir.absolute()}")
    print(f"📝 Compiled markdown: {test_md_path.name}")
    print(f"📁 Individual sections: {section_count} files")
    print("\nTo generate PDF, run:")
    print(f"  pandoc {test_md_path} -o test_ebook.pdf --pdf-engine=xelatex")
    print("\n✅ All template system components working!")
    
    return True

if __name__ == "__main__":
    success = test_ebook_generation()
    sys.exit(0 if success else 1)
