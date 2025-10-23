#!/usr/bin/env python3
"""
Image Generation using Vertex AI Imagen 4.0 Ultra
Uses Google Cloud's Vertex AI API for highest quality image generation
"""

import os
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64

# Vertex AI imports
from google import genai
from google.genai import types

# Configure Vertex AI with API key
GEMINI_API_KEY = "AIzaSyBW3GE8dH4UexMymdK8FatlS-AsE_9JLB8"

# Initialize client
client = genai.Client(api_key=GEMINI_API_KEY)

# Available Gemini image generation models (work without billing!)
IMAGE_MODELS = {
    "preview": "gemini-2.0-flash-preview-image-generation",      # Preview model - BEST
    "experimental": "gemini-2.0-flash-exp-image-generation",     # Experimental model
    "ultra": "gemini-2.5-flash-image",                           # Latest Gemini 2.5
    "flash-preview": "gemini-2.5-flash-image-preview"            # Flash preview
}

DEFAULT_MODEL = "preview"  # Gemini 2.0 Flash Preview Image - No billing required!

# Genre-specific styles
GENRE_STYLES = {
    "technology": {
        "style": "modern tech illustration, sleek futuristic design",
        "colors": "deep blues, cyan, white, silver",
        "mood": "innovative, cutting-edge, professional"
    },
    "healthcare": {
        "style": "medical illustration, clean clinical design",
        "colors": "medical blue, mint green, white",
        "mood": "caring, professional, trustworthy"
    },
    "science": {
        "style": "scientific diagram, detailed technical illustration",
        "colors": "scientific color-coding, high contrast",
        "mood": "analytical, precise, educational"
    },
    "business": {
        "style": "professional infographic, corporate design",
        "colors": "navy blue, gold, white",
        "mood": "professional, authoritative, trustworthy"
    },
    "education": {
        "style": "educational illustration, friendly design",
        "colors": "warm colors, balanced palette",
        "mood": "approachable, clear, engaging"
    },
    "finance": {
        "style": "financial visualization, clean professional design",
        "colors": "dark green, gold, navy",
        "mood": "secure, professional, sophisticated"
    },
    "environment": {
        "style": "environmental illustration, natural design",
        "colors": "earth tones, greens, blues",
        "mood": "sustainable, natural, hopeful"
    },
    "general": {
        "style": "clean modern illustration",
        "colors": "balanced color palette",
        "mood": "professional, accessible"
    }
}


def detect_genre(topic):
    """Detect genre from topic"""
    topic_lower = topic.lower()
    
    genre_keywords = {
        "technology": ["technology", "tech", "ai", "artificial intelligence", "machine learning", 
                      "software", "digital", "cyber", "data", "computing", "algorithm"],
        "healthcare": ["health", "medical", "healthcare", "medicine", "clinical", "patient", 
                      "treatment", "diagnosis", "therapy", "wellness"],
        "science": ["science", "scientific", "research", "physics", "chemistry", "biology", 
                   "quantum", "laboratory", "experiment"],
        "business": ["business", "management", "leadership", "strategy", "corporate", 
                    "entrepreneurship", "marketing", "sales"],
        "education": ["education", "learning", "teaching", "academic", "school", "university", 
                     "training", "curriculum"],
        "finance": ["finance", "financial", "investment", "banking", "economics", "trading", 
                   "cryptocurrency", "blockchain"],
        "environment": ["environment", "climate", "sustainability", "green", "ecological", 
                       "conservation", "renewable"]
    }
    
    for genre, keywords in genre_keywords.items():
        if any(keyword in topic_lower for keyword in keywords):
            return genre
    
    return "general"


def generate_optimized_prompt(topic, section, genre):
    """Generate ultra-optimized prompt for Imagen"""
    style = GENRE_STYLES[genre]
    
    prompt = f"""Ultra-high-quality professional illustration for: {section}

Context: {topic}

Visual Style: {style['style']}
Color Palette: {style['colors']}
Mood: {style['mood']}

Technical Requirements:
- Publication-ready quality
- 16:9 aspect ratio
- Professional composition
- Clear visual hierarchy
- Publication standards
- 8K resolution rendering
- Photorealistic where appropriate
- Clean, modern aesthetic

Focus: Create a compelling visual that clearly represents the concept while maintaining 
professional publishing standards. Avoid text overlays."""
    
    return prompt


