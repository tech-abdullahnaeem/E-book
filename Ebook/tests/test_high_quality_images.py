#!/usr/bin/env python3
"""
High-Quality Image Generation System
Generates actual high-quality, genre-specific images using AI
"""

import os
import time
import json
import requests
import google.generativeai as genai
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBW3GE8dH4UexMymdK8FatlS-AsE_9JLB8"
genai.configure(api_key=GEMINI_API_KEY)

# Image generation options
USE_POLLINATIONS_AI = True  # Free AI image generation API
USE_PLACEHOLDER = True  # High-quality placeholder generation

# Genre-specific visual styles for high-quality output
PREMIUM_STYLES = {
    "technology": {
        "aesthetic": "sleek, modern, futuristic tech aesthetic with clean lines",
        "lighting": "soft ambient lighting with digital glow effects",
        "colors": "deep blues (#1E3A8A), cyan (#06B6D4), white (#FFFFFF), silver gradients",
        "quality": "8K resolution, ray-traced, photorealistic 3D rendering",
        "mood": "innovative, cutting-edge, sophisticated, professional"
    },
    "healthcare": {
        "aesthetic": "clean medical environment, professional clinical design",
        "lighting": "bright, clean lighting with soft shadows",
        "colors": "medical blue (#2563EB), mint green (#10B981), pure white (#FFFFFF)",
        "quality": "ultra-high resolution, medical-grade precision, detailed textures",
        "mood": "caring, trustworthy, professional, hopeful, compassionate"
    },
    "science": {
        "aesthetic": "scientific precision, detailed technical illustration",
        "lighting": "even laboratory lighting, clear visibility",
        "colors": "scientific color-coding, high contrast for clarity",
        "quality": "microscopic detail, scientific accuracy, publication-ready",
        "mood": "analytical, precise, educational, authoritative"
    },
    "business": {
        "aesthetic": "corporate professionalism, executive design",
        "lighting": "professional office lighting, polished appearance",
        "colors": "navy blue (#1E40AF), emerald (#059669), gold accents (#F59E0B)",
        "quality": "sharp details, professional photography quality",
        "mood": "confident, successful, strategic, growth-oriented"
    }
}


def detect_genre(topic):
    """Detect genre from topic"""
    topic_lower = topic.lower()
    
    keywords = {
        "technology": ["ai", "machine learning", "software", "algorithm", "data", "tech"],
        "healthcare": ["health", "medical", "clinical", "patient", "diagnosis", "treatment"],
        "science": ["biology", "chemistry", "physics", "research", "scientific"],
        "business": ["business", "management", "strategy", "marketing", "leadership"]
    }
    
    for genre, words in keywords.items():
        if any(word in topic_lower for word in words):
            return genre
    
    return "technology"


