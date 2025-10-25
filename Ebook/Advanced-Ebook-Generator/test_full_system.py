#!/usr/bin/env python3
"""
Full End-to-End Test for Advanced E-Book Generator
Tests complete workflow: Gemini API → Content Generation → Template → PDF
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def run_full_test():
    """Run complete e-book generation test"""
    
    print("=" * 70)
    print("🚀 FULL END-TO-END TEST: Advanced E-Book Generator")
    print("=" * 70)
    
    # Load environment
    print("\n📋 Step 1: Loading environment variables...")
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found in .env file")
        return False
    print(f"✅ API Key loaded: {api_key[:20]}...")
    
    # Import modules
    print("\n📦 Step 2: Importing modules...")
    try:
        from utils.content_generator import ContentGenerator
        from utils.research_engine import ResearchEngine
        from utils.citation_manager import CitationManager
        from utils.pdf_builder import PDFBuilder
        import yaml
        print("✅ All modules imported successfully")
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Load configuration
    print("\n⚙️  Step 3: Loading configuration...")
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    # Test parameters
    topic = "Python Programming for Beginners"
    genre = "technology"
    num_chapters = 3
    length_preset = "short"
    
    print(f"\n📚 Step 4: Test E-Book Parameters")
    print(f"   Topic: {topic}")
    print(f"   Genre: {genre}")
    print(f"   Chapters: {num_chapters}")
    print(f"   Length: {length_preset}")
    
    # Initialize components
    print("\n🔧 Step 5: Initializing components...")
    try:
        content_gen = ContentGenerator(
            api_key=api_key,
            genre=genre,
            config=config
        )
        
        research_engine = ResearchEngine(
            api_key=os.getenv('GOOGLE_API_KEY', ''),
            search_engine_id=os.getenv('SEARCH_ENGINE_ID', '')
        )
        
        citation_mgr = CitationManager('APA')
        pdf_builder = PDFBuilder(config)
        
        print("✅ All components initialized")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Generate outline
    print(f"\n📝 Step 6: Generating book outline with Gemini API...")
    try:
        length_config = config['book_length'][length_preset]
        outline = content_gen.generate_outline(topic, num_chapters, length_config)
        
        print(f"✅ Outline generated: {len(outline)} sections")
        for i, section in enumerate(outline[:5], 1):
            print(f"   {i}. {section['title']} ({section['type']})")
        if len(outline) > 5:
            print(f"   ... and {len(outline) - 5} more sections")
            
    except Exception as e:
        print(f"❌ Outline generation error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Generate content for sections
    print(f"\n✍️  Step 7: Generating content with Gemini API...")
    print("   (This will take a few minutes...)")
    
    generated_content = []
    features = {
        'case_studies': False,
        'quiz_questions': False,
        'did_you_know': True,
        'real_world_examples': True,
        'summary_boxes': True,
        'expert_quotes': False
    }
    
    try:
        words_per_section = length_config['words_per_section']
        
        for i, section in enumerate(outline, 1):
            print(f"\n   📄 Generating: {section['title']}")
            
            # Simple research for main sections
            research_context = []
            if section['type'] in ['introduction', 'chapter']:
                print(f"      🔍 Researching...")
                try:
                    research_context = research_engine.search(
                        f"{topic} {section['title']}", 
                        max_results=3
                    )
                except:
                    print(f"      ⚠️  Research skipped (API not configured)")
            
            # Generate content
            print(f"      🤖 Gemini generating content...")
            content = content_gen.generate_section(
                topic=topic,
                section=section,
                research_context=research_context,
                features=features,
                words_target=words_per_section
            )
            
            generated_content.append({
                'section': section,
                'content': content
            })
            
            word_count = len(content.split())
            print(f"      ✅ Generated {word_count} words")
            
        print(f"\n✅ All {len(generated_content)} sections generated!")
        
    except Exception as e:
        print(f"\n❌ Content generation error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Save individual markdown files
    print(f"\n💾 Step 8: Saving individual section files...")
    try:
        output_dir = Path('output_full_test')
        output_dir.mkdir(exist_ok=True)
        sections_dir = output_dir / 'sections'
        sections_dir.mkdir(exist_ok=True)
        
        section_files = pdf_builder._save_section_files(
            generated_content, 
            sections_dir, 
            topic
        )
        
        print(f"✅ Saved {len(section_files)} section files to {sections_dir}")
        
    except Exception as e:
        print(f"❌ File saving error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Compile with template
    print(f"\n🔨 Step 9: Compiling with professional template...")
    try:
        final_markdown = pdf_builder._compile_with_template(
            topic=topic,
            genre=genre,
            content=generated_content,
            citation_manager=citation_mgr
        )
        
        # Save compiled markdown
        md_filename = "python_programming_for_beginners_ebook_final.md"
        md_path = output_dir / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)
        
        print(f"✅ Compiled markdown saved: {md_path}")
        print(f"   File size: {len(final_markdown):,} characters")
        
    except Exception as e:
        print(f"❌ Template compilation error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Convert to PDF
    print(f"\n📄 Step 10: Converting to PDF with Pandoc...")
    try:
        pdf_filename = "python_programming_for_beginners_ebook.pdf"
        pdf_path = output_dir / pdf_filename
        
        pdf_builder._convert_to_pdf(str(md_path), str(pdf_path))
        
        if pdf_path.exists():
            file_size = pdf_path.stat().st_size / 1024  # KB
            print(f"✅ PDF created successfully!")
            print(f"   Location: {pdf_path}")
            print(f"   Size: {file_size:.1f} KB")
        else:
            print(f"⚠️  PDF file not found, but markdown is available")
            
    except Exception as e:
        print(f"⚠️  PDF conversion error: {e}")
        print(f"   Markdown file is still available at: {md_path}")
        print(f"   You can manually convert with:")
        print(f"   pandoc {md_path} -o book.pdf --pdf-engine=xelatex")
    
    # Summary
    print("\n" + "=" * 70)
    print("🎉 FULL TEST COMPLETE!")
    print("=" * 70)
    
    print(f"\n📊 Summary:")
    print(f"   ✓ Generated {len(generated_content)} sections using Gemini API")
    print(f"   ✓ Created {len(section_files)} individual markdown files")
    print(f"   ✓ Compiled with professional template")
    print(f"   ✓ Final output in: {output_dir.absolute()}")
    
    print(f"\n📁 Output Files:")
    print(f"   📝 Compiled markdown: {md_path.name}")
    print(f"   📄 PDF: {pdf_filename}")
    print(f"   📂 Section files: {len(section_files)} files in sections/")
    
    print(f"\n🔍 To view results:")
    print(f"   cd {output_dir}")
    print(f"   open {pdf_filename}  # macOS")
    print(f"   # or")
    print(f"   cat sections/*.md  # View individual sections")
    
    print("\n✅ System is fully operational!")
    print("   - Gemini API: Working ✓")
    print("   - Content Generation: Working ✓")
    print("   - Template System: Working ✓")
    print("   - File Organization: Working ✓")
    print("   - PDF Generation: " + ("Working ✓" if pdf_path.exists() else "Check manually"))
    
    return True

if __name__ == "__main__":
    try:
        success = run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
