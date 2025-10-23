import os
import re
import json
import requests
import pypandoc
import time
import google.generativeai as genai
from googleapiclient.discovery import build

# --- 1. SETUP: PASTE YOUR KEYS HERE ---
GOOGLE_API_KEY = "AIzaSyDu2X02nDnt1vUeLeu86qhIc9O6yicuO5A"
GEMINI_API_KEY = "AIzaSyCLPZ_mJgjezYGVGnCW2EcMg25yBD1QAIw"
SEARCH_ENGINE_ID = "65db4755016cc4d9c"

# Initialize the clients
genai.configure(api_key=GEMINI_API_KEY)
search_service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)


# --- 2. HELPER FUNCTIONS (The "Sub-Agents") ---

def slugify(text):
    """
    Cleans up a string to be a valid filename.
    e.g., "Chapter 1: The Beginning" -> "chapter_1_the_beginning"
    """
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[\s_-]+', '_', text).strip('_')
    return text

def generate_outline(topic):
    """
    Step 1: The Architect
    Takes a topic and returns a list of section titles.
    """
    print(f"-> 1. Architect: Generating outline for '{topic}'...")
    prompt = (
        f"You are a professional author. Create an outline for the ebook topic '{topic}' with exactly these sections:\n"
        f"1. Abstract\n"
        f"2. Chapter 1: [Main topic area 1]\n"
        f"3. Chapter 2: [Main topic area 2]\n"
        f"4. Chapter 3: [Main topic area 3]\n"
        f"5. Conclusion\n"
        f"Return ONLY a JSON array of strings with these exact section titles, properly named for the topic."
    )
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        response = model.generate_content(prompt)
        time.sleep(7.5)  # Rate limit: 60s/8req = 7.5s per request
        
        outline_json = response.text.strip()
    except Exception as e:
        print(f"ERROR generating outline: {e}")
        return ["Abstract", "Chapter 1: Introduction", "Chapter 2: Main Content", "Chapter 3: Advanced Topics", "Conclusion"]
    
    outline_json = outline_json
    print(f"Outline response: {outline_json}")  # Debug
    # Remove markdown code block if present
    if outline_json.startswith('```json'):
        outline_json = outline_json[7:]
    if outline_json.endswith('```'):
        outline_json = outline_json[:-3]
    outline_json = outline_json.strip()
    # Assuming it returns JSON, parse it
    try:
        outline = json.loads(outline_json)
        return outline
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        # Try to extract list from text
        import re
        # Assume it's a list in text
        lines = outline_json.split('\n')
        outline = [line.strip('- "').strip() for line in lines if line.strip()]
        return outline

# NOTE: Google Search functionality removed for now
# Re-enable if you want to add research context to content generation