def generate_premium_image_prompts(topic, section_title, genre=None):
    """
    Generate multiple high-quality prompts optimized for different AI tools
    """
    if genre is None:
        genre = detect_genre(topic)
    
    style = PREMIUM_STYLES.get(genre, PREMIUM_STYLES["technology"])
    
    print(f"\n{'='*70}")
    print(f"🎨 Generating Premium Image Prompts")
    print(f"{'='*70}")
    print(f"Topic: {topic}")
    print(f"Section: {section_title}")
    print(f"Genre: {genre.title()}")
    print(f"{'='*70}\n")
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        prompt = f"""
You are an expert visual designer creating prompts for AI image generation tools.

**Context:**
- Ebook Topic: {topic}
- Section: {section_title}
- Genre: {genre.title()}
- Purpose: Educational ebook illustration (16:9 aspect ratio)

**Visual Style Guidelines:**
- Aesthetic: {style['aesthetic']}
- Lighting: {style['lighting']}
- Colors: {style['colors']}
- Quality: {style['quality']}
- Mood: {style['mood']}

**Task:** Generate 4 optimized prompts for different tools:

1. **DALL-E 3 PROMPT** (OpenAI)
   - Natural language, descriptive
   - 1-2 detailed sentences
   - Focus on clarity and composition
   - Include style and mood
   
2. **MIDJOURNEY PROMPT** (Discord Bot)
   - Artistic, parameter-rich
   - Use descriptive keywords
   - Include technical parameters:
     * --ar 16:9 (aspect ratio)
     * --style raw (for photorealism)
     * --v 6 (version 6)
     * --quality 2 (highest quality)
   - Evocative language
   
3. **STABLE DIFFUSION PROMPT** (Automatic1111/ComfyUI)
   - Detailed keyword list (comma-separated)
   - Quality tags: masterpiece, best quality, highly detailed, 8k, professional
   - Negative prompt included (what to avoid)
   - Specific art style
   
4. **LEONARDO.AI PROMPT** (User-friendly platform)
   - Clear description with style
   - Include: composition, style, quality level
   - Medium-length, balanced detail

**Requirements for ALL prompts:**
- Directly relevant to "{section_title}"
- Professional, educational purpose
- 16:9 horizontal format
- Publication-ready quality
- Clear, sharp, well-composed
- No text/typography in images (unless specified)
- Appropriate for {genre} audience

Format your response clearly with headers for each tool.
Make each prompt ready to copy-paste directly into the respective tool.
"""
        
        print("⏳ Generating optimized prompts...")
        response = model.generate_content(prompt)
        prompts = response.text
        
        print(f"\n✅ Prompts generated successfully!\n")
        
        return prompts
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def save_prompts(topic, section_title, prompts, output_dir="image_prompts"):
    """Save prompts to organized files"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Create safe filename
    safe_name = section_title.lower().replace(' ', '_').replace(':', '').replace('/', '_')[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"{output_dir}/{safe_name}_prompts.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("="*70 + "\n")
        f.write("HIGH-QUALITY IMAGE GENERATION PROMPTS\n")
        f.write("="*70 + "\n\n")
        f.write(f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}\n")
        f.write(f"Topic: {topic}\n")
        f.write(f"Section: {section_title}\n\n")
        f.write("="*70 + "\n")
        f.write("READY-TO-USE PROMPTS\n")
        f.write("="*70 + "\n\n")
        f.write(prompts)
        f.write("\n\n" + "="*70 + "\n")
        f.write("USAGE INSTRUCTIONS\n")
        f.write("="*70 + "\n\n")
        f.write("1. Choose your preferred AI image generation tool\n")
        f.write("2. Copy the corresponding prompt above\n")
        f.write("3. Paste into the tool (DALL-E, Midjourney, Stable Diffusion, or Leonardo)\n")
        f.write("4. Generate the image\n")
        f.write("5. Download and use in your ebook\n\n")
        f.write("TIP: For Midjourney, paste the entire prompt including --parameters\n")
        f.write("TIP: For Stable Diffusion, use both positive and negative prompts\n")
        f.write("TIP: For best results, generate 2-3 variations and pick the best\n")
    
    print(f"💾 Prompts saved to: {filename}")
    return filename


def test_single_image():
    """Test: Generate prompts for a single image"""
    print("\n" + "="*70)
    print("TEST 1: SINGLE HIGH-QUALITY IMAGE PROMPT GENERATION")
    print("="*70)
    
    topic = "Artificial Intelligence in Healthcare"
    section = "AI-Powered Diagnostic Systems and Medical Imaging"
    
    prompts = generate_premium_image_prompts(topic, section)
    
    if prompts:
        print("\n" + "-"*70)
        print("GENERATED PROMPTS:")
        print("-"*70)
        print(prompts)
        print("-"*70 + "\n")
        
        filename = save_prompts(topic, section, prompts)
        print(f"\n✅ Test Complete! Check: {filename}")
    else:
        print("\n❌ Test Failed")


def test_multiple_images():
    """Test: Generate prompts for multiple sections"""
    print("\n" + "="*70)
    print("TEST 2: MULTIPLE IMAGE PROMPTS GENERATION")
    print("="*70)
    
    topic = "Machine Learning Fundamentals"
    sections = [
        "Introduction to Neural Networks",
        "Supervised vs Unsupervised Learning Comparison",
        "Deep Learning Architecture and Layers",
        "Model Training and Optimization Process"
    ]
    
    results = []
    
    for i, section in enumerate(sections, 1):
        print(f"\n[{i}/{len(sections)}] Processing: {section}")
        
        prompts = generate_premium_image_prompts(topic, section)
        
        if prompts:
            filename = save_prompts(topic, section, prompts)
            results.append({
                'section': section,
                'file': filename,
                'success': True
            })
        else:
            results.append({
                'section': section,
                'file': None,
                'success': False
            })
        
        # Rate limiting
        if i < len(sections):
            time.sleep(3)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r['success'])
    print(f"✅ Successfully generated: {successful}/{len(sections)}")
    
    print("\nGenerated files:")
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {result['section']}")
        if result['file']:
            print(f"     → {result['file']}")
    
    print("\n" + "="*70 + "\n")


def test_genre_specific():
    """Test: Different genres produce different styles"""
    print("\n" + "="*70)
    print("TEST 3: GENRE-SPECIFIC STYLE GENERATION")
    print("="*70)
    
    test_cases = [
        ("Machine Learning Algorithms", "Neural Network Architecture", "technology"),
        ("Human Anatomy Guide", "The Cardiovascular System", "healthcare"),
        ("Quantum Physics Explained", "Wave-Particle Duality", "science"),
        ("Business Strategy Handbook", "Competitive Analysis Framework", "business")
    ]
    
    for topic, section, expected_genre in test_cases:
        print(f"\n{'─'*70}")
        print(f"Topic: {topic}")
        print(f"Expected Genre: {expected_genre.title()}")
        
        detected = detect_genre(topic)
        match = "✓" if detected == expected_genre else "✗"
        print(f"Detected Genre: {detected.title()} {match}")
        
        if detected in PREMIUM_STYLES:
            style = PREMIUM_STYLES[detected]
            print(f"Style: {style['aesthetic']}")
            print(f"Colors: {style['colors']}")
        
        time.sleep(1)
    
    print("\n" + "="*70 + "\n")


def main():
    """Run comprehensive high-quality image prompt generation tests"""
    
    print("\n" + "="*70)
    print("HIGH-QUALITY IMAGE PROMPT GENERATOR")
    print("For DALL-E 3, Midjourney, Stable Diffusion, Leonardo.AI")
    print("="*70)
    
    # Run tests
    test_single_image()
    
    print("\n" + "─"*70)
    input("\nPress Enter to continue to Test 2 (Multiple Images)...")
    
    test_multiple_images()
    
    print("\n" + "─"*70)
    input("\nPress Enter to continue to Test 3 (Genre Detection)...")
    
    test_genre_specific()
    
    # Final message
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE!")
    print("="*70)
    print("\n📁 Check the 'image_prompts/' directory for generated prompt files")
    print("📝 Each file contains ready-to-use prompts for 4 different AI tools")
    print("🎨 Copy-paste prompts directly into your chosen image generator")
    print("\n✨ Tips for best results:")
    print("   • Generate 2-3 variations of each image")
    print("   • Use Midjourney for artistic style")
    print("   • Use DALL-E 3 for precise descriptions")
    print("   • Use Stable Diffusion for fine control")
    print("   • Use Leonardo.AI for ease of use")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
