#!/usr/bin/env python3
"""
Advanced Image Generation System for Ebooks
Genre-adaptive, context-aware visual generation using Gemini AI
"""

import os
import time
import json
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBW3GE8dH4UexMymdK8FatlS-AsE_9JLB8"
genai.configure(api_key=GEMINI_API_KEY)

# Genre-specific visual styles
GENRE_STYLES = {
    "technology": {
        "style": "modern, clean, tech-focused digital illustration",
        "colors": "blue, cyan, white, gray gradients with tech accents",
        "elements": "circuits, networks, devices, interfaces, diagrams",
        "mood": "innovative, cutting-edge, professional, futuristic"
    },
    "science": {
        "style": "scientific illustration, detailed diagrams, educational",
        "colors": "natural tones, scientific color coding, clear contrasts",
        "elements": "molecules, processes, data visualization, charts",
        "mood": "analytical, precise, informative, authoritative"
    },
    "business": {
        "style": "professional infographic, clean corporate design",
        "colors": "corporate blues, greens, gold accents, professional palette",
        "elements": "charts, graphs, timelines, process flows, icons",
        "mood": "professional, trustworthy, growth-oriented, strategic"
    },
    "healthcare": {
        "style": "medical illustration, clean clinical design, compassionate",
        "colors": "medical blues, greens, soft whites, caring tones",
        "elements": "anatomy, procedures, patient care, medical technology",
        "mood": "caring, professional, trustworthy, hopeful"
    },
    "education": {
        "style": "educational illustration, clear and approachable",
        "colors": "warm, inviting colors, high contrast for clarity",
        "elements": "diagrams, step-by-step visuals, learning aids",
        "mood": "accessible, encouraging, clear, engaging"
    },
    "finance": {
        "style": "financial infographic, data-driven visualization",
        "colors": "green, gold, navy blue, wealth-associated colors",
        "elements": "graphs, trends, coins, growth charts, statistics",
        "mood": "trustworthy, growth-focused, professional, stable"
    },
    "creative": {
        "style": "artistic, expressive, visually striking",
        "colors": "vibrant, artistic palette, creative contrasts",
        "elements": "abstract concepts, creative metaphors, artistic elements",
        "mood": "inspiring, imaginative, expressive, innovative"
    },
    "academic": {
        "style": "scholarly illustration, academic precision",
        "colors": "muted professional tones, academic color schemes",
        "elements": "detailed diagrams, research visuals, academic charts",
        "mood": "authoritative, scholarly, precise, intellectual"
    }
}

# Content type specific prompts
CONTENT_TYPES = {
    "introduction": "overview illustration showing the big picture",
    "concept": "conceptual diagram explaining the main idea visually",
    "comparison": "side-by-side comparison chart or split visual",
    "process": "step-by-step process flow or sequential diagram",
    "timeline": "timeline visualization with key milestones",
    "statistics": "data visualization with charts and graphs",
    "architecture": "system architecture or structural diagram",
    "workflow": "workflow diagram showing process steps",
    "hierarchy": "hierarchical structure or organization chart",
    "relationship": "relationship diagram showing connections",
    "example": "real-world example illustration or case study visual",
    "summary": "comprehensive summary infographic"
}


def detect_genre(topic):
    """Intelligently detect the genre/domain of the ebook topic"""
    topic_lower = topic.lower()
    
    genre_keywords = {
        "technology": ["ai", "artificial intelligence", "machine learning", "programming", 
                      "software", "computer", "algorithm", "data", "tech", "digital"],
        "science": ["biology", "chemistry", "physics", "scientific", "research", 
                   "experiment", "molecular", "quantum", "genetic"],
        "healthcare": ["medical", "health", "medicine", "patient", "clinical", 
                      "diagnosis", "treatment", "healthcare", "disease"],
        "business": ["business", "management", "marketing", "strategy", "leadership",
                    "entrepreneurship", "corporate", "sales"],
        "finance": ["finance", "investment", "trading", "economics", "money",
                   "banking", "stock", "wealth", "cryptocurrency"],
        "education": ["learning", "education", "teaching", "student", "pedagogy",
                     "curriculum", "training", "instruction"],
        "academic": ["theory", "analysis", "framework", "methodology", "philosophical",
                    "theoretical", "scholarly", "academic"]
    }
    
    scores = {}
    for genre, keywords in genre_keywords.items():
        scores[genre] = sum(1 for keyword in keywords if keyword in topic_lower)
    
    best_genre = max(scores, key=scores.get)
    return best_genre if scores[best_genre] > 0 else "technology"