def write_section(section_title, context, topic, is_conclusion=False, is_abstract=False):
    """
    Step 2b: The Writer
    Writes a single section of the ebook given a title and research.
    """
    print(f"--> 2b. Writer: Writing section '{section_title}'...")
    
    # Special prompt for abstract (max 9 lines, ~150-200 words)
    if is_abstract:
        prompt = (
            f"You are an expert author. Write a concise abstract for an ebook about '{topic}'.\n"
            f"The abstract should:\n"
            f"1. Provide a brief overview of what the ebook covers\n"
            f"2. Highlight the key topics and main themes\n"
            f"3. Explain the value readers will gain\n"
            f"4. Be written in a professional, engaging tone\n"
            f"IMPORTANT: Keep it SHORT - maximum 9 lines or 150-200 words.\n"
            f"Write as a single, well-structured paragraph.\n"
            f"Do NOT use headings, bullet points, or section breaks."
        )
    # Special prompt for conclusion
    elif is_conclusion:
        prompt = (
            f"You are an expert author. Write a compelling conclusion for an ebook about '{topic}'.\n"
            f"The conclusion should:\n"
            f"1. Summarize the key points covered in the book\n"
            f"2. Emphasize the importance of {topic}\n"
            f"3. Provide forward-looking perspective or call to action\n"
            f"4. End on an inspiring and memorable note\n"
            f"Write 4-5 well-structured paragraphs. Use professional, engaging tone.\n"
            f"Do NOT use headings (like #) since this is just the conclusion section."
        )
    else:
        prompt = (
            f"You are an expert author writing an authoritative ebook about '{topic}'.\n"
            f"Write a comprehensive, engaging, and detailed section for: '{section_title}'.\n"
            f"Requirements:\n"
            f"- Write 4-6 substantial paragraphs with clear topic sentences\n"
            f"- Include specific facts, examples, and explanations\n"
            f"- Use an academic yet accessible tone\n"
            f"- Add **bold** for key terms and *italics* for emphasis\n\n"
            
            f"TABLE GUIDELINES (Optional - Include ONLY if truly beneficial):\n"
            f"- Add tables ONLY when they genuinely enhance understanding (comparisons, statistics, timelines)\n"
            f"- If the content is better explained through narrative, skip tables\n"
            f"- When you do include a table:\n"
            f"  * Use proper Markdown format with pipe (|) separators\n"
            f"  * Include clear header row with concise column names\n"
            f"  * Apply proper alignment: |:--- (left) | :---: (center) | ---:| (right)\n"
            f"  * Include 4-8 data rows maximum\n"
            f"  * Keep cell content concise (2-5 words)\n"
            f"  * Add caption: Table: Descriptive explanation\n"
            f"- Good table candidates: feature comparisons, performance metrics, timelines, specifications\n"
            f"- Skip tables for: philosophical discussions, narrative content, conceptual explanations\n\n"
            
            f"FORMATTING STANDARDS:\n"
            f"- Include bullet points or numbered lists for key takeaways\n"
            f"- Ensure accuracy and depth of coverage\n"
            f"- Do NOT use headings (like #) since section title is already added\n"
            f"- Make it informative and well-researched in tone"
        )
    
    # Retry logic for transient errors such as quota/429
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            model = genai.GenerativeModel('gemini-2.0-flash-exp')
            response = model.generate_content(prompt)
            time.sleep(7.5)  # Rate limit: 60s/8req = 7.5s per request
            return response.text
        except Exception as e:
            err = str(e)
            print(f"     ERROR generating content (attempt {attempt}/{max_retries}): {err}")
            # If it's a quota or rate limit error, wait the suggested backoff if present, else wait a default and retry
            if attempt < max_retries and ("429" in err or "quota" in err.lower() or "rate limit" in err.lower()):
                backoff = 22  # default backoff seconds for quota issues
                # Try to extract a numeric retry delay if present in the message
                m = re.search(r'retry in\s*(\d+\.?\d*)s', err)
                if m:
                    try:
                        backoff = max(7.5, float(m.group(1)))
                    except Exception:
                        pass
                print(f"     Retrying in {int(backoff)} seconds...")
                time.sleep(backoff)
                continue
            else:
                break

    return f"[Content generation failed for {section_title}]"

# NOTE: Image generation functionality removed for now
# Re-enable if you want to add images to ebook sections


# --- 3. THE MAIN WORKFLOW ---