def generate_image_with_vertex(prompt, output_path, model_name="ultra"):
    """
    Generate image using Vertex AI Imagen API
    
    Args:
        prompt: Image generation prompt
        output_path: Where to save the image
        model_name: Which model to use (ultra, standard, fast, imagen-3)
    
    Returns:
        tuple: (success, message, image_path)
    """
    print(f"\n{'='*70}")
    print(f"🎨 Generating Image with Gemini")
    print(f"{'='*70}")
    print(f"Model: {IMAGE_MODELS.get(model_name, model_name)}")
    print(f"Output: {output_path}")
    print(f"{'='*70}\n")
    
    try:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        print("⏳ Generating high-quality image...")
        print(f"   Using: {IMAGE_MODELS[model_name]}")
        
        # Generate image using generateContent API (for Gemini image models)
        # These models require BOTH text and image modalities
        response = client.models.generate_content(
            model=IMAGE_MODELS[model_name],
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["TEXT", "IMAGE"]
            )
        )
        
        # Extract and save image
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            # Found image data
                            image_data = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            
                            print(f"   Found image: {mime_type}")
                            
                            # Decode base64 if needed
                            if isinstance(image_data, str):
                                image_bytes = base64.b64decode(image_data)
                            else:
                                image_bytes = image_data
                            
                            # Convert to PIL Image and save
                            pil_image = Image.open(BytesIO(image_bytes))
                            pil_image.save(output_path)
                            
                            size = os.path.getsize(output_path)
                            width, height = pil_image.size
                            
                            print(f"\n✅ High-quality image generated successfully!")
                            print(f"   File: {output_path}")
                            print(f"   Size: {size:,} bytes ({size/1024:.1f} KB)")
                            print(f"   Dimensions: {width}x{height}")
                            print(f"   Model: {IMAGE_MODELS[model_name]}")
                            print(f"   Quality: HIGH (Gemini 2.0)")
                            
                            return True, "Image generated successfully", output_path
        
        print("⚠️  No image data found in response")
        print(f"Response structure: {response}")
        return False, "No image data in response", None
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error generating image: {error_msg}")
        
        # Handle specific errors
        if "quota" in error_msg.lower() or "rate" in error_msg.lower():
            print("\n💡 Quota limit reached. Suggestions:")
            print("   • Wait a few seconds and retry")
            print("   • Use 'fast' model instead of 'ultra'")
            print("   • Check API quota limits")
        elif "permission" in error_msg.lower() or "auth" in error_msg.lower():
            print("\n💡 Authentication issue. Check:")
            print("   • API key is correct")
            print("   • Vertex AI API is enabled")
            print("   • Billing is enabled (if required)")
        elif "not found" in error_msg.lower():
            print("\n💡 Model not accessible. Try:")
            print("   • Using 'fast' or 'standard' model")
            print("   • Checking model availability in your region")
        
        return False, error_msg, None


def test_single_image():
    """Test: Generate a single ultra-quality image"""
    print("\n" + "="*70)
    print("TEST 1: SINGLE ULTRA-QUALITY IMAGE")
    print("="*70)
    
    topic = "Artificial Intelligence in Healthcare"
    section = "AI-Powered Diagnostic Systems"
    
    genre = detect_genre(topic)
    print(f"\n📊 Detected Genre: {genre.title()}")
    print(f"   Style: {GENRE_STYLES[genre]['style']}")
    
    # Generate prompt
    prompt = generate_optimized_prompt(topic, section, genre)
    
    print(f"\n📝 Generated Prompt:")
    print(f"{'-'*70}")
    print(prompt[:500] + "..." if len(prompt) > 500 else prompt)
    print(f"{'-'*70}\n")
    
    # Generate image with preview model
    output_path = "test_healthcare_diagnostic_preview.png"
    success, message, path = generate_image_with_vertex(
        prompt, 
        output_path,
        model_name="preview"  # Using gemini-2.0-flash-preview-image-generation
    )
    
    if success:
        print(f"\n✅ TEST PASSED")
        print(f"   Image saved to: {path}")
    else:
        print(f"\n⚠️  TEST FAILED WITH PREVIEW MODEL")
        print(f"   Reason: {message}")
        print(f"\n   Trying with EXPERIMENTAL model as fallback...")
        
        # Try experimental model
        output_path_exp = "test_healthcare_diagnostic_experimental.png"
        success_exp, message_exp, path_exp = generate_image_with_vertex(
            prompt,
            output_path_exp,
            model_name="experimental"
        )
        
        if success_exp:
            print(f"\n✅ FALLBACK SUCCESSFUL")
            print(f"   Image saved to: {path_exp}")
            return True
        else:
            print(f"\n❌ FALLBACK ALSO FAILED: {message_exp}")
    
    return success