def detect_content_type(section_title):
    """Detect the type of content from section title"""
    title_lower = section_title.lower()
    
    if any(word in title_lower for word in ["introduction", "overview", "what is"]):
        return "introduction"
    elif any(word in title_lower for word in ["vs", "versus", "compare", "comparison"]):
        return "comparison"
    elif any(word in title_lower for word in ["process", "steps", "how to", "procedure"]):
        return "process"
    elif any(word in title_lower for word in ["timeline", "history", "evolution"]):
        return "timeline"
    elif any(word in title_lower for word in ["statistics", "data", "metrics", "performance"]):
        return "statistics"
    elif any(word in title_lower for word in ["architecture", "structure", "framework"]):
        return "architecture"
    elif any(word in title_lower for word in ["workflow", "pipeline", "flow"]):
        return "workflow"
    elif any(word in title_lower for word in ["types", "categories", "classification"]):
        return "hierarchy"
    elif any(word in title_lower for word in ["example", "case study", "application"]):
        return "example"
    elif any(word in title_lower for word in ["summary", "conclusion", "key points"]):
        return "summary"
    else:
        return "concept"


def generate_advanced_image_prompt(topic, section_title, genre=None):
    """Generate sophisticated, genre-adaptive image prompts"""
    if genre is None:
        genre = detect_genre(topic)
    
    style_guide = GENRE_STYLES.get(genre, GENRE_STYLES["technology"])
    content_type = detect_content_type(section_title)
    content_description = CONTENT_TYPES.get(content_type, "conceptual illustration")
    
    prompt = f"""
Create a professional, high-quality {content_description} for an ebook.

**Context:**
- Main Topic: {topic}
- Section: {section_title}
- Genre: {genre.title()}

**Visual Style:**
- Style: {style_guide['style']}
- Color Palette: {style_guide['colors']}
- Key Elements: {style_guide['elements']}
- Mood: {style_guide['mood']}

**Content Requirements:**
- Clear visual hierarchy with focal point
- Professional typography if text is included
- Balanced composition following rule of thirds
- High contrast for readability in print and digital
- Appropriate for {genre} audience
- Educational and informative purpose

**Technical Specifications:**
- Format: Digital illustration / Infographic
- Aspect Ratio: 16:9 (horizontal) for better ebook integration
- Quality: Publication-ready, high resolution
- Style consistency: Modern, clean, professional

**Specific to this section:**
Create a visual that clearly illustrates "{section_title}" in the context of {topic}.
The image should help readers understand the concept at a glance and complement the written content.

Make it visually appealing, informative, and genre-appropriate.
"""
    
    return prompt.strip()


def generate_image_with_gemini(prompt, output_path="generated_image.png"):
    """Generate visual specification and placeholder using Gemini AI"""
    print(f"\n{'='*70}")
    print(f"🎨 Generating Visual Specification")
    print(f"{'='*70}")
    print(f"Output: {output_path}")
    
    # Note: Imagen API not available in current SDK
    # Generating detailed specification instead
    print("\n📝 Creating detailed visual specification for external tools...")
    print("    (Can be used with DALL-E, Midjourney, Stable Diffusion, or designers)")
    
    return generate_image_description(prompt, output_path)


