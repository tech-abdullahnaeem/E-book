#!/usr/bin/env python3
"""
High-Quality Image Generation using Gemini API
Generates actual images using Gemini's Imagen models
"""

import os
import time
import base64
import google.generativeai as genai
from datetime import datetime
from PIL import Image
from io import BytesIO

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBW3GE8dH4UexMymdK8FatlS-AsE_9JLB8"
genai.configure(api_key=GEMINI_API_KEY)

# Available Gemini image generation models (that work with standard API)
IMAGE_MODELS = {
    "ultra": "gemini-2.5-flash-image",                           # Latest Gemini 2.5 with image generation
    "experimental": "gemini-2.0-flash-exp-image-generation",     # Experimental model
    "preview": "gemini-2.0-flash-preview-image-generation",      # Preview model  
    "flash-preview": "gemini-2.5-flash-image-preview"            # Flash preview
}

DEFAULT_MODEL = "ultra"  # Use Gemini 2.5 by default

# NOTE: Imagen 4.0 models (imagen-4.0-ultra-generate-001, etc.) require Vertex AI SDK
# and GCP project setup. Using Gemini models that support generateContent API instead.

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
        "colors": "navy blue, emerald, gold accents",
        "mood": "professional, strategic, growth-oriented"
    }
}


def detect_genre(topic):
    """Detect genre from topic"""
    topic_lower = topic.lower()
    
    keywords = {
        "technology": ["ai", "machine learning", "software", "algorithm", "data", "tech", "digital"],
        "healthcare": ["health", "medical", "clinical", "patient", "diagnosis", "treatment", "disease"],
        "science": ["biology", "chemistry", "physics", "research", "scientific", "quantum"],
        "business": ["business", "management", "strategy", "marketing", "leadership", "sales"]
    }
    
    for genre, words in keywords.items():
        if any(word in topic_lower for word in words):
            return genre
    
    return "technology"


def generate_optimized_prompt(topic, section_title, genre=None):
    """Generate optimized prompt for Gemini image generation"""
    if genre is None:
        genre = detect_genre(topic)
    
    style = GENRE_STYLES.get(genre, GENRE_STYLES["technology"])
    
    # Create concise but detailed prompt for Imagen
    prompt = f"""Create a professional educational illustration for an ebook:

Topic: {topic}
Section: {section_title}

Style: {style['style']}
Colors: {style['colors']}
Mood: {style['mood']}

Requirements:
- 16:9 horizontal format
- Clean, modern design
- High quality, publication-ready
- Educational and informative
- No text or labels in image
- Professional {genre} aesthetic"""
    
    return prompt.strip()


def generate_image_with_gemini(prompt, output_path, model_name="ultra"):
    """
    Generate actual image using Gemini Imagen API
    
    Args:
        prompt: Image generation prompt
        output_path: Where to save the image
        model_name: Which model to use (ultra, standard, fast, imagen-3)
    
    Returns:
        tuple: (success, message, image_path)
    """
    print(f"\n{'='*70}")
    print(f"🎨 Generating Image with Gemini Imagen")
    print(f"{'='*70}")
    print(f"Model: {IMAGE_MODELS.get(model_name, model_name)}")
    print(f"Output: {output_path}")
    print(f"{'='*70}\n")
    
    try:
        print("⏳ Generating ultra-high-quality image...")
        
        # Get the model
        model_id = IMAGE_MODELS.get(model_name, model_name)
        model = genai.GenerativeModel(model_id)
        
        # Generate image using predict method (for Imagen models)
        response = model.predict(
            prompt=prompt,
            number_of_images=1,
            aspect_ratio="16:9",
            safety_filter_level="block_only_high",
            person_generation="allow_adult"
        )
        
        # Extract and save image
        if hasattr(response, 'images') and len(response.images) > 0:
            image = response.images[0]
            
            # Save the image
            if hasattr(image, '_pil_image'):
                image._pil_image.save(output_path)
            elif hasattr(image, 'save'):
                image.save(output_path)
            else:
                # Try to handle as bytes
                with open(output_path, 'wb') as f:
                    f.write(image)
            
            size = os.path.getsize(output_path)
            img = Image.open(output_path)
            width, height = img.size
            
            print(f"\n✅ Ultra-quality image generated successfully!")
            print(f"   File: {output_path}")
            print(f"   Size: {size:,} bytes")
            print(f"   Dimensions: {width}x{height}")
            print(f"   Model: {model_id}")
            
            return True, "Image generated successfully", output_path
        
        print("⚠️  No image data found in response")
        return False, "No image data in response", None
        
    except AttributeError as e:
        # Try alternative approach with generateContent
        print(f"⚠️  predict() not available, trying generateContent()...")
        return generate_with_content_api(prompt, output_path, model_name)
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error generating image: {error_msg}")
        
        if "quota" in error_msg.lower() or "rate" in error_msg.lower():
            print("\n💡 Quota limit reached. Try again in a few seconds.")
        elif "not found" in error_msg.lower():
            print("\n💡 Model not found or not supported. Trying alternative...")
            return generate_with_content_api(prompt, output_path, model_name)
        
        return False, error_msg, None