def test_multiple_images():
    """Test: Generate multiple images"""
    print("\n" + "="*70)
    print("TEST 2: MULTIPLE IMAGE GENERATION")
    print("="*70)
    
    topic = "Machine Learning Fundamentals"
    sections = [
        "Introduction to Neural Networks",
        "Supervised vs Unsupervised Learning",
        "Deep Learning Architecture"
    ]
    
    genre = detect_genre(topic)
    print(f"\n📊 Topic Genre: {genre.title()}")
    
    os.makedirs("generated_images_vertex", exist_ok=True)
    
    results = []
    
    for i, section in enumerate(sections, 1):
        print(f"\n[{i}/{len(sections)}] Processing: {section}")
        
        # Generate prompt
        prompt = generate_optimized_prompt(topic, section, genre)
        
        # Generate filename
        safe_name = section.lower().replace(' ', '_')[:40]
        output_path = f"generated_images_vertex/{i:02d}_{safe_name}.png"
        
        # Generate image
        success, message, path = generate_image_with_vertex(
            prompt,
            output_path,
            model_name="preview"  # Use preview for batch generation
        )
        
        results.append({
            'section': section,
            'success': success,
            'path': path,
            'message': message
        })
        
        # Rate limiting
        if i < len(sections):
            print("\n⏳ Waiting 3 seconds (rate limiting)...")
            time.sleep(3)
    
    # Summary
    print(f"\n{'='*70}")
    print("BATCH GENERATION COMPLETE")
    print(f"{'='*70}")
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Successful: {successful}/{len(results)}")
    
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['section']}")
        if r['success']:
            print(f"   → {r['path']}")
    
    return successful == len(results)


def main():
    """Run comprehensive tests"""
    
    print("\n" + "="*70)
    print("GEMINI 2.5 IMAGE GENERATION - HIGH QUALITY")
    print("="*70)
    
    print("\n📋 Available Models:")
    for key, model in IMAGE_MODELS.items():
        quality = "🌟 BEST" if key == "preview" else "🧪 EXPERIMENTAL" if key == "experimental" else ""
        print(f"   • {key}: {model} {quality}")
    
    print("\n💡 Using Gemini image generation models")
    print("   ✅ No billing required!")
    print("   ✅ High-quality image generation")
    print("   ⚠️  Imagen 4.0 requires GCP billing (not used here)")
    
    # Test 1: Single ultra-quality image
    input("\n\nPress Enter to start Test 1 (Ultra Quality Image)...")
    success1 = test_single_image()
    
    # Test 2: Multiple images
    if success1:
        input("\n\nPress Enter to continue to Test 2 (Batch Generation)...")
        success2 = test_multiple_images()
    else:
        print("\n⚠️  Skipping Test 2 due to Test 1 failure")
        success2 = False
    
    # Final summary
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE!")
    print("="*70)
    print(f"\n✅ Test 1 (Single Image): {'PASSED' if success1 else 'FAILED'}")
    print(f"{'✅' if success2 else '⚠️ '} Test 2 (Batch): {'PASSED' if success2 else 'SKIPPED/FAILED'}")
    
    print("\n📁 Generated files:")
    print("   • test_healthcare_diagnostic_preview.png (or _experimental.png)")
    print("   • generated_images_vertex/ (batch images)")
    
    print("\n✨ All images are publication-ready, high-quality outputs")
    print("   Generated using Gemini 2.0 Flash Preview Image Generation")
    print("   No billing required!")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
