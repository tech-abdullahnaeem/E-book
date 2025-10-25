#!/usr/bin/env python3
"""
Recompile existing sections with updated template (TOC fixes + styled boxes)
"""
import pypandoc
import re
from pathlib import Path
from datetime import datetime

def escape_latex_in_tables(content: str) -> str:
    """Escape special LaTeX characters (&, %, #) in markdown tables"""
    lines = content.split('\n')
    result = []
    in_table = False
    
    for line in lines:
        # Detect if we're in a table (lines with |)
        if '|' in line and not line.strip().startswith('```'):
            in_table = True
            # Escape & % and # in table cells, but not the | separators
            # Split by |, escape each cell, rejoin
            parts = line.split('|')
            escaped_parts = []
            for part in parts:
                # Escape &, %, and # characters for LaTeX
                escaped = part.replace('&', '\\&').replace('%', '\\%').replace('#', '\\#')
                escaped_parts.append(escaped)
            line = '|'.join(escaped_parts)
        elif in_table and line.strip() == '':
            in_table = False
        
        result.append(line)
    
    return '\n'.join(result)

def format_special_boxes(content: str, section_name: str = "") -> str:
    """Format special content boxes (quizzes, did you know, summaries)
    
    ONLY apply to chapter content, not to Preface or Prologue
    """
    
    # Skip special formatting for Preface and Prologue
    if "Preface" in section_name or "Prologue" in section_name or "prologue" in section_name.lower():
        return content
    
    # Format quiz sections - match the actual format in content
    # Pattern: "## 📝 Chapter Quiz" followed by content until next ## or end
    content = re.sub(
        r'##\s*📝\s*Chapter Quiz\s*\n(.*?)(?=\n##|\n---|\Z)',
        r'::: quiz\n\1\n:::',
        content,
        flags=re.DOTALL
    )
    
    # Format "Did You Know?" boxes - match the actual format
    # Pattern: "**Did You Know?**" on its own line, followed by content until next paragraph
    content = re.sub(
        r'\*\*Did You Know\?\*\*\s*\n(.*?)(?=\n\n[A-Z]|\n\n\*\*|\n##|\Z)',
        r'::: didyouknow\n\1\n:::',
        content,
        flags=re.DOTALL
    )
    
    # Format Summary/Key Takeaway boxes
    # Pattern: "**Key Takeaway:**" followed by content
    content = re.sub(
        r'\*\*Key Takeaway:\*\*\s*\n?(.*?)(?=\n\n[A-Z]|\n\n\*\*|\n##|\Z)',
        r'::: keytakeaway\n\1\n:::',
        content,
        flags=re.DOTALL
    )
    
    # Format Case Study boxes
    # Pattern: "**Case Study:" followed by title and content
    content = re.sub(
        r'\*\*Case Study:\s*(.*?)\*\*\s*\n(.*?)(?=\n\n[A-Z]|\n\n\*\*|\n##|\Z)',
        r'::: casestudy\n**\1**\n\n\2\n:::',
        content,
        flags=re.DOTALL
    )
    
    return content

def add_chapter_page_breaks(content: str) -> str:
    """Add \\newpage before each chapter heading"""
    # Match "## Chapter N:" or "# Chapter N:"
    content = re.sub(
        r'(^|\n)(#{1,2}\s+Chapter\s+\d+:)',
        r'\1\\newpage\n\n\2',
        content,
        flags=re.MULTILINE
    )
    return content