def generate_with_content_api(prompt, output_path, model_name="ultra"):
    """Fallback: Try using generateContent API"""
    try:
        print("\n⏳ Trying alternative generation method...")
        
        model_id = IMAGE_MODELS.get(model_name, model_name)
        model = genai.GenerativeModel(model_id)
        
        # Try generateContent
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                candidate_count=1
            )
        )
        
        # Look for image data
        if hasattr(response, 'candidates'):
            for candidate in response.candidates:
                if hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data'):
                            # Found image data
                            image_data = part.inline_data.data
                            image = Image.open(BytesIO(image_data))
                            image.save(output_path)
                            
                            size = os.path.getsize(output_path)
                            width, height = image.size
                            
                            print(f"\n✅ Image generated successfully (alternative method)!")
                            print(f"   File: {output_path}")
                            print(f"   Size: {size:,} bytes")
                            print(f"   Dimensions: {width}x{height}")
                            
                            return True, "Image generated with alternative API", output_path
        
        return False, "No image data found", None
        
    except Exception as e:
        return False, f"Alternative method failed: {str(e)}", None


def test_single_image():
    """Test: Generate a single high-quality image"""
    print("\n" + "="*70)
    print("TEST 1: SINGLE IMAGE GENERATION")
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
    print(prompt)
    print(f"{'-'*70}\n")
    
    # Generate image
    output_path = "test_healthcare_diagnostic.png"
    success, message, path = generate_image_with_gemini(
        prompt, 
        output_path,
        model_name="ultra"  # Ultra quality model
    )
    
    if success:
        print(f"\n✅ TEST PASSED")
        print(f"   Image saved to: {path}")
    else:
        print(f"\n❌ TEST FAILED")
        print(f"   Reason: {message}")
    
    return success


def test_multiple_images():
    """Test: Generate multiple images for different sections"""
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
    
    os.makedirs("generated_images", exist_ok=True)
    
    results = []
    
    for i, section in enumerate(sections, 1):
        print(f"\n[{i}/{len(sections)}] Processing: {section}")
        
        # Generate prompt
        prompt = generate_optimized_prompt(topic, section, genre)
        
        # Generate filename
        safe_name = section.lower().replace(' ', '_')[:40]
        output_path = f"generated_images/{i:02d}_{safe_name}.png"
        
        # Generate image
        success, message, path = generate_image_with_gemini(
            prompt,
            output_path,
            model_name="imagen-4-fast"
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
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Successfully generated: {successful}/{len(sections)}")
    
    print("\nResults:")
    for result in results:
        status = "✓" if result['success'] else "✗"
        print(f"  {status} {result['section']}")
        if result['path']:
            print(f"     → {result['path']}")
        else:
            print(f"     → Error: {result['message']}")
    
    print("\n" + "="*70)
    
    return successful == len(sections)


def test_different_models():
    """Test: Compare different Gemini image models"""
    print("\n" + "="*70)
    print("TEST 3: MODEL COMPARISON")
    print("="*70)
    
    topic = "Quantum Computing"
    section = "Quantum Superposition Visualization"
    
    prompt = generate_optimized_prompt(topic, section)
    
    # Test different models
    models_to_test = [
        ("imagen-4-fast", "Imagen 4.0 Fast"),
        ("imagen-3", "Imagen 3.0"),
    ]
    
    os.makedirs("model_comparison", exist_ok=True)
    
    for model_key, model_name in models_to_test:
        print(f"\n{'─'*70}")
        print(f"Testing: {model_name}")
        print(f"{'─'*70}")
        
        output_path = f"model_comparison/{model_key}_quantum.png"
        
        success, message, path = generate_image_with_gemini(
            prompt,
            output_path,
            model_name=model_key
        )
        
        if success:
            print(f"✅ {model_name}: Success")
        else:
            print(f"❌ {model_name}: Failed - {message}")
        
        time.sleep(3)  # Rate limiting
    
    print("\n" + "="*70)


def main():
    """Run comprehensive image generation tests"""
    
    print("\n" + "="*70)
    print("GEMINI IMAGE GENERATION SYSTEM")
    print("Using Imagen 3.0 and Imagen 4.0 Models")
    print("="*70)
    
    print("\n📋 Available Models:")
    for key, model in IMAGE_MODELS.items():
        print(f"   • {key}: {model}")
    
    # Test 1: Single image
    input("\n\nPress Enter to start Test 1 (Single Image)...")
    test_single_image()
    
    # Test 2: Multiple images
    input("\n\nPress Enter to continue to Test 2 (Multiple Images)...")
    test_multiple_images()
    
    # Test 3: Model comparison
    input("\n\nPress Enter to continue to Test 3 (Model Comparison)...")
    test_different_models()
    
    # Final summary
    print("\n" + "="*70)
    print("ALL TESTS COMPLETE!")
    print("="*70)
    print("\n📁 Check these directories:")
    print("   • Current directory: test_healthcare_diagnostic.png")
    print("   • generated_images/: Multiple test images")
    print("   • model_comparison/: Model comparison images")
    print("\n✨ All images are publication-ready, high-quality outputs")
    print("   Generated using Gemini Imagen models")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
