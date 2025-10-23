#!/usr/bin/env python3
"""
Working Gemini Image Generation
Uses Gemini 2.x image generation models
"""

import os
import time
import google.generativeai as genai
from PIL import Image
from io import BytesIO

# Configure API
GEMINI_API_KEY = "AIzaSyBW3GE8dH4UexMymdK8FatlS-AsE_9JLB8"
genai.configure(api_key=GEMINI_API_KEY)

# Working models (use generateContent)
WORKING_MODELS = {
    "gemini-2.5-flash": "gemini-2.5-flash-image",
    "gemini-2.0-flash": "gemini-2.0-flash-exp-image-generation",
    "gemini-2.0-preview": "gemini-2.0-flash-preview-image-generation"
}

# Genre styles
GENRE_STYLES = {
    "technology": "modern tech illustration, sleek futuristic design, deep blues and cyan, 16:9",
    "healthcare": "medical illustration, clean clinical design, medical blue and mint green, 16:9",
    "science": "scientific diagram, detailed technical illustration, high contrast colors, 16:9",
    "business": "professional infographic, corporate design, navy blue and gold, 16:9"
}


def detect_genre(topic):
    """Detect genre"""
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ["health", "medical", "clinical", "patient"]):
        return "healthcare"
    elif any(w in topic_lower for w in ["business", "management", "strategy"]):
        return "business"
    elif any(w in topic_lower for w in ["biology", "chemistry", "physics", "science"]):
        return "science"
    else:
        return "technology"


def generate_image(prompt, output_path="generated_image.png", model_key="gemini-2.5-flash"):
    """
    Generate image using Gemini
    
    Returns: (success, message, path)
    """
    print(f"\n{'='*70}")
    print(f"🎨 Generating Image")
    print(f"{'='*70}")
    print(f"Model: {WORKING_MODELS[model_key]}")
    print(f"Output: {output_path}")
    
    try:
        print("\n⏳ Generating...")
        
        model = genai.GenerativeModel(WORKING_MODELS[model_key])
        response = model.generate_content(prompt)
        
        # Check response
        if not response or not response.candidates:
            return False, "No response from model", None
        
        # Extract image
        candidate = response.candidates[0]
        if not hasattr(candidate.content, 'parts'):
            return False, "No image parts in response", None
        
        # Find image data
        for part in candidate.content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                # Save image
                image_bytes = part.inline_data.data
                
                with open(output_path, 'wb') as f:
                    f.write(image_bytes)
                
                # Verify
                img = Image.open(output_path)
                width, height = img.size
                size = os.path.getsize(output_path)
                
                print(f"\n✅ Success!")
                print(f"   File: {output_path}")
                print(f"   Size: {width}x{height} ({size:,} bytes)")
                
                return True, "Generated successfully", output_path
        
        return False, "No image data found", None
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False, str(e), None


def test_basic():
    """Test basic generation"""
    print("\n" + "="*70)
    print("TEST: Basic Image Generation")
    print("="*70)
    
    prompt = "Create a professional tech illustration: AI neural network diagram with nodes and connections, modern blue gradient, 16:9 horizontal format, clean design"
    
    success, msg, path = generate_image(prompt, "test_basic.png")
    
    if success:
        print(f"\n✅ TEST PASSED - Image saved: {path}")
    else:
        print(f"\n❌ TEST FAILED - {msg}")
    
    return success


def test_with_topic():
    """Test with ebook topic"""
    print("\n" + "="*70)
    print("TEST: Ebook Topic Image")
    print("="*70)
    
    topic = "Machine Learning in Healthcare"
    section = "AI Diagnostic Systems"
    
    genre = detect_genre(topic)
    style = GENRE_STYLES[genre]
    
    prompt = f"""Create a professional illustration for an educational ebook:

Topic: {topic}
Section: {section}

Style: {style}

Show: AI analyzing medical images, doctor with digital display, modern hospital setting
Requirements: Professional, educational, high quality, no text in image"""
    
    print(f"\nGenre: {genre}")
    print(f"Prompt: {prompt[:100]}...")
    
    success, msg, path = generate_image(prompt, "test_healthcare.png")
    
    if success:
        print(f"\n✅ TEST PASSED - Image saved: {path}")
    else:
        print(f"\n❌ TEST FAILED - {msg}")
    
    return success


def main():
    """Run tests"""
    print("\n" + "="*70)
    print("GEMINI IMAGE GENERATION - WORKING VERSION")
    print("="*70)
    
    print("\n📋 Using model: gemini-2.5-flash-image")
    print("   This model supports generateContent for images\n")
    
    # Test 1
    input("Press Enter to run Test 1 (Basic)...")
    test1 = test_basic()
    
    if test1:
        time.sleep(2)
        
        # Test 2
        input("\n\nPress Enter to run Test 2 (Healthcare)...")
        test2 = test_with_topic()
    
    print("\n" + "="*70)
    print("TESTS COMPLETE")
    print("="*70)
    print("\n📁 Check generated files:")
    print("   • test_basic.png")
    print("   • test_healthcare.png")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