def main():
    topic = input("Enter the ebook topic: ").strip()
    
    # Validate topic
    if not topic or len(topic) < 3:
        print("ERROR: Please enter a valid topic (at least 3 characters)")
        return
    
    print(f"\n✓ Topic: {topic}")
    confirm = input("Generate ebook for this topic? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Create a directory to hold the markdown chapters
    os.makedirs("chapters", exist_ok=True)
    
    # Get the outline
    print("\n" + "="*60)
    print("PHASE 1: GENERATING OUTLINE")
    print("="*60)
    try:
        outline = generate_outline(topic)
        print(f"✓ Generated outline with {len(outline)} sections")
    except Exception as e:
        print(f"Failed to generate outline: {e}")
        return

    md_files_list = [] # To store the paths of all our .md files
    
    # NOTE: We don't create separate cover/TOC files anymore
    # The template has these built-in, we'll just generate content sections

    # Start the content generation loop
    print("\n" + "="*60)
    print("PHASE 2: GENERATING CONTENT")
    print("="*60)
    
    for i, section_title in enumerate(outline):
        print(f"\n[{i+1}/{len(outline)}] Processing: {section_title}")
        
        try:
            # Check if this is the conclusion
            is_conclusion = section_title.lower() == "conclusion"

            # If this is the Abstract, use special abstract prompt
            if section_title.lower() == "abstract":
                section_text = write_section(section_title, "", topic, is_conclusion=False, is_abstract=True)
                # Post-process: ensure it's concise (max 9 lines)
                lines = [line for line in section_text.split('\n') if line.strip()]
                if len(lines) > 9:
                    section_text = '\n'.join(lines[:9])
            else:
                # Generate content normally
                section_text = write_section(section_title, "", topic, is_conclusion)
            
            # 4. Save this section to its own .md file
            md_filename = f"{i+1:02d}_{slugify(section_title)}.md"
            md_path = os.path.join("chapters", md_filename)
            
            with open(md_path, "w", encoding="utf-8") as f:
                # Decide on heading strategy:
                # - If the generated text already begins with a heading (e.g., 'Chapter 1' or '#'),
                #   do not prepend another heading to avoid duplication.
                # - Otherwise, add a single H1 heading for major sections (Abstract, Chapter, Conclusion),
                #   or H2 for minor/other items.

                cleaned_text = section_text.strip()

                # Normalize leading code fences
                if cleaned_text.startswith('```'):
                    # leave code blocks intact; don't try to parse headings inside code
                    pass

                # Detect if content already contains a markdown heading for this section
                content_starts_with_heading = False
                first_line = cleaned_text.split('\n', 1)[0].strip()
                if first_line.startswith('#'):
                    content_starts_with_heading = True

                # Determine whether to add a page break: skip adding a newpage before the very first content
                add_pagebreak = True
                # If this is the first section file and template already adds TOC + newpage, skip extra pagebreak
                if i == 0:
                    add_pagebreak = False

                if add_pagebreak and (section_title.lower().startswith("chapter") or section_title.lower() in ["abstract", "conclusion"]):
                    f.write("\\newpage\n\n")

                if not content_starts_with_heading:
                    # Use H1 for major sections
                    if section_title.lower().startswith('chapter') or section_title.lower() in ['abstract', 'conclusion']:
                        f.write(f"# {section_title}\n\n")
                    else:
                        f.write(f"## {section_title}\n\n")

                # Remove duplicate title occurrences inside the generated content
                if first_line.lower().startswith(section_title.lower()):
                    # strip the duplicated title line
                    cleaned_text = cleaned_text.split('\n', 1)[1].strip() if '\n' in cleaned_text else ''
                if cleaned_text.startswith(f"# {section_title}"):
                    cleaned_text = cleaned_text[len(f"# {section_title}"):].strip()
                if cleaned_text.startswith(f"## {section_title}"):
                    cleaned_text = cleaned_text[len(f"## {section_title}"):].strip()

                # Collapse excessive blank lines to a single blank line
                cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

                f.write(cleaned_text)
            
            md_files_list.append(md_path)
            print(f"     ✓ Saved to '{md_filename}'")
            
        except Exception as e:
            print(f"     ERROR: Failed to generate section - {e}")
            # Continue with next section instead of crashing

    # --- 5. THE TYPESETTER (Assembly) ---
    print("\n" + "="*60)
    print("PHASE 3: ASSEMBLING EBOOK")
    print("="*60)
    
    output_filename = f"{slugify(topic)}_ebook.pdf"
    
    # Generate subtitle using Gemini
    print("Generating subtitle...")
    try:
        subtitle_prompt = f"Create a compelling, concise subtitle (5-10 words) for an ebook about '{topic}'. Return only the subtitle text, no quotes."
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        subtitle_response = model.generate_content(subtitle_prompt)
        subtitle = subtitle_response.text.strip().strip('"').strip("'")
        time.sleep(7.5)
        print(f"✓ Subtitle: {subtitle}")
    except Exception as e:
        print(f"Warning: Could not generate subtitle - {e}")
        subtitle = f"A Comprehensive Guide"
    
    # Read template
    print("Loading template...")
    try:
        with open('chapters/template.md', 'r', encoding='utf-8') as f:
            template = f.read()
    except FileNotFoundError:
        print("ERROR: Template file not found at 'chapters/template.md'")
        return
    
    # Remove template example content completely
    # Find where actual template ends and examples begin
    list_of_tables_marker = '# List of Tables'
    if list_of_tables_marker in template:
        # Find the end of "List of Tables" section
        lot_pos = template.find(list_of_tables_marker)
        # Find the next newpage after that
        next_section = template.find('\n\\newpage', lot_pos + len(list_of_tables_marker))
        if next_section != -1:
            # Keep only up to this point
            template = template[:next_section + 9]  # Include the \newpage
    
    print("✓ Template loaded")
    
    # Replace all placeholders
    replacements = {
        '{{BOOK_TITLE}}': topic.title(),
        '{{BOOK_SUBTITLE}}': subtitle,
        '{{AUTHOR_NAME}}': 'AI Ebook Generator',
        '{{PUBLICATION_DATE}}': 'October 21, 2025',
        '{{PUBLISHER}}': 'AI Generated Books',
        '{{COPYRIGHT_YEAR}}': '2025',
        '{{BOOK_VERSION}}': '1.0',
        '{{KEYWORDS}}': f'ebook, AI generated, {topic}, education',
        '{{BOOK_DESCRIPTION}}': f'A comprehensive guide to {topic}, generated using advanced AI technology',
        '{{SUBJECT}}': topic,
        '{{ISBN}}': '',
        '{{DOI}}': '',
        '{{LICENSE_TEXT}}': 'This work is licensed under a Creative Commons Attribution 4.0 International License.',
        '{{DEDICATION_TEXT}}': f'To all those seeking to understand {topic} and its impact on our world.',
        '{{PREFACE_TEXT}}': f'This ebook provides a comprehensive exploration of {topic}, generated using advanced artificial intelligence. While AI-generated, the content is based on established knowledge and aims to provide readers with accurate, accessible information.'
    }
    
    for placeholder, value in replacements.items():
        template = template.replace(placeholder, value)
    
    # Read all generated content
    print("Compiling content...")
    generated_chapters = ''
    for md_path in md_files_list:
        try:
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()
                generated_chapters += content + '\n\n'
        except Exception as e:
            print(f"Warning: Could not read {md_path} - {e}")
    
    # Find insertion point after template TOC
    toc_marker = '# Table of Contents\n\n<!-- Pandoc generates TOC automatically when `toc: true` is set. -->\n\n\\newpage'
    insert_pos = template.find(toc_marker)
    if insert_pos != -1:
        insert_pos += len(toc_marker)
        # Insert generated chapters after TOC
        book_content = template[:insert_pos] + '\n\n' + generated_chapters
    else:
        # Fallback if marker not found
        print("Warning: Could not find TOC marker, appending content to end")
        book_content = template + '\n\n' + generated_chapters
    
    print("✓ Content compiled")
    
    # Write the complete book
    print("Saving book.md...")
    try:
        with open('book.md', 'w', encoding='utf-8') as f:
            f.write(book_content)
        print("✓ Saved book.md")
    except Exception as e:
        print(f"ERROR: Could not save book.md - {e}")
        return
    
    print("\nCompiling PDF...")
    try:
        # Try xelatex first (better fonts)
        pypandoc.convert_file(
            'book.md',
            'pdf',
            outputfile=output_filename,
            extra_args=[
                '--pdf-engine=xelatex',
                '--toc',
                '--toc-depth=2',
                '-N',
                '--highlight-style=tango',
                '-V', 'geometry:margin=1in',
                '-V', 'documentclass=book',
                '-V', 'linkcolor=blue',
                '-V', 'urlcolor=blue'
            ]
        )
        print(f"\n{'='*60}")
        print(f"🚀 SUCCESS! Ebook saved as '{output_filename}'")
        print(f"{'='*60}")
        print(f"\n✓ Generated {len(outline)} sections")
        print(f"✓ PDF ready for distribution")
        
    except Exception as e:
        print(f"Error with xelatex, trying pdflatex... ({e})")
        try:
            # Fallback to pdflatex
            pypandoc.convert_file(
                'book.md',
                'pdf',
                outputfile=output_filename,
                extra_args=[
                    '--pdf-engine=pdflatex',
                    '--toc',
                    '--toc-depth=2',
                    '-N'
                ]
            )
            print(f"\n{'='*60}")
            print(f"🚀 SUCCESS! Ebook saved as '{output_filename}'")
            print(f"{'='*60}")
        except Exception as e2:
            print(f"\nERROR: Could not create PDF. Is Pandoc installed?")
            print(f"Error: {e2}")
            print(f"\nYou can still use 'book.md' with online converters.")


if __name__ == "__main__":
    main()