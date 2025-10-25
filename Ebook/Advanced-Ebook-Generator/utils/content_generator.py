"""
Content Generator Module
Handles AI-powered content generation with genre-specific customization
"""

import time
import json
import re
from typing import List, Dict, Optional
import google.generativeai as genai


class ContentGenerator:
    """AI-powered content generator with advanced features"""
    
    def __init__(self, api_key: str, genre: str, config: dict):
        """Initialize the content generator"""
        self.api_key = api_key
        self.genre = genre
        self.config = config
        self.genre_config = config['genres'].get(genre, config['genres']['technology'])
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Rate limiting settings
        self.rate_limit_delay = config['api_settings']['rate_limit_delay']
        self.max_retries = config['api_settings']['max_retries']
    
    def generate_outline(self, topic: str, num_chapters: int, length_config: dict) -> List[Dict]:
        """Generate book outline with custom structure"""
        
        subsections = length_config['subsections']
        
        prompt = f"""You are a bestselling author in the {self.genre} genre. Create a compelling book outline for "{topic}".

Write this as a professional {self.genre} book that would be published by major publishers. Study how top authors in the {self.genre} genre structure their books and create a similar high-quality outline.

Structure Required:
- Preface (personal introduction from the author)
- Introduction (engaging hook that draws readers in)
- {num_chapters} Main Chapters (each with {subsections} well-crafted subsections)
- Conclusion (powerful closing with lasting impact)

For each chapter:
- Create compelling, professional chapter titles (not generic)
- Design {subsections} subsection titles that flow naturally
- Write a brief description of the chapter's core message

Return ONLY valid JSON in this exact format:
[
  {{"title": "Preface", "type": "preface", "subsections": []}},
  {{"title": "Introduction", "type": "introduction", "subsections": []}},
  {{"title": "Chapter 1: [Compelling Title]", "type": "chapter", "subsections": ["Subsection 1", "Subsection 2"], "description": "Brief description"}},
  {{"title": "Conclusion", "type": "conclusion", "subsections": []}}
]

Make this outline worthy of a bestselling {self.genre} book about {topic}.
"""
        
        try:
            response = self.model.generate_content(prompt)
            time.sleep(self.rate_limit_delay)
            
            outline_text = response.text.strip()
            
            # Clean JSON
            if outline_text.startswith('```json'):
                outline_text = outline_text[7:]
            if outline_text.startswith('```'):
                outline_text = outline_text[3:]
            if outline_text.endswith('```'):
                outline_text = outline_text[:-3]
            outline_text = outline_text.strip()
            
            outline = json.loads(outline_text)
            return outline
            
        except Exception as e:
            print(f"Error generating outline: {e}")
            # Fallback outline
            return self._create_fallback_outline(topic, num_chapters, subsections)
    
    def _create_fallback_outline(self, topic: str, num_chapters: int, subsections: int) -> List[Dict]:
        """Create a basic fallback outline"""
        outline = [
            {"title": "Preface", "type": "preface", "subsections": []},
            {"title": "Introduction", "type": "introduction", "subsections": []}
        ]
        
        for i in range(1, num_chapters + 1):
            chapter = {
                "title": f"Chapter {i}: Understanding {topic}",
                "type": "chapter",
                "subsections": [f"Subsection {j}" for j in range(1, subsections + 1)],
                "description": f"Exploring key aspects of {topic}"
            }
            outline.append(chapter)
        
        outline.append({"title": "Conclusion", "type": "conclusion", "subsections": []})
        return outline
    
    def generate_section(
        self,
        topic: str,
        section: Dict,
        research_context: List[Dict],
        features: Dict,
        words_target: int
    ) -> str:
        """Generate content for a specific section with enhancements"""
        
        section_type = section['type']
        section_title = section['title']
        subsections = section.get('subsections', [])
        
        # Build research context
        research_text = ""
        if research_context:
            research_text = "\n\nResearch Context:\n"
            for idx, result in enumerate(research_context[:3], 1):
                research_text += f"{idx}. {result.get('title', 'No title')}: {result.get('snippet', 'No description')}\n"
        
        # Build enhancement instructions
        enhancement_instructions = ""
        if features.get('case_studies'):
            enhancement_instructions += "- Include 1-2 real-world case studies with specific examples\n"
        if features.get('did_you_know'):
            enhancement_instructions += "- Add 'Did You Know?' fact boxes with interesting insights\n"
        if features.get('real_world_examples'):
            enhancement_instructions += "- Provide concrete real-world examples throughout\n"
        if features.get('summary_boxes'):
            enhancement_instructions += "- Include key takeaway summary boxes\n"
        if features.get('expert_quotes'):
            enhancement_instructions += "- Include relevant expert quotes or industry insights\n"
        
        # Section-specific prompts
        if section_type == 'preface':
            prompt = self._get_preface_prompt(topic, words_target)
        elif section_type == 'introduction':
            prompt = self._get_introduction_prompt(topic, research_text, enhancement_instructions, words_target)
        elif section_type == 'chapter':
            prompt = self._get_chapter_prompt(topic, section_title, subsections, research_text, enhancement_instructions, words_target)
        elif section_type == 'conclusion':
            prompt = self._get_conclusion_prompt(topic, enhancement_instructions, words_target)
        else:
            prompt = self._get_generic_prompt(section_title, topic, words_target)
        
        # Generate with retry logic
        content = self._generate_with_retry(prompt)
        
        # Add quiz questions if enabled
        if features.get('quiz_questions') and section_type == 'chapter':
            quiz = self._generate_quiz(section_title, topic)
            content += f"\n\n{quiz}"
        
        return content
    
    def _get_preface_prompt(self, topic: str, words_target: int) -> str:
        """Generate prompt for preface section"""
        return f"""You are writing the preface for a professional {self.genre} book about "{topic}".

Write this preface as a bestselling {self.genre} author would. Study how top authors in this genre write their prefaces and match that quality and style.

In the preface, authentically convey:
1. Why you (as the author) wrote this book - what drove you to create it
2. Your personal connection or journey with {topic}
3. What readers will gain from this book
4. How this book is different from others on {topic}
5. A personal invitation to the reader to engage with the material

Write approximately {words_target} words.
Use first person ("I", "my"). Be personal, genuine, and compelling.
Write like this is going to be published - make it exceptional.
"""
    
    def _get_abstract_prompt(self, topic: str, words_target: int) -> str:
        """Generate prompt for abstract section (kept for backward compatibility)"""
        return f"""Write a professional abstract for an e-book about "{topic}".

Genre: {self.genre.title()}
Tone: {self.genre_config['tone']}
Target Length: {words_target} words

The abstract should:
1. Provide a comprehensive overview of the book's scope
2. Highlight the main themes and topics covered
3. Explain the value and benefits readers will gain
4. Be written in an engaging, professional tone
5. Hook the reader's interest

Write as a cohesive, well-structured text without headings.
"""
    
    def _get_introduction_prompt(self, topic: str, research_text: str, enhancements: str, words_target: int) -> str:
        """Generate prompt for introduction"""
        return f"""You are writing the introduction for a professional {self.genre} book about "{topic}".

Write this as a bestselling {self.genre} author would - study how masters of this genre craft their introductions and match that caliber.

{research_text}

Create an introduction (~{words_target} words) that:
1. Opens with a powerful hook that immediately grabs attention (story, statistic, provocative question, or bold statement)
2. Establishes why {topic} matters RIGHT NOW - create urgency and relevance
3. Connects emotionally with the reader - make them feel understood
4. Outlines the transformation or value this book delivers
5. Builds anticipation for the journey ahead

{enhancements}

Write in a natural, flowing narrative style. This should read like a published book from a major publisher, not an academic paper or blog post.
Use compelling storytelling where appropriate. Make readers unable to stop reading.
"""
    
    def _get_chapter_prompt(self, topic: str, chapter_title: str, subsections: List[str], research_text: str, enhancements: str, words_target: int) -> str:
        """Generate prompt for a chapter"""
        
        subsection_text = ""
        if subsections:
            subsection_text = f"\n\nOrganize the chapter around these subsections:\n"
            for subsection in subsections:
                subsection_text += f"- {subsection}\n"
            subsection_text += "\nWeave these together into a cohesive narrative, not just disconnected sections."
        
        return f"""You are writing a chapter for a professional {self.genre} book about "{topic}".

**Chapter Title**: {chapter_title}

Write this chapter as if it will be published by a major publisher. Study how bestselling {self.genre} authors craft their chapters - the pacing, depth, examples, and narrative flow - and match that quality.

Target length: ~{words_target} words
{subsection_text}
{research_text}

Chapter Requirements:
1. **Opening Hook**: Start with something compelling (story, question, surprising fact, or vivid scenario)
2. **Clear Structure**: Guide readers through the content logically, building on each concept
3. **Depth & Substance**: Provide real value - insights, frameworks, actionable information
4. **Concrete Examples**: Use real-world scenarios, case studies, or relatable situations
5. **Engaging Voice**: Write like you're having an intelligent conversation, not lecturing
6. **Smooth Transitions**: Connect ideas naturally - each paragraph should flow to the next
7. **Memorable Takeaways**: Ensure readers leave with clear, applicable knowledge

{enhancements}

Write in a natural, narrative style appropriate for published {self.genre} books. Use:
- **Bold** for key concepts or critical insights
- *Italics* for emphasis or important terms
- Clear headings (##) for subsections
- Tables for comparisons or structured data (when helpful)
- Blockquotes for powerful insights or important callouts
- Lists for clarity (but don't overuse them)

This should read like a chapter from a book readers can't put down, not a textbook or technical manual.
"""
    
    def _get_conclusion_prompt(self, topic: str, enhancements: str, words_target: int) -> str:
        """Generate prompt for conclusion"""
        return f"""You are writing the conclusion for a professional {self.genre} book about "{topic}".

Write this conclusion as a bestselling {self.genre} author would - this is your final moment with the reader. Make it count.

Create a powerful conclusion (~{words_target} words) that:
1. **Synthesize Key Insights**: Elegantly tie together the book's main themes (without just listing them)
2. **Reinforce Transformation**: Remind readers of the journey they've taken and what they've gained
3. **Future Vision**: Paint a compelling picture of what's next - whether that's action steps, future trends, or a broader perspective
4. **Emotional Resonance**: Leave readers feeling inspired, empowered, or deeply satisfied
5. **Strong Closing**: End with a memorable final thought - a call to action, inspiring vision, or powerful statement

{enhancements}

This conclusion should feel like the satisfying end of a journey, not just a summary.
Write with the same narrative quality as the best chapters. Make readers glad they read this book.
"""
    
    def _get_generic_prompt(self, section_title: str, topic: str, words_target: int) -> str:
        """Generic prompt for other sections"""
        return f"""Write content for the section: "{section_title}" in an e-book about "{topic}".

Genre: {self.genre.title()}
Tone: {self.genre_config['tone']}
Target Length: {words_target} words

Write comprehensive, professional content appropriate for this section.
Use proper markdown formatting.
"""
    
    def _generate_quiz(self, chapter_title: str, topic: str) -> str:
        """Generate quiz questions for a chapter"""
        
        prompt = f"""Create 5 thought-provoking quiz questions for a chapter titled "{chapter_title}" in an e-book about "{topic}".

Format each question as:
**Question X:** [Question text]
a) [Option A]
b) [Option B]
c) [Option C]
d) [Option D]

**Answer:** [Correct letter]
**Explanation:** [Brief explanation of why this is correct]

Make questions educational and relevant to the chapter content.
"""
        
        try:
            response = self.model.generate_content(prompt)
            time.sleep(self.rate_limit_delay)
            return f"\n\n---\n\n## 📝 Chapter Quiz\n\n{response.text}"
        except:
            return ""
    
    def _generate_with_retry(self, prompt: str) -> str:
        """Generate content with retry logic"""
        
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.model.generate_content(prompt)
                time.sleep(self.rate_limit_delay)
                return response.text
            except Exception as e:
                if attempt < self.max_retries:
                    backoff = self.config['api_settings']['retry_backoff']
                    print(f"Retry attempt {attempt}/{self.max_retries} after {backoff}s...")
                    time.sleep(backoff)
                else:
                    raise e
        
        return "[Content generation failed]"
    
    def generate_optional_section(
        self,
        topic: str,
        section_name: str,
        main_content: List[Dict],
        citation_manager
    ) -> str:
        """Generate optional sections like Glossary, Bibliography, etc."""
        
        # Front Matter Sections
        if section_name == "Dedication":
            return self._generate_dedication(topic)
        elif section_name == "Epigraph":
            return self._generate_epigraph(topic)
        elif section_name == "Foreword":
            return self._generate_foreword(topic)
        elif section_name == "Preface":
            return self._generate_preface(topic)
        elif section_name == "Acknowledgments":
            return self._generate_acknowledgments(topic)
        
        # Back Matter Sections
        elif section_name == "Epilogue":
            return self._generate_epilogue(topic, main_content)
        elif section_name == "Afterword":
            return self._generate_afterword(topic)
        elif section_name == "Glossary":
            return self._generate_glossary(topic, main_content)
        elif section_name == "Bibliography":
            return citation_manager.generate_bibliography()
        elif section_name == "Notes & References":
            return self._generate_notes_references(topic)
        elif section_name == "Index":
            return self._generate_index(main_content)
        elif section_name == "About the Author":
            return self._generate_about_author()
        elif section_name == "Appendices":
            return self._generate_appendices(topic)
        elif section_name == "Other Books by Author":
            return self._generate_other_books()
        else:
            return f"## {section_name}\n\n[Content for {section_name}]"
    
    def _generate_glossary(self, topic: str, main_content: List[Dict]) -> str:
        """Generate a glossary of key terms"""
        
        prompt = f"""Create a comprehensive glossary for a professional {self.genre} book about "{topic}".

Include 15-20 key terms that {self.genre} readers need to understand.
Write clear, accessible definitions appropriate for your audience.

Format:
**Term**: Concise, clear definition

List alphabetically. Match the quality of glossaries in published {self.genre} books.
"""
        
        return self._generate_with_retry(prompt)
    
    def _generate_index(self, main_content: List[Dict]) -> str:
        """Generate an index placeholder"""
        return """# Index {.unnumbered}

\\printindex

*Note: The index will be automatically generated during PDF compilation if indexing is enabled.*
"""
    
    def _generate_about_author(self) -> str:
        """Generate About the Author section"""
        return """## About the Author

This e-book was generated using advanced AI technology, combining multiple artificial intelligence systems to create comprehensive, well-researched content. The AI Author specializes in creating educational and informative content across various domains.
"""
    
    def _generate_appendices(self, topic: str) -> str:
        """Generate appendices"""
        
        prompt = f"""Create useful appendices for a professional {self.genre} book about "{topic}".

Provide valuable supplementary resources that {self.genre} readers would actually use:
- Curated resources (websites, books, courses)
- Recommended tools or software
- Further reading
- Professional organizations or communities

Make this genuinely helpful, not just filler. Format clearly with headings and lists.
"""
        
        return self._generate_with_retry(prompt)
    
    # Front Matter Generation Methods
    
    def _generate_dedication(self, topic: str) -> str:
        """Generate dedication"""
        
        prompt = f"""Write a heartfelt dedication for a professional {self.genre} book about "{topic}".

Study how acclaimed {self.genre} authors write dedications. Keep it short (2-3 sentences), personal, and meaningful.
Make it appropriate for a published {self.genre} book.
Format simply without heading.
"""
        
        return self._generate_with_retry(prompt)
    
    def _generate_epigraph(self, topic: str) -> str:
        """Generate epigraph (inspirational quote)"""
        
        prompt = f"""Select an inspiring and relevant quote for a professional {self.genre} book about "{topic}".

Choose a quote that would resonate with {self.genre} readers - something thought-provoking and perfectly aligned with the book's theme.

Format:
"The quote goes here."
— Author Name, Source (if relevant)
"""
        
        return self._generate_with_retry(prompt)
    
    def _generate_foreword(self, topic: str) -> str:
        """Generate foreword"""
        
        prompt = f"""Write a foreword for a professional {self.genre} book about "{topic}".

Write as if you are a respected expert in the {self.genre} field recommending this book.
Study how forewords are written in published {self.genre} books and match that quality.

Include:
- Why this book is important and timely (compelling opening)
- What makes this book unique and valuable
- Who should read it and why
- A strong, enthusiastic recommendation

Write ~400-500 words in the style appropriate for published {self.genre} books.
"""
        
        return self._generate_with_retry(prompt)
    
    def _generate_preface(self, topic: str) -> str:
        """Generate preface"""
        
        prompt = f"""Write the preface for a professional {self.genre} book about "{topic}".

Write as the author in first person. Study how bestselling {self.genre} authors write prefaces - personal, engaging, and authentic.

Cover:
- Why you wrote this book (personal motivation, passion, or experience)
- Your journey with {topic}
- What readers will gain
- How to get the most from this book

Write ~400-600 words. Be personal, genuine, and compelling - make readers excited to dive in.
"""
        
        return self._generate_with_retry(prompt)
    
    def _generate_acknowledgments(self, topic: str) -> str:
        """Generate acknowledgments"""
        
        prompt = f"""Write acknowledgments for a professional {self.genre} book about "{topic}".

Write as the author would - genuine gratitude to those who made the book possible.
Study how published {self.genre} books handle acknowledgments.

Thank (naturally, not as a checklist):
- Experts, researchers, or mentors in the {self.genre} field
- Beta readers and supporters
- Tools and resources used
- The {self.genre} community

Keep it heartfelt and authentic. ~200-300 words.
"""
        
        return self._generate_with_retry(prompt)
    
    # Back Matter Generation Methods
    
    def _generate_epilogue(self, topic: str, main_content: List[Dict]) -> str:
        """Generate epilogue"""
        
        prompt = f"""Write an epilogue for a professional {self.genre} book about "{topic}".

Study how great {self.genre} authors write epilogues - reflective, forward-looking, and satisfying.

The epilogue should:
- Reflect on the journey and insights
- Look toward the future of {topic}
- Leave readers inspired and contemplative
- Provide closure while opening new possibilities

Write ~400-500 words with the narrative quality expected in published {self.genre} books.
"""
        
        return self._generate_with_retry(prompt)
    
    def _generate_afterword(self, topic: str) -> str:
        """Generate afterword"""
        
        prompt = f"""Write an afterword for an e-book about "{topic}".

Genre: {self.genre.title()}
Tone: {self.genre_config['tone']}

Include:
1. Final thoughts and reflections
2. How the book came to be
3. Future directions in {topic}
4. A call to action for readers

Length: 300-400 words
"""
        
        return self._generate_with_retry(prompt)
    
    def _generate_notes_references(self, topic: str) -> str:
        """Generate notes and references section"""
        
        return f"""## Notes & References

### Chapter Notes

This e-book incorporates established research and knowledge about {topic}. While AI-generated, the content is based on verified information and best practices in the field.

### Additional Reading

For further exploration of {topic}, readers are encouraged to:
- Consult peer-reviewed journals in the field
- Follow current research and developments
- Engage with professional communities
- Explore the bibliography for source materials

### Citations

Specific citations are formatted according to the selected citation style and appear in the Bibliography section.
"""
    
    def _generate_other_books(self) -> str:
        """Generate other books section"""
        
        return """## Other Books by the Author

This AI-powered e-book generation system can create comprehensive books on any topic. 

### Available Topics Include:
- Technology and Innovation
- Healthcare and Medicine
- Business and Leadership
- Science and Research
- Education and Learning
- Finance and Economics
- Personal Development

For more information about generating custom e-books, please visit our platform.
"""