def main():
    # Paths
    base_dir = Path(__file__).parent
    sections_dir = base_dir / 'output' / 'sections'
    output_dir = base_dir / 'output'
    template_path = base_dir / 'templates' / 'ebook_template.md'
    
    print("🔄 Recompiling existing content with updated template...")
    print(f"📂 Sections directory: {sections_dir}")
    print(f"📂 Output directory: {output_dir}")
    
    # Check sections exist
    if not sections_dir.exists():
        print("❌ No sections directory found!")
        return
    
    # Load template
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    # Metadata
    topic = "Artificial Intelligence"
    genre = "technology"
    current_year = datetime.now().year
    current_date = datetime.now().strftime("%B %Y")
    
    # Load all section files
    section_files = sorted(sections_dir.glob('*.md'))
    print(f"📄 Found {len(section_files)} section files\n")
    
    # Organize sections by type
    front_matter = {}
    back_matter = {}
    main_content = []  # List of tuples: (section_name, content)
    
    for file in section_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        filename = file.stem
        
        if filename.startswith('01_front_'):
            section_name = filename.split('_', 2)[2].upper().replace('_', '_')
            front_matter[section_name] = content
            print(f"  ✓ Front matter: {section_name}")
        elif filename.startswith('06_back_'):
            section_name = filename.split('_', 2)[2].upper().replace('_', '_')
            back_matter[section_name] = content
            print(f"  ✓ Back matter: {section_name}")
        else:
            # Main content (preface, intro, chapters, conclusion)
            # Extract section name from filename for filtering
            section_type = filename.split('_')[0] if '_' in filename else filename
            main_content.append((filename, content))
            print(f"  ✓ Main content: {file.name[:50]}...")
    
    # Prepare replacements
    replacements = {
        '{{BOOK_TITLE}}': topic,
        '{{BOOK_SUBTITLE}}': "From Turing's Dream to Deep Learning's Reality",
        '{{AUTHOR_NAME}}': "AI Ebook Creator",
        '{{PUBLICATION_DATE}}': current_date,
        '{{VERSION}}': "1.0",
        '{{COPYRIGHT_YEAR}}': str(current_year),
        '{{PUBLISHER}}': "Advanced Ebook Generator",
        '{{ISBN}}': "N/A",
        '{{LICENSE}}': "CC BY-NC-SA 4.0",
        '{{LICENSE_FULL}}': "This work is licensed under Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.",
        '{{KEYWORDS}}': "artificial intelligence, machine learning, AI, technology",
        '{{BOOK_DESCRIPTION}}': f"A comprehensive {genre} guide exploring {topic} in depth.",
        '{{SUBJECT}}': topic,
        '{{GENRE}}': genre.title(),
        '{{CONTACT_EMAIL}}': "info@example.com",
        '{{WEBSITE}}': "https://example.com",
    }
    
    # Add front matter sections
    for key, content in front_matter.items():
        replacements[f'{{{{{key}}}}}'] = content
    
    # Add back matter sections
    for key, content in back_matter.items():
        replacements[f'{{{{{key}}}}}'] = content
    
    # Add main content
    main_content_combined_parts = []
    for filename, content in main_content:
        formatted_content = format_special_boxes(content, filename)
        main_content_combined_parts.append(formatted_content)
    
    main_content_combined = "\n\n".join(main_content_combined_parts)
    
    # Apply special formatting
    print(f"\n🎨 Applying special formatting...")
    main_content_combined = escape_latex_in_tables(main_content_combined)
    main_content_combined = add_chapter_page_breaks(main_content_combined)
    
    replacements['{{MAIN_CONTENT}}'] = main_content_combined
    
    # Remove unused placeholders
    all_placeholders = [
        '{{DEDICATION}}', '{{EPIGRAPH}}', '{{FOREWORD}}', '{{PREFACE}}',
        '{{ACKNOWLEDGMENTS}}', '{{EPILOGUE}}', '{{AFTERWORD}}', '{{APPENDICES}}',
        '{{GLOSSARY}}', '{{NOTES_REFERENCES}}', '{{BIBLIOGRAPHY}}', '{{INDEX}}',
        '{{ABOUT_AUTHOR}}', '{{OTHER_BOOKS}}'
    ]
    
    for placeholder in all_placeholders:
        if placeholder not in replacements:
            replacements[placeholder] = ""
    
    # Apply replacements
    compiled_content = template
    for placeholder, value in replacements.items():
        compiled_content = compiled_content.replace(placeholder, value)
    
    # Save final markdown
    md_filename = "artificial_intelligence_ebook_recompiled_final.md"
    md_path = output_dir / md_filename
    
    print(f"\n💾 Saving compiled markdown...")
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(compiled_content)
    
    print(f"✅ Saved: {md_path}")
    
    # Convert to PDF
    print(f"\n📕 Converting to PDF...")
    pdf_filename = "artificial_intelligence_ebook_recompiled.pdf"
    pdf_path = output_dir / pdf_filename
    
    # Get absolute path to Lua filter
    filter_path = base_dir / 'filters' / 'boxify.lua'
    
    try:
        pypandoc.convert_file(
            str(md_path),
            'pdf',
            outputfile=str(pdf_path),
            extra_args=[
                '--pdf-engine=xelatex',
                '--toc',
                '--toc-depth=2',
                '--number-sections',
                f'--metadata=title:{topic}',
                '--standalone',
                f'--lua-filter={filter_path}'
            ]
        )
        print(f"✅ PDF created: {pdf_path}")
        
        # Get file size
        size_kb = pdf_path.stat().st_size / 1024
        print(f"📊 Size: {size_kb:.1f} KB")
        
    except Exception as e:
        print(f"❌ PDF conversion error: {e}")
        return
    
    print(f"\n🎯 Applied fixes:")
    print("   ✓ TOC depth reduced (3 → 2)")
    print("   ✓ Front/back matter marked as {.unnumbered}")
    print("   ✓ Fenced divs + Lua filter for styled boxes")
    print("   ✓ Blue boxes for quizzes")
    print("   ✓ Yellow boxes for 'Did You Know?'")
    print("   ✓ Green boxes for summaries")
    print("   ✓ Purple boxes for case studies")
    print("   ✓ No LaTeX escaping issues")
    print("   ✓ Chapter page breaks")
    print(f"\n✨ Done! Check the PDF to verify all fixes.")

if __name__ == '__main__':
    main()
