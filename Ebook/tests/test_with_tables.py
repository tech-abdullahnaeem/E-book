#!/usr/bin/env python3
"""
Quick test script to generate ebook with tables
"""

import os
import sys
import time
import json
import google.generativeai as genai

# Configure Gemini
genai.configure(api_key="AIzaSyBW3GE8dH4UexMymdK8FatlS-AsE_9JLB8")

def generate_outline(topic):
    """Generate a 5-section outline"""
    prompt = (
        f"You are an expert author creating an ebook outline about '{topic}'.\n"
        f"Create a JSON array of exactly 5 sections in this order:\n"
        f"1. Abstract (overview)\n"
        f"2-4. Three main chapters\n"
        f"5. Conclusion\n\n"
        f"Format: [\"Abstract: ...\", \"Chapter 1: ...\", \"Chapter 2: ...\", \"Chapter 3: ...\", \"Conclusion: ...\"]\n"
        f"Return ONLY the JSON array, no other text."
    )
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        time.sleep(7.5)
        
        # Parse response
        text = response.text.strip()
        if text.startswith('```'):
            text = text.split('\n', 1)[1].rsplit('\n', 1)[0]
        
        outline = json.loads(text)
        return outline
    except Exception as e:
        print(f"ERROR: {e}")
        return [
            f"Abstract: Introduction to {topic}",
            f"Chapter 1: Understanding {topic}",
            f"Chapter 2: Applications of {topic}",
            f"Chapter 3: Future of {topic}",
            f"Conclusion: Final Thoughts on {topic}"
        ]

def write_section_with_tables(section_title, topic):
    """Generate content with tables where appropriate"""
    prompt = (
        f"Write a detailed, professional section for '{section_title}' in an ebook about '{topic}'.\n\n"
        
        f"CONTENT REQUIREMENTS:\n"
        f"- Write 4-6 substantial, well-structured paragraphs\n"
        f"- Include **bold** for key terms and *italics* for emphasis\n"
        f"- Use academic yet accessible tone with real-world examples\n"
        f"- Do NOT use headings (# or ##) since title is already added\n\n"
        
        f"TABLE REQUIREMENTS (CRITICAL - Include 2-3 professional tables):\n"
        f"- Create information-dense tables that enhance understanding\n"
        f"- Use proper Markdown format with clean alignment:\n\n"
        
        f"  Example Format:\n"
        f"  | Column 1 (Text) | Column 2 (Category) | Column 3 (Number) |\n"
        f"  |:----------------|:-------------------:|------------------:|\n"
        f"  | Left aligned    | Center aligned      | Right aligned     |\n"
        f"  | Data row 1      | Category A          | 95%               |\n"
        f"  | Data row 2      | Category B          | 87%               |\n\n"
        
        f"  Table: Professional caption explaining what the table shows\n\n"
        
        f"- ALIGNMENT RULES:\n"
        f"  * Text/descriptions → Left align (|:---)\n"
        f"  * Categories/status → Center align (|:---:)\n"
        f"  * Numbers/percentages/dates → Right align (---:|)\n"
        f"- Include 4-8 meaningful rows per table\n"
        f"- Use concise cell content (2-5 words per cell)\n"
        f"- Tables should: compare features, show statistics, present timelines, or list specifications\n"
        f"- Add descriptive captions that explain the table's purpose\n\n"
        
        f"TABLE IDEAS FOR THIS TOPIC:\n"
        f"1. Feature comparison table (Traditional vs AI-powered)\n"
        f"2. Performance metrics table (Accuracy rates, speeds, costs)\n"
        f"3. Timeline table (Development stages, adoption dates)\n"
        f"4. Classification table (Types, categories, applications)\n\n"
        
        f"FINAL TOUCHES:\n"
        f"- End with bullet points summarizing key takeaways\n"
        f"- Ensure tables are integrated naturally into the narrative\n"
        f"- Make content informative, accurate, and engaging"
    )
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        time.sleep(7.5)
        return response.text
    except Exception as e:
        return f"[Error generating content: {e}]"

def main():
    topic = "Artificial Intelligence in Healthcare"
    print(f"\n{'='*70}")
    print(f"Testing Ebook Generator with Tables")
    print(f"Topic: {topic}")
    print(f"{'='*70}\n")
    
    # Generate outline
    print("📋 Generating outline...")
    outline = generate_outline(topic)
    print(f"✓ Created {len(outline)} sections")
    
    # Generate one sample section with tables
    section_title = outline[1]  # First chapter
    print(f"\n📝 Generating sample chapter with tables: '{section_title}'")
    
    content = write_section_with_tables(section_title, topic)
    
    # Save to test file
    test_file = "test_chapter_with_tables.md"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(f"# {section_title}\n\n")
        f.write(content)
    
    print(f"\n✓ Saved to: {test_file}")
    
    # Check for tables
    table_count = content.count('|')
    has_tables = '|' in content and '---' in content
    
    print(f"\n{'='*70}")
    print(f"RESULTS:")
    print(f"  - File size: {len(content)} characters")
    print(f"  - Contains tables: {'YES ✓' if has_tables else 'NO ✗'}")
    print(f"  - Pipe characters: {table_count}")
    print(f"{'='*70}\n")
    
    # Show preview
    print("Preview of generated content:\n")
    print(content[:500] + "...\n")

if __name__ == "__main__":
    main()