def generate_image_description(prompt, output_path):
    """Generate detailed image description using Gemini text model"""
    try:
        print("\n📝 Generating detailed visual specification...")
        
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        description_prompt = f"""
Based on this image prompt:
{prompt}

Create an extremely detailed visual specification that could be used by:
1. A professional illustrator
2. Another AI image generation tool (DALL-E, Midjourney, Stable Diffusion)
3. A graphic designer

Include:
- **Composition:** Exact layout, positioning, visual hierarchy
- **Color Scheme:** Specific colors with hex codes if possible
- **Typography:** Font styles, sizes, text placement
- **Visual Elements:** Detailed list of all elements to include
- **Style Details:** Line weights, shadows, gradients, effects
- **Dimensions:** Relative sizes and proportions
- **Technical Notes:** Any specific techniques or approaches

Also generate optimized prompts for:
- **DALL-E 3:** Clear, concise, descriptive
- **Midjourney:** Artistic, parameter-rich
- **Stable Diffusion:** Detailed with quality tags

Make it so detailed that anyone could recreate this image from your description.
"""
        
        response = model.generate_content(description_prompt)
        description = response.text
        
        # Generate simplified prompts for external tools
        external_prompts = generate_external_tool_prompts(prompt)
        
        # Save comprehensive specification
        desc_file = output_path.replace('.png', '_specification.txt')
        with open(desc_file, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("VISUAL SPECIFICATION FOR EBOOK IMAGE\n")
            f.write("="*70 + "\n\n")
            f.write(f"Original Advanced Prompt:\n{'-'*70}\n{prompt}\n\n")
            f.write(f"Detailed Specification:\n{'-'*70}\n{description}\n\n")
            f.write(f"Ready-to-Use Prompts for External Tools:\n{'-'*70}\n{external_prompts}\n")
        
        print(f"\n✅ Visual specification generated!")
        print(f"   File: {desc_file}")
        print(f"   Includes: Detailed spec + Ready-to-use prompts for DALL-E/Midjourney/SD")
        
        # Create placeholder image
        create_styled_placeholder(prompt, output_path, description[:200])
        
        return True, f"Visual specification saved to {desc_file}"
        
    except Exception as e:
        print(f"❌ Description generation failed: {e}")
        return False, str(e)


def generate_external_tool_prompts(original_prompt):
    """Generate optimized prompts for external AI image tools"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
Based on this image concept:
{original_prompt}

Generate 3 optimized prompts:

1. **DALL-E 3 Prompt** (clear, descriptive, natural language):
   - Focus on clear description
   - Specific about style and composition
   - 1-2 sentences, very descriptive

2. **Midjourney Prompt** (artistic, with parameters):
   - Artistic and evocative language
   - Include style references
   - Add parameters like --ar 16:9 --style raw --v 6

3. **Stable Diffusion Prompt** (detailed with quality tags):
   - Detailed description with quality tags
   - Keywords separated by commas
   - Include: detailed, high quality, professional, etc.

Format each clearly with the tool name as header.
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"Could not generate external tool prompts: {e}"


def create_styled_placeholder(prompt, output_path, preview_text, size=(1600, 900)):
    """Create a professional placeholder image"""
    try:
        img = Image.new('RGB', size, color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # Gradient background
        for y in range(size[1]):
            progress = y / size[1]
            r = int(70 + (130 - 70) * progress)
            g = int(130 + (180 - 130) * progress)
            b = int(180 + (220 - 180) * progress)
            draw.line([(0, y), (size[0], y)], fill=(r, g, b))
        
        # Fonts
        try:
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 48)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
            text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Title
        title = "📊 Visual Placeholder"
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text(((size[0] - title_width) / 2, 100), title, fill=(255, 255, 255), font=title_font)
        
        # Subtitle
        subtitle = "Image specification generated - Ready for visual creation"
        subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
        subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
        draw.text(((size[0] - subtitle_width) / 2, 170), subtitle, fill=(240, 240, 240), font=subtitle_font)
        
        # Preview box
        box_padding = 60
        box_top = 250
        box_bottom = size[1] - 100
        draw.rectangle(
            [(box_padding, box_top), (size[0] - box_padding, box_bottom)],
            fill=(255, 255, 255, 230),
            outline=(100, 100, 100),
            width=2
        )
        
        # Preview text
        wrapped = wrap_text_simple(preview_text, 80)
        y_text = box_top + 30
        for line in wrapped[:10]:
            draw.text((box_padding + 30, y_text), line, fill=(40, 40, 40), font=text_font)
            y_text += 35
        
        # Footer
        footer = "Use the accompanying _specification.txt file to generate the actual image"
        footer_bbox = draw.textbbox((0, 0), footer, font=text_font)
        footer_width = footer_bbox[2] - footer_bbox[0]
        draw.text(((size[0] - footer_width) / 2, size[1] - 50), footer, fill=(255, 255, 255), font=text_font)
        
        img.save(output_path)
        print(f"🖼️  Placeholder image created: {output_path}")
        return True
        
    except Exception as e:
        print(f"⚠️  Placeholder creation failed: {e}")
        img = Image.new('RGB', size, color=(100, 150, 200))
        img.save(output_path)
        return True


def wrap_text_simple(text, max_chars):
    """Simple text wrapping"""
    words = text.split()
    lines = []
    current = []
    current_len = 0
    
    for word in words:
        if current_len + len(word) + 1 <= max_chars:
            current.append(word)
            current_len += len(word) + 1
        else:
            if current:
                lines.append(' '.join(current))
            current = [word]
            current_len = len(word)
    
    if current:
        lines.append(' '.join(current))
    
    return lines


def generate_ebook_visuals(topic, sections):
    """Generate images for each section of an ebook"""
    print(f"\n{'='*70}")
    print(f"Generating Visuals for Ebook: {topic}")
    print(f"{'='*70}\n")
    
    os.makedirs("images", exist_ok=True)
    genre = detect_genre(topic)
    print(f"🎨 Detected Genre: {genre.title()}")
    print(f"   Style: {GENRE_STYLES[genre]['style']}\n")
    
    image_map = {}
    
    for i, section in enumerate(sections, 1):
        print(f"\n[{i}/{len(sections)}] Processing: {section}")
        
        # Generate advanced prompt
        image_prompt = generate_advanced_image_prompt(topic, section, genre)
        
        # Generate filename
        safe_name = section.lower().replace(' ', '_').replace(':', '').replace('/', '_')[:50]
        image_path = f"images/{i:02d}_{safe_name}.png"
        
        # Generate image
        success, message = generate_image_with_gemini(image_prompt, image_path)
        
        if success:
            image_map[section] = image_path
            print(f"✅ Ready: {image_path}\n")
        else:
            print(f"⚠️  {message}\n")
        
        time.sleep(2)
    
    return image_map


def main():
    """Run comprehensive image generation tests"""
    
    print("\n" + "="*70)
    print("ADVANCED EBOOK IMAGE GENERATION SYSTEM")
    print("="*70 + "\n")
    
    # Test 1: Genre Detection
    print("### TEST 1: Genre Detection ###\n")
    test_topics = [
        "Machine Learning Algorithms",
        "Human Anatomy and Physiology",
        "Business Strategy and Leadership",
        "Quantum Physics Explained"
    ]
    
    for topic in test_topics:
        genre = detect_genre(topic)
        print(f"Topic: {topic}")
        print(f"  → Genre: {genre.title()}")
        print(f"  → Style: {GENRE_STYLES[genre]['style']}\n")
    
    # Test 2: Single image with advanced prompt
    print("\n### TEST 2: Advanced Image Generation ###\n")
    
    test_topic = "Artificial Intelligence in Healthcare"
    test_section = "AI-Powered Diagnostic Systems: Architecture and Workflow"
    
    prompt = generate_advanced_image_prompt(test_topic, test_section)
    print(f"Generated Prompt Preview:\n{'-'*70}")
    print(prompt[:300] + "...")
    print(f"{'-'*70}\n")
    
    success, message = generate_image_with_gemini(prompt, "test_advanced_image.png")
    print(f"\nResult: {message}\n")
    
    # Test 3: Generate full set
    print("\n### TEST 3: Generate Full Ebook Image Set ###\n")
    
    topic = "Machine Learning Fundamentals"
    sections = [
        "Introduction to Machine Learning",
        "Supervised vs Unsupervised Learning",
        "Neural Networks Architecture",
        "Model Training Process"
    ]
    
    image_map = generate_ebook_visuals(topic, sections)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"✅ Images/Specs generated: {len(image_map)}")
    print(f"📁 Output directory: images/")
    
    if image_map:
        print("\nGenerated files:")
        for section, path in image_map.items():
            if os.path.exists(path):
                size = os.path.getsize(path)
                spec_file = path.replace('.png', '_specification.txt')
                has_spec = "✓" if os.path.exists(spec_file) else "✗"
                print(f"  • {path} ({size:,} bytes) [Spec: {has_spec}]")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
