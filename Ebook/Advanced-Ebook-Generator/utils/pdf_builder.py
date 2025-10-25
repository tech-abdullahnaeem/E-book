"""
PDF Builder Module
Handles PDF compilation with professional template system
Generates markdown files first, then converts to PDF
"""

import os
import re
from pathlib import Path
from datetime import datetime
import pypandoc


class PDFBuilder:
    """Builds professional PDF from generated content using template system"""
    
    def __init__(self, config: dict):
        """Initialize PDF builder"""
        self.config = config
        self.pdf_settings = config['pdf_settings']
        self.template_path = Path(__file__).parent.parent / "templates" / "ebook_template.md"
    
    def build(
        self,
        topic: str,
        genre: str,
        content: list,
        citation_manager,
        output_dir: str = "output"
    ) -> str:
        """Build the complete PDF using template system
        
        Process:
        1. Load template
        2. Generate all markdown content
        3. Save individual section .md files
        4. Compile into template
        5. Save final compiled .md file
        6. Convert to PDF using Pandoc
        """
        
        # Create output directories
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create sections directory for individual markdown files
        sections_dir = output_path / "sections"
        sections_dir.mkdir(exist_ok=True)
        
        print(f"\n📝 Generating markdown files...")
        
        # Step 1: Generate individual section markdown files
        section_files = self._save_section_files(content, sections_dir, topic)
        
        print(f"✅ Created {len(section_files)} markdown section files")
        
        # Step 2: Compile all content using template
        print(f"\n🔨 Compiling content with template...")
        final_markdown = self._compile_with_template(
            topic, genre, content, citation_manager
        )
        
        # Step 3: Save final compiled markdown
        md_filename = self._slugify(topic) + "_ebook_final.md"
        md_path = output_path / md_filename
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(final_markdown)
        
        print(f"✅ Saved compiled markdown: {md_path}")
        
        # Step 4: Convert to PDF
        pdf_filename = self._slugify(topic) + "_ebook.pdf"
        pdf_path = output_path / pdf_filename
        
        print(f"\n📄 Converting to PDF...")
        try:
            self._convert_to_pdf(str(md_path), str(pdf_path))
            print(f"✅ PDF created successfully: {pdf_path}")
            return str(pdf_path)
        except Exception as e:
            print(f"⚠️  PDF conversion error: {e}")
            print(f"📝 Markdown file available at: {md_path}")
            return str(md_path)
    
    
    def _save_section_files(self, content: list, sections_dir: Path, topic: str) -> list:
        """Save each section as individual markdown file"""
        section_files = []
        
        # Counters for different types
        counters = {
            'front_matter': 0,
            'chapter': 0,
            'back_matter': 0
        }
        
        for item in content:
            section = item['section']
            section_content = item['content']
            section_type = section['type']
            
            # Generate filename based on type
            if section_type == 'front_matter':
                counters['front_matter'] += 1
                filename = f"01_front_{counters['front_matter']:02d}_{self._slugify(section['title'])}.md"
            elif section_type == 'preface':
                filename = f"02_preface.md"
            elif section_type == 'introduction':
                filename = f"03_introduction.md"
            elif section_type == 'chapter':
                counters['chapter'] += 1
                filename = f"04_chapter_{counters['chapter']:02d}_{self._slugify(section['title'])}.md"
            elif section_type == 'conclusion':
                filename = f"05_conclusion.md"
            elif section_type == 'back_matter':
                counters['back_matter'] += 1
                filename = f"06_back_{counters['back_matter']:02d}_{self._slugify(section['title'])}.md"
            else:
                filename = f"99_other_{self._slugify(section['title'])}.md"
            
            # Save file
            file_path = sections_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                # Add title if not in content
                if not section_content.strip().startswith('#'):
                    f.write(f"# {section['title']}\n\n")
                f.write(section_content)
            
            section_files.append({
                'path': file_path,
                'type': section_type,
                'title': section['title']
            })
        
        return section_files
    
    def _compile_with_template(self, topic: str, genre: str, content: list, citation_manager) -> str:
        """Compile content using the professional template"""
        
        # Load template
        if not self.template_path.exists():
            print(f"⚠️  Template not found at {self.template_path}, using basic format")
            return self._compile_markdown(topic, genre, content, citation_manager)
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        
        # Prepare metadata replacements
        current_year = datetime.now().year
        current_date = datetime.now().strftime("%B %Y")
        
        # Generate keywords from topic
        keywords = self._generate_keywords(topic, genre)
        
        # Prepare replacements dictionary
        replacements = {
            '{{BOOK_TITLE}}': topic,
            '{{BOOK_SUBTITLE}}': f"A Comprehensive Guide to {topic}",
            '{{AUTHOR_NAME}}': "AI Ebook Creator",
            '{{PUBLICATION_DATE}}': current_date,
            '{{VERSION}}': "1.0",
            '{{COPYRIGHT_YEAR}}': str(current_year),
            '{{PUBLISHER}}': "Advanced Ebook Generator",
            '{{ISBN}}': "N/A",
            '{{LICENSE}}': "CC BY-NC-SA 4.0",
            '{{LICENSE_FULL}}': self._get_license_text(),
            '{{KEYWORDS}}': keywords,
            '{{BOOK_DESCRIPTION}}': f"A comprehensive {genre} guide exploring {topic} in depth.",
            '{{SUBJECT}}': topic,
            '{{GENRE}}': genre.title(),
            '{{CONTACT_EMAIL}}': "info@example.com",
            '{{WEBSITE}}': "https://example.com",
        }
        
        # Separate content by type
        front_matter_content = []
        main_content_parts = []
        back_matter_content = []
        
        for item in content:
            section = item['section']
            section_content = item['content']
            section_type = section['type']
            formatted = self._format_section(item)
            
            if section_type == 'front_matter':
                front_matter_content.append((section['title'], formatted))
            elif section_type == 'back_matter':
                back_matter_content.append((section['title'], formatted))
            elif section_type == 'preface':
                # Preface goes to front matter template placeholder, not main content
                front_matter_content.append(('Preface', formatted))
            else:
                # Introduction, chapters, conclusion go to main content
                main_content_parts.append(formatted)
        
        # Build front matter sections
        for title, content_text in front_matter_content:
            placeholder = f"{{{{{title.upper().replace(' ', '_').replace('&', 'AND')}}}}}"
            replacements[placeholder] = content_text
        
        # Build back matter sections
        for title, content_text in back_matter_content:
            placeholder = f"{{{{{title.upper().replace(' ', '_').replace('&', 'AND')}}}}}"
            replacements[placeholder] = content_text
        
        # Main content
        replacements['{{MAIN_CONTENT}}'] = "\n\n".join(main_content_parts)
        
        # Remove unused placeholders (set to empty string)
        all_placeholders = [
            '{{DEDICATION}}', '{{EPIGRAPH}}', '{{FOREWORD}}', '{{PREFACE}}', 
            '{{ACKNOWLEDGMENTS}}', '{{EPILOGUE}}', '{{AFTERWORD}}', '{{APPENDICES}}',
            '{{GLOSSARY}}', '{{NOTES_REFERENCES}}', '{{BIBLIOGRAPHY}}', '{{INDEX}}',
            '{{ABOUT_AUTHOR}}', '{{OTHER_BOOKS}}'
        ]
        
        for placeholder in all_placeholders:
            if placeholder not in replacements:
                replacements[placeholder] = ""
        
        # Apply all replacements
        compiled_content = template
        for placeholder, value in replacements.items():
            compiled_content = compiled_content.replace(placeholder, value)
        
        return compiled_content
    
    def _compile_markdown(self, topic: str, genre: str, content: list, citation_manager) -> str:
        """Compile all content into markdown with proper ordering (fallback method)"""
        
        # Generate metadata header
        metadata = self._generate_metadata(topic, genre)
        
        # Separate content by type
        front_matter = []
        main_content = []
        back_matter = []
        
        for item in content:
            section_type = item['section']['type']
            if section_type == 'front_matter':
                front_matter.append(item)
            elif section_type == 'back_matter':
                back_matter.append(item)
            else:
                main_content.append(item)
        
        # Compile sections in order: front matter -> main content -> back matter
        sections_md = ""
        
        # Add front matter
        for item in front_matter:
            sections_md += self._format_section(item)
        
        # Add main content
        for item in main_content:
            sections_md += self._format_section(item)
        
        # Add back matter
        for item in back_matter:
            sections_md += self._format_section(item)
        
        # Combine everything
        complete_md = metadata + "\n\n" + sections_md
        
        return complete_md
    
    def _format_section(self, item: dict) -> str:
        """Format a single section"""
        section = item['section']
        section_content = item['content']
        section_type = section['type']
        
        formatted = ""
        
        # Add page break before chapters (ALWAYS)
        if section_type == 'chapter':
            formatted += "\\newpage\n\n"
        
        # Add section heading with appropriate formatting
        if not section_content.strip().startswith('#'):
            # Front matter and back matter should be unnumbered
            if section_type in ['front_matter', 'back_matter']:
                formatted += f"# {section['title']} {{.unnumbered}}\n\n"
            elif section_type in ['preface', 'introduction', 'conclusion']:
                formatted += f"# {section['title']} {{.unnumbered}}\n\n"
            elif section_type == 'chapter':
                formatted += f"# {section['title']}\n\n"
            else:
                formatted += f"## {section['title']}\n\n"
        
        # Process content for special formatting (quizzes, did you know boxes)
        # Pass section title so we can skip Preface/Prologue
        processed_content = self._format_special_boxes(section_content, section['title'])
        formatted += processed_content + "\n\n"
        
        return formatted
    
    def _format_special_boxes(self, content: str, section_name: str = "") -> str:
        """Convert special content to fenced divs for Pandoc Lua filter processing
        
        ONLY apply to chapter content, not to Preface or Prologue
        """
        
        # Skip special formatting for Preface and Prologue
        if "Preface" in section_name or "Prologue" in section_name or "prologue" in section_name.lower():
            return content
        
        # Convert quiz sections to fenced divs
        content = re.sub(
            r'##\s*📝\s*Chapter Quiz\s*\n(.*?)(?=\n##|\n---|\Z)',
            r'::: quiz\n\n\1\n:::\n',
            content,
            flags=re.DOTALL
        )
        
        # Convert "Did You Know?" to fenced divs
        content = re.sub(
            r'\n\*\*Did You Know\?\*\*\s*\n((?:(?!\n\*\*).)*?)(?=\n\n|\Z)',
            r'\n::: didyouknow\n\n\1\n:::\n\n',
            content,
            flags=re.DOTALL
        )
        
        # Convert "Key Takeaway" to fenced divs
        content = re.sub(
            r'\*\*Key Takeaways?:\*\*\s*\n((?:(?!\n\*\*).)*?)(?=\n\n|\Z)',
            r'::: keytakeaway\n\n\1\n:::\n\n',
            content,
            flags=re.DOTALL
        )
        
        # Convert Case Study to fenced divs
        content = re.sub(
            r'\*\*Case Study:\s*(.*?)\*\*\s*\n\n((?:(?!\n\*\*Case Study).)*?)(?=\n\n\*\*|\n##|\Z)',
            r'::: casestudy\n\n**\1**\n\n\2\n:::\n\n',
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _generate_metadata(self, topic: str, genre: str) -> str:
        """Generate YAML metadata for PDF"""
        
        current_date = datetime.now().strftime("%B %d, %Y")
        
        metadata = f"""---
title: "{topic.title()}"
subtitle: "A Comprehensive Guide"
author: "AI Ebook Generator"
date: "{current_date}"
lang: en-US

# PDF Settings
documentclass: book
classoption: [11pt, oneside, openany]
geometry: [margin={self.pdf_settings['margin']}, paperwidth={self.pdf_settings['page_size'].split('x')[0].strip()}, paperheight={self.pdf_settings['page_size'].split('x')[1].strip()}]
mainfont: "{self.pdf_settings['font']['main']}"
sansfont: "{self.pdf_settings['font']['sans']}"
monofont: "{self.pdf_settings['font']['mono']}"

# Table of Contents
toc: true
toc-depth: {self.pdf_settings['toc_depth']}
number-sections: true

# Colors and Links
linkcolor: blue
urlcolor: blue
toccolor: black
colorlinks: true

# Metadata
keywords: [{genre}, ebook, AI-generated, comprehensive guide]
subject: "{topic}"
---

<!-- Title Page -->
\\begin{{titlepage}}
\\begin{{center}}

\\vspace*{{2cm}}

{{\\Huge\\bfseries {topic.title()}}}

\\vspace{{0.5cm}}

{{\\LARGE A Comprehensive Guide}}

\\vspace{{2cm}}

{{\\Large\\itshape AI Ebook Generator}}

\\vfill

{{\\large {current_date}}}

\\end{{center}}
\\end{{titlepage}}

\\newpage

<!-- Copyright Page -->
## Copyright Notice

**Copyright © {datetime.now().year} AI Ebook Generator**

This e-book was generated using advanced AI technology. All rights reserved.

### License

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

\\newpage

<!-- Table of Contents -->
# Table of Contents

<!-- Pandoc generates TOC automatically when `toc: true` is set. -->

\\newpage
"""
        
        return metadata
    
    def _convert_to_pdf(self, md_path: str, pdf_path: str):
        """Convert markdown to PDF using pandoc with Lua filter"""
        
        # Get path to Lua filter
        filter_path = Path(__file__).parent.parent / 'filters' / 'boxify.lua'
        
        try:
            # Try with primary engine
            pypandoc.convert_file(
                md_path,
                'pdf',
                outputfile=pdf_path,
                extra_args=[
                    f'--pdf-engine={self.pdf_settings["default_engine"]}',
                    '--toc',
                    f'--toc-depth={self.pdf_settings["toc_depth"]}',
                    '-N',
                    '--highlight-style=tango',
                    '-V', f'geometry:margin={self.pdf_settings["margin"]}',
                    '-V', 'documentclass=book',
                    '-V', 'linkcolor=blue',
                    '-V', 'urlcolor=blue',
                    f'--lua-filter={filter_path}'
                ]
            )
        except Exception as e:
            print(f"Error with {self.pdf_settings['default_engine']}, trying {self.pdf_settings['fallback_engine']}...")
            
            # Try with fallback engine
            pypandoc.convert_file(
                md_path,
                'pdf',
                outputfile=pdf_path,
                extra_args=[
                    f'--pdf-engine={self.pdf_settings["fallback_engine"]}',
                    '--toc',
                    f'--toc-depth={self.pdf_settings["toc_depth"]}',
                    '-N',
                    f'--lua-filter={filter_path}'
                ]
            )
    
    
    def _generate_keywords(self, topic: str, genre: str) -> str:
        """Generate keywords for metadata"""
        # Extract key words from topic
        words = topic.split()
        keywords = [w.lower() for w in words if len(w) > 3]
        keywords.append(genre.lower())
        return ", ".join(keywords[:10])  # Limit to 10 keywords
    
    def _get_license_text(self) -> str:
        """Get full license text"""
        return """This work is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**.

You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit
- **NonCommercial** — You may not use the material for commercial purposes
- **ShareAlike** — If you remix, transform, or build upon the material, you must distribute your contributions under the same license

For the full license text, visit: https://creativecommons.org/licenses/by-nc-sa/4.0/"""
    
    def _slugify(self, text: str) -> str:
        """Convert text to filename-safe slug"""
        text = re.sub(r'[^\w\s-]', '', text.lower())
        text = re.sub(r'[\s_-]+', '_', text).strip('_')
        return text
