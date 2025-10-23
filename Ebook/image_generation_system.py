#!/usr/bin/env python3
"""
Two-Stage Image Generation System for Ebooks
Stage 1: Generate highly detailed, pixel-level prompts using Gemini text model
Stage 2: Generate images using those detailed prompts with Gemini image model
"""

import os
import time
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64
import json

# Import both APIs
import google.generativeai as genai_text  # For text generation
from google import genai  # For image generation
from google.genai import types

# Configuration
GEMINI_API_KEY = "AIzaSyBW3GE8dH4UexMymdK8FatlS-AsE_9JLB8"

# Configure text generation
genai_text.configure(api_key=GEMINI_API_KEY)

# Configure image generation
image_client = genai.Client(api_key=GEMINI_API_KEY)

# Models
TEXT_MODEL = "gemini-2.0-flash-exp"  # For generating detailed prompts
IMAGE_MODEL = "gemini-2.0-flash-preview-image-generation"  # For generating images

# Photorealistic rendering styles (inspired by Slidexy)
RENDERING_STYLES = {
    "photorealistic": {
        "description": "Professional stock photography style with perfect lighting, diverse professionals, "
                      "modern workspace, and polished commercial aesthetic. Magazine-quality composition "
                      "with award-winning visual design.",
        "technical": "professional photography, DSLR quality, f/2.8 aperture, 50mm lens, perfect lighting, "
                    "sharp focus, commercial quality, 8K resolution, masterpiece quality",
        "quality_keywords": ["masterpiece quality", "professional presentation grade", "ultra high definition 8K",
                           "magazine-quality composition", "award-winning visual design", "crisp clarity",
                           "rich color depth", "perfect exposure balance", "intricate fine details"]
    },
    "3d_cgi": {
        "description": "Ultra-photorealistic 3D CGI rendering with physically accurate ray-traced lighting, "
                      "perfect material properties (metalness, roughness, subsurface scattering), "
                      "crisp reflections, and studio-quality presentation",
        "technical": "path-traced global illumination, PBR materials with 4K textures, anti-aliased edges, "
                    "studio HDRI lighting, Cycles/Octane render quality, physically based rendering",
        "quality_keywords": ["photorealistic 3D render", "ray-traced lighting", "PBR materials", 
                           "studio quality", "ultra-detailed CGI", "perfect material properties"]
    },
    "illustration": {
        "description": "Professional digital illustration with artistic flair, balanced between realism and style",
        "technical": "digital painting, high-resolution artwork, professional illustration techniques",
        "quality_keywords": ["professional illustration", "artistic excellence", "polished execution"]
    }
}

# Character quality standards (from Slidexy)
CHARACTER_REQUIREMENTS = """
PHOTOREALISTIC CHARACTER STANDARDS (MANDATORY):
- Photorealistic skin tones with natural subsurface scattering and pore detail
- Anatomically correct facial features: proper eye spacing, nose proportions, lip structure
- Natural body proportions following human anatomy (7.5-8 head heights for adults)
- Diverse representation REQUIRED:
  * Ethnicities: Include varied Asian, African, Caucasian, Hispanic, Middle Eastern features
  * Genders: Balanced male/female/non-binary representation where applicable
  * Ages: Appropriate age range (20s-60s for professional contexts)
  * Body types: Realistic variety in build and stature
- Professional attire appropriate to context:
  * Business: suits, smart casual, appropriate industry dress codes
  * Healthcare: medical scrubs, lab coats, professional medical attire
  * Tech: smart casual, modern professional wear
- Authentic expressions and micro-expressions:
  * Natural eye contact and gaze direction
  * Genuine smiles with appropriate crow's feet and cheek lift
  * Context-appropriate emotional states
- Natural gestures and body language:
  * Relaxed, confident postures
  * Purposeful hand positions and gestures
  * Realistic weight distribution and balance
- Proper depth placement in scene:
  * Realistic size perspective (closer = larger)
  * Appropriate depth of field focus
  * Natural interaction with environment and lighting
- Environmental integration:
  * Realistic shadows cast by and on characters
  * Appropriate lighting interaction (skin highlights, clothing folds)
  * Natural interaction with props and surroundings
"""

# Genre-specific visual characteristics (enhanced with photorealism)
GENRE_CHARACTERISTICS = {
    "technology": {
        "color_palette": "Deep navy blue (#1a1f3a) as base, electric cyan (#00d9ff) for highlights, "
                        "silver (#c0c0c0) for metallic elements, pure white (#ffffff) for contrast, "
                        "subtle purple (#8b5cf6) for depth",
        "visual_style": "Ultra-photorealistic 3D CGI or professional photography. Futuristic, sleek, "
                       "minimalist with geometric precision. Sharp edges, clean lines, isometric perspectives. "
                       "Ray-traced reflections, PBR materials, studio lighting",
        "lighting": "Professional three-point lighting: key light (6500K, high intensity), fill light (30% intensity), "
                   "rim light for edge definition. Subtle neon glow effects, dramatic highlights on metallic surfaces",
        "composition": "Rule of thirds with central focal point, negative space for modern feel, "
                      "layered depth with foreground-midground-background separation. Magazine-quality framing",
        "texture": "Photorealistic materials: glossy metallic surfaces (metalness: 0.9, roughness: 0.1), "
                  "matte carbon fiber, translucent glass with ray-traced reflections, PBR textures at 4K",
        "rendering_style": "3d_cgi"
    },
    "healthcare": {
        "color_palette": "Medical blue (#0077be) as primary, mint green (#98e5d1) for healing, "
                        "clean white (#ffffff) for sterility, soft gray (#e8eaed) for neutrality, "
                        "warm peach (#ffcba4) for human touch",
        "visual_style": "Professional stock photography style. Photorealistic medical professionals with diverse "
                       "representation, modern healthcare facilities, clean clinical environments. "
                       "Scientific accuracy with approachable, human-centered aesthetics",
        "lighting": "Professional medical photography lighting: soft key light (5500K natural), "
                   "gentle fill (40% intensity), subtle rim lighting. No harsh shadows, perfect exposure balance",
        "composition": "Magazine-quality healthcare photography. Balanced symmetry for trust, diverse professionals "
                      "in natural poses, clear visual hierarchy, professional depth of field (f/2.8)",
        "texture": "Photorealistic medical materials: smooth medical-grade plastics, fabric textures on scrubs, "
                  "natural skin tones with proper subsurface scattering, clinical surfaces with realistic reflectivity",
        "rendering_style": "photorealistic",
        "characters_required": True,
        "character_context": "Diverse medical professionals (doctors, nurses, technicians) in appropriate medical "
                           "attire, natural expressions showing care and professionalism"
    },
    "science": {
        "color_palette": "Scientific blue (#0066cc) for knowledge, emerald green (#50c878) for biology, "
                        "amber (#ffbf00) for chemistry, deep purple (#6a0dad) for physics, white (#ffffff) for clarity",
        "visual_style": "Analytical, precise, educational. Technical diagrams with artistic flair, "
                       "cross-sections, molecular structures, data visualization elements",
        "lighting": "Laboratory lighting - bright and even, strategic spotlights on key elements, "
                   "subtle color-coded lighting for different scientific domains",
        "composition": "Organized grid layouts, clear labeling areas, systematic arrangement, "
                      "scientific accuracy in spatial relationships",
        "texture": "Graph paper subtlety, microscopic textures, crystalline structures, "
                  "smooth scientific instruments, detailed surface patterns"
    },
    "business": {
        "color_palette": "Navy blue (#002244) for authority, gold (#d4af37) for success, "
                        "charcoal gray (#36454f) for sophistication, white (#ffffff) for clarity, "
                        "forest green (#228b22) for growth",
        "visual_style": "Professional stock photography of diverse business professionals in modern office "
                       "environments. Corporate aesthetics with authentic human interaction, "
                       "award-winning commercial photography quality",
        "lighting": "Professional corporate photography lighting: three-point setup with key (5000K), "
                   "fill (35% intensity), and subtle rim light. Soft window light simulation for natural feel",
        "composition": "Magazine-quality business photography. Golden ratio proportions, diverse professionals "
                      "in natural collaborative poses, modern workspace environment, professional depth of field",
        "texture": "Photorealistic business materials: brushed metal office furniture, natural wood finishes, "
                  "glass surfaces with accurate reflections, fabric suits and professional attire, "
                  "realistic skin tones and diverse features",
        "rendering_style": "photorealistic",
        "characters_required": True,
        "character_context": "Diverse business professionals (various ages, ethnicities, genders) in modern "
                           "business attire, natural confident poses, authentic professional interactions"
    },
    "education": {
        "color_palette": "Warm orange (#ff8c42) for enthusiasm, sky blue (#87ceeb) for clarity, "
                        "grass green (#7cb342) for growth, sunny yellow (#ffd700) for optimism, "
                        "soft purple (#9370db) for creativity",
        "visual_style": "Friendly, accessible, engaging. Illustrated style with clean modern execution, "
                       "playful yet professional, clear information hierarchy",
        "lighting": "Bright, cheerful lighting, soft shadows, warm color temperature, "
                   "even illumination for clarity",
        "composition": "Dynamic but organized, visual flow guides the eye, whitespace for breathing room, "
                      "modular layout for easy understanding",
        "texture": "Smooth vector-like surfaces, subtle paper textures, chalkboard effects, "
                  "soft gradients, friendly rounded forms"
    },
    "finance": {
        "color_palette": "Deep green (#004d40) for wealth, gold (#cfb53b) for prosperity, "
                        "midnight blue (#191970) for security, silver (#aaa9ad) for stability, "
                        "white (#ffffff) for transparency",
        "visual_style": "Secure, sophisticated, data-driven. Clean charts and graphs, "
                       "architectural precision, luxury aesthetics",
        "lighting": "Controlled studio lighting, subtle highlights on metallic elements, "
                   "depth-creating shadows, professional ambiance",
        "composition": "Stable horizontal and vertical alignments, structured grid systems, "
                      "clear data visualization, premium spacing",
        "texture": "Polished marble, brushed gold, currency textures, glass and steel, "
                  "premium material finishes"
    },
    "environment": {
        "color_palette": "Forest green (#228b22) for nature, sky blue (#87ceeb) for air, "
                        "earth brown (#8b4513) for soil, ocean blue (#006994) for water, "
                        "sun gold (#ffd700) for energy",
        "visual_style": "Natural, organic, hopeful. Flowing forms, natural patterns, "
                       "sustainable aesthetics, connection between elements",
        "lighting": "Natural sunlight, golden hour warmth, soft atmospheric effects, "
                   "environmental ambient light, gentle shadows",
        "composition": "Organic flow, natural balance, ecosystem representation, "
                      "circular economy visualizations",
        "texture": "Natural materials, organic patterns, leaf veins, water ripples, "
                  "earth textures, plant structures"
    },
    "general": {
        "color_palette": "Balanced blue (#4a90e2) as primary, neutral gray (#808080) for stability, "
                        "white (#ffffff) for clarity, accent colors context-dependent",
        "visual_style": "Clean, modern, professional. Universal design principles, "
                       "clear communication, accessible aesthetics",
        "lighting": "Balanced three-point lighting, neutral color temperature, "
                   "professional illumination",
        "composition": "Classic design principles, clear hierarchy, balanced layout, "
                      "purposeful negative space",
        "texture": "Smooth professional surfaces, subtle depth, clean execution, "
                  "modern material design"
    }
}

# Content type visual specifications
CONTENT_TYPE_SPECS = {
    "process": "Step-by-step visual flow with numbered stages, directional arrows, "
               "progressive color intensity, left-to-right or top-to-bottom flow",
    "comparison": "Split-screen composition, mirror layout, contrasting colors for different sides, "
                 "central dividing line, balanced visual weight",
    "concept": "Central focal point with radiating supporting elements, conceptual symbolism, "
              "abstract-yet-clear representation, layered meaning",
    "data": "Clean data visualization, color-coded categories, clear axes and labels, "
           "professional chart styling, emphasis on key insights",
    "system": "Interconnected components, flow diagrams, hierarchical structure, "
             "clear input-output relationships, modular design",
    "timeline": "Horizontal or vertical timeline, chronological markers, milestone highlights, "
               "progressive visual narrative, temporal flow indicators",
    "relationship": "Network diagram style, connecting lines, node-based layout, "
                   "relationship strength indicators, clustering of related elements",
    "hierarchy": "Pyramid or tree structure, clear levels, size variation for importance, "
                "top-down or bottom-up flow, organizational clarity",
    "transformation": "Before-and-after layout, transformation arrow or gradient, "
                     "clear distinction between states, visual metamorphosis",
    "ecosystem": "Circular or cyclical layout, interconnected elements, environmental context, "
                "holistic view, balanced ecosystem representation",
    "architecture": "Blueprint or schematic style, technical precision, cross-sectional views, "
                   "layered structure, dimensional accuracy",
    "abstract": "Symbolic representation, artistic interpretation, metaphorical elements, "
               "conceptual visualization, creative freedom with purpose"
}


def detect_genre(topic):
    """Detect genre from topic"""
    topic_lower = topic.lower()
    
    genre_keywords = {
        "technology": ["technology", "tech", "ai", "artificial intelligence", "machine learning", 
                      "software", "digital", "cyber", "data", "computing", "algorithm", "neural"],
        "healthcare": ["health", "medical", "healthcare", "medicine", "clinical", "patient", 
                      "treatment", "diagnosis", "therapy", "wellness", "diagnostic"],
        "science": ["science", "scientific", "research", "physics", "chemistry", "biology", 
                   "quantum", "laboratory", "experiment", "molecular"],
        "business": ["business", "management", "leadership", "strategy", "corporate", 
                    "entrepreneurship", "marketing", "sales", "enterprise"],
        "education": ["education", "learning", "teaching", "academic", "school", "university", 
                     "training", "curriculum", "pedagogy"],
        "finance": ["finance", "financial", "investment", "banking", "economics", "trading", 
                   "cryptocurrency", "blockchain", "market"],
        "environment": ["environment", "climate", "sustainability", "green", "ecological", 
                       "conservation", "renewable", "ecosystem"]
    }
    
    for genre, keywords in genre_keywords.items():
        if any(keyword in topic_lower for keyword in keywords):
            return genre
    
    return "general"


def detect_content_type(section_title):
    """Detect content type from section title"""
    title_lower = section_title.lower()
    
    type_keywords = {
        "process": ["process", "workflow", "steps", "procedure", "how to", "methodology"],
        "comparison": ["vs", "versus", "comparison", "compare", "difference", "contrast"],
        "timeline": ["timeline", "history", "evolution", "development", "progress"],
        "system": ["system", "architecture", "framework", "structure", "platform"],
        "data": ["data", "statistics", "metrics", "analysis", "results", "findings"],
        "relationship": ["relationship", "connection", "network", "interaction"],
        "hierarchy": ["hierarchy", "levels", "organization", "structure", "layers"],
        "transformation": ["transformation", "change", "transition", "shift", "evolution"],
        "concept": ["introduction", "overview", "concept", "fundamentals", "basics"]
    }
    
    for content_type, keywords in type_keywords.items():
        if any(keyword in title_lower for keyword in keywords):
            return content_type
    
    return "concept"


def generate_detailed_prompt(topic, section, content_preview=""):
    """
    Stage 1: Generate extremely detailed, pixel-level prompt for image generation
    Uses Gemini text model to create comprehensive visual specifications
    """
    print(f"\n{'='*70}")
    print(f"🎨 STAGE 1: Generating Detailed Image Prompt")
    print(f"{'='*70}")
    
    # Detect genre and content type
    genre = detect_genre(topic)
    content_type = detect_content_type(section)
    
    print(f"   Topic: {topic}")
    print(f"   Section: {section}")
    print(f"   Detected Genre: {genre.title()}")
    print(f"   Content Type: {content_type.title()}")
    
    # Get genre-specific characteristics
    genre_specs = GENRE_CHARACTERISTICS[genre]
    content_specs = CONTENT_TYPE_SPECS[content_type]
    
    # Get rendering style
    rendering_style = genre_specs.get('rendering_style', 'illustration')
    style_specs = RENDERING_STYLES[rendering_style]
    
    # Check if characters are required
    characters_required = genre_specs.get('characters_required', False)
    character_context = genre_specs.get('character_context', '')
    
    # Create comprehensive prompt for text generation
    prompt_generator_instruction = f"""You are a master visual designer and prompt engineer with expertise in creating PHOTOREALISTIC, publication-quality illustrations for professional ebooks. Your specialty is generating HYPER-DETAILED, pixel-precise prompts that produce stunning, magazine-grade imagery following professional photography and CGI rendering standards.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EBOOK CONTEXT & REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 EBOOK DETAILS:
   • Topic: {topic}
   • Chapter/Section: {section}
   • Target Genre: {genre}
   • Visual Content Type: {content_type}
   • Content Context: {content_preview[:500] if content_preview else "N/A"}

🎨 RENDERING STYLE: {rendering_style.upper().replace('_', ' ')}
   • Style Description: {style_specs['description']}
   • Technical Requirements: {style_specs['technical']}
   • Quality Standards: {', '.join(style_specs['quality_keywords'][:5])}

🎨 GENRE-SPECIFIC DESIGN SYSTEM:
   • Color Palette: {genre_specs['color_palette']}
   • Visual Style: {genre_specs['visual_style']}
   • Lighting Design: {genre_specs['lighting']}
   • Composition Rules: {genre_specs['composition']}
   • Surface Textures: {genre_specs['texture']}

📐 CONTENT TYPE LAYOUT REQUIREMENTS:
   • Layout Pattern: {content_specs}

{"👥 CHARACTER REQUIREMENTS (MANDATORY):" if characters_required else ""}
{CHARACTER_REQUIREMENTS if characters_required else ""}
{f"   • Context: {character_context}" if characters_required else ""}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR MISSION: CREATE A MASTERPIECE PROMPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate an ULTRA-DETAILED image generation prompt with SURGICAL PRECISION for an ebook illustration. This must be publication-ready, professional, and perfectly aligned with the ebook's topic and genre.

🎯 MANDATORY SPECIFICATIONS (Include ALL of these):

1️⃣ SPATIAL ARCHITECTURE & COMPOSITION (25% of prompt):
   ▸ Exact aspect ratio (16:9 for ebook full-width images)
   ▸ Three-layer depth structure:
     - Foreground: Main subjects with precise placement (use rule of thirds: x=0.33/0.66, y=0.33/0.66)
     - Midground: Supporting elements with size ratios relative to foreground (e.g., 60% scale)
     - Background: Environmental context with appropriate depth blur
   ▸ Visual weight distribution (specify percentages: 40% left, 60% right, etc.)
   ▸ Negative space allocation (identify exact areas in percentage)
   ▸ Leading lines and eye flow path (describe the visual journey)
   ▸ Frame within frame techniques (if applicable)

2️⃣ HYPER-PRECISE COLOR ENGINEERING (20% of prompt):
   ▸ Primary colors with EXACT hex codes (e.g., #1a2b3c)
   ▸ Secondary and accent colors with hex values
   ▸ Color temperature specifications (warm: 2700K-3500K, cool: 5000K-7000K)
   ▸ Gradient specifications:
     - Start point (x,y coordinates as percentages)
     - End point coordinates
     - Gradient type (linear, radial, angular)
     - Color stops with hex codes
   ▸ Saturation levels (0-100% scale)
   ▸ Value/brightness contrast ratios (e.g., 3:1, 7:1 for accessibility)
   ▸ Color harmony type (analogous, complementary, triadic, etc.)

3️⃣ ADVANCED LIGHTING ARCHITECTURE (20% of prompt):
   ▸ Primary light source:
     - Position (polar coordinates: angle and distance)
     - Intensity (lumens or relative scale 1-10)
     - Color temperature (Kelvin scale)
     - Quality (hard/soft, beam angle)
   ▸ Fill light specifications (position, intensity at 30-50% of key)
   ▸ Rim/edge lighting (position, color, intensity)
   ▸ Ambient occlusion (shadow darkness in crevices)
   ▸ Specular highlights (location, size, intensity)
   ▸ Global illumination behavior (bounce light color and intensity)
   ▸ Shadow characteristics:
     - Penumbra softness (0-100%)
     - Direction and length
     - Opacity (0-100%)
     - Color tint (if any)

4️⃣ VISUAL ELEMENTS & SYMBOLISM (25% of prompt):
   ▸ Primary subject:
     - Exact description with technical details
     - Size (absolute or relative: "occupies 35% of frame height")
     - Position with coordinates
     - Orientation (angle, rotation)
     - Level of detail (photorealistic, stylized, abstract)
   ▸ Secondary elements (2-5 items):
     - Description, size ratios (e.g., "30% size of primary subject")
     - Spatial relationships (distance, alignment)
     - Purpose in composition
   ▸ Symbolic elements relevant to ebook content:
     - What concepts they represent
     - How they connect to the section topic
   ▸ Typography or text elements (if any):
     - Font style hints
     - Size and placement
     - Integration with imagery

5️⃣ ARTISTIC EXECUTION & STYLE (15% of prompt):
   ▸ Primary rendering style (choose one):
     - Photorealistic (specify camera: 50mm, f/2.8, ISO 100)
     - Digital illustration (vector, raster, mixed media)
     - 3D rendered (render engine style: Octane, Cycles, Arnold)
     - Painterly (oil, watercolor, acrylic technique)
     - Technical diagram (blueprint, schematic, infographic)
   ▸ Line work characteristics:
     - Thickness (0.5pt - 3pt)
     - Style (clean, sketchy, organic, geometric)
     - Anti-aliasing quality
   ▸ Texture application:
     - Macro textures (visible patterns)
     - Micro textures (surface quality)
     - Blend modes (multiply, overlay, screen)
   ▸ Artistic influences or style references (e.g., "reminiscent of modern tech illustrations from Apple's design language")

6️⃣ TECHNICAL & MATERIAL SPECIFICATIONS (15% of prompt):
   ▸ Resolution target: 1024×576 pixels minimum, 8K quality rendering
   ▸ Aspect ratio locked: 16:9 (ebook standard)
   ▸ Depth of field:
     - Focus plane (which layer: foreground/midground/background)
     - Bokeh characteristics (circular, hexagonal)
     - Blur intensity (f-stop equivalent: f/1.4 - f/22)
   ▸ Material properties using PBR specifications:
     - Metallic surfaces: metalness (0-1), roughness (0-1)
     - Dielectric surfaces: reflectivity index, roughness
     - Translucent materials: subsurface scattering, opacity
     - Emissive elements: color and intensity
   ▸ Edge treatment:
     - Sharp edges (technical elements, modern design)
     - Soft edges (organic elements, backgrounds)
     - Anti-aliasing quality (8x MSAA equivalent)
   ▸ Post-processing effects:
     - Chromatic aberration (subtle: 0.1-0.3)
     - Vignetting (darkness at edges: 0-30%)
     - Bloom/glow on bright elements (radius, intensity)
     - Film grain (if applicable: 0-5%)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL REQUIREMENTS (SLIDEXY STANDARDS):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ PHOTOREALISTIC QUALITY:
  • Masterpiece quality, professional presentation grade
  • Ultra high definition 8K resolution rendering
  • Magazine-quality composition with award-winning visual design
  • Crisp clarity and sharpness throughout
  • Rich color depth with perfect exposure balance
  • Intricate fine details in all elements

✓ TECHNICAL EXCELLENCE:
  • Exact 16:9 aspect ratio (1024×576 pixels minimum)
  • {style_specs['technical']}
  • Professional photography standards (if photorealistic)
  • PBR material properties (if 3D CGI)

✓ CHARACTER STANDARDS (if applicable):
  • MANDATORY diverse representation (ethnicities, genders, ages, body types)
  • Photorealistic skin tones with natural features
  • Anatomically correct proportions and poses
  • Professional attire appropriate to context
  • Authentic expressions and natural gestures
  • Proper environmental integration with realistic lighting

✓ STRICT PROHIBITIONS:
  • NO TEXT, LETTERS, WORDS, OR TYPOGRAPHY OF ANY KIND in the image
  • NO watermarks, logos, or branding elements
  • NO generic stock photo clichés
  • NO unrealistic poses or expressions

✓ OUTPUT FORMAT:
  • ONE comprehensive, flowing paragraph (600-800 words)
  • Include EXACT numerical values (percentages, coordinates, hex codes)
  • Maintain semantic relevance to ebook section content
  • Ensure visual storytelling that enhances reader understanding
  • Publication-quality, professional ebook illustration standards
  • Genre-appropriate aesthetics throughout
  • Technically precise for AI image generation
  • SPECIFIC details about every element - no generic descriptions

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generate the hyper-detailed, publication-ready image prompt NOW:"""

    try:
        # Generate detailed prompt using text model
        model = genai_text.GenerativeModel(TEXT_MODEL)
        
        print(f"\n⏳ Generating detailed prompt with {TEXT_MODEL}...")
        
        response = model.generate_content(
            prompt_generator_instruction,
            generation_config=genai_text.types.GenerationConfig(
                temperature=0.8,  # Higher creativity for richer descriptions
                top_p=0.95,
                top_k=50,
                max_output_tokens=4096,  # Increased for more detailed prompts
            )
        )
        
        detailed_prompt = response.text.strip()
        
        # Remove "Here's the detailed prompt:" type prefixes if present
        if detailed_prompt.lower().startswith(("here's", "here is", "the prompt", "prompt:")):
            lines = detailed_prompt.split('\n')
            if len(lines) > 1:
                detailed_prompt = '\n'.join(lines[1:]).strip()
        
        print(f"\n✅ ULTRA-DETAILED PHOTOREALISTIC PROMPT GENERATED!")
        print(f"   Length: {len(detailed_prompt)} characters")
        print(f"   Words: {len(detailed_prompt.split())} words")
        print(f"   Target: 600-800 words (Slidexy-grade photorealistic detail)")
        print(f"   Rendering Style: {rendering_style.upper().replace('_', ' ')}")
        if characters_required:
            print(f"   ✓ Characters Required: Diverse representation enforced")
        
        # Save prompt to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        prompt_dir = "generated_prompts"
        os.makedirs(prompt_dir, exist_ok=True)
        
        safe_section = section.lower().replace(' ', '_')[:50]
        prompt_file = f"{prompt_dir}/{timestamp}_{safe_section}.txt"
        
        with open(prompt_file, 'w') as f:
            f.write(f"Topic: {topic}\n")
            f.write(f"Section: {section}\n")
            f.write(f"Genre: {genre}\n")
            f.write(f"Content Type: {content_type}\n")
            f.write(f"\n{'='*70}\n")
            f.write(f"DETAILED PROMPT:\n")
            f.write(f"{'='*70}\n\n")
            f.write(detailed_prompt)
        
        print(f"   Prompt saved: {prompt_file}")
        
        return detailed_prompt, genre, content_type
        
    except Exception as e:
        print(f"\n❌ Error generating detailed prompt: {e}")
        # Fallback to basic prompt
        fallback = f"Professional {genre} illustration for {section}. {genre_specs['visual_style']} {genre_specs['color_palette']}"
        return fallback, genre, content_type


def generate_image_from_prompt(detailed_prompt, output_path, genre, content_type):
    """
    Stage 2: Generate image using the detailed prompt
    """
    print(f"\n{'='*70}")
    print(f"🖼️  STAGE 2: Generating Image from Detailed Prompt")
    print(f"{'='*70}")
    print(f"   Model: {IMAGE_MODEL}")
    print(f"   Output: {output_path}")
    print(f"   Genre: {genre.title()}")
    print(f"   Type: {content_type.title()}")
    print(f"{'='*70}\n")
    
    try:
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        
        print("⏳ Generating high-quality image...")
        
        # Generate image using detailed prompt
        response = image_client.models.generate_content(
            model=IMAGE_MODEL,
            contents=detailed_prompt,
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
                            
                            print(f"   ✓ Image data received: {mime_type}")
                            
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
                            
                            print(f"\n✅ HIGH-QUALITY IMAGE GENERATED!")
                            print(f"   📁 File: {output_path}")
                            print(f"   📏 Size: {size:,} bytes ({size/1024:.1f} KB)")
                            print(f"   📐 Dimensions: {width}x{height}")
                            print(f"   🎨 Genre: {genre.title()}")
                            print(f"   📊 Type: {content_type.title()}")
                            
                            return True, "Image generated successfully", output_path
        
        print("⚠️  No image data found in response")
        return False, "No image data in response", None
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ Error generating image: {error_msg}")
        return False, error_msg, None


def generate_ebook_image(topic, section, output_path, content_preview=""):
    """
    Complete two-stage workflow: Generate detailed prompt, then generate image
    """
    print(f"\n{'#'*70}")
    print(f"# TWO-STAGE IMAGE GENERATION WORKFLOW")
    print(f"{'#'*70}\n")
    
    start_time = time.time()
    
    # Stage 1: Generate detailed prompt
    detailed_prompt, genre, content_type = generate_detailed_prompt(
        topic, section, content_preview
    )
    
    print(f"\n📝 Generated Prompt Preview:")
    print(f"{'-'*70}")
    preview_length = min(300, len(detailed_prompt))
    print(f"{detailed_prompt[:preview_length]}...")
    print(f"{'-'*70}")
    
    # Small delay between stages
    time.sleep(1)
    
    # Stage 2: Generate image
    success, message, path = generate_image_from_prompt(
        detailed_prompt, output_path, genre, content_type
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n{'='*70}")
    print(f"⏱️  Total Time: {elapsed_time:.2f} seconds")
    print(f"{'='*70}\n")
    
    return success, message, path, detailed_prompt


# =============================================================================
# TEST FUNCTIONS
# =============================================================================

def test_single_image():
    """Test: Generate single image with two-stage workflow"""
    print("\n" + "="*70)
    print("TEST 1: SINGLE IMAGE - TWO-STAGE WORKFLOW")
    print("="*70)
    
    topic = "Quantum Computing Revolution"
    section = "Quantum Entanglement and Superposition"
    content_preview = """
    Quantum entanglement represents one of the most fascinating phenomena in quantum mechanics,
    where particles become interconnected in ways that defy classical physics. When particles
    are entangled, the quantum state of one particle instantaneously influences the state of
    another, regardless of the distance between them. Superposition allows quantum bits to exist
    in multiple states simultaneously, enabling quantum computers to process vast amounts of
    information in parallel. This fundamental property gives quantum computers their extraordinary
    computational power, potentially solving problems that would take classical computers millennia.
    """
    
    output_path = "test_quantum_computing.png"
    
    success, message, path, prompt = generate_ebook_image(
        topic, section, output_path, content_preview
    )
    
    if success:
        print(f"\n✅ TEST PASSED")
        print(f"   Image: {path}")
    else:
        print(f"\n❌ TEST FAILED: {message}")
    
    return success


def test_multiple_images():
    """Test: Generate multiple images for different sections"""
    print("\n" + "="*70)
    print("TEST 2: MULTIPLE IMAGES - BATCH GENERATION (MIXED GENRES)")
    print("="*70)
    
    # Test different genres with rich content
    sections_data = [
        {
            "topic": "Sustainable Energy Solutions",
            "title": "Solar Energy Conversion Process",
            "content": """Photovoltaic cells convert sunlight directly into electricity through the 
            photovoltaic effect. When photons strike the semiconductor material in solar panels, 
            they knock electrons loose from atoms, creating an electric current. Modern solar panels 
            use multiple layers of silicon semiconductors with different properties to maximize 
            efficiency, achieving conversion rates of 20-25% in commercial applications."""
        },
        {
            "topic": "Modern Healthcare Innovation",
            "title": "Telemedicine vs Traditional Healthcare",
            "content": """Telemedicine leverages digital communication technologies to provide 
            remote healthcare services, fundamentally transforming patient-doctor interactions. 
            Unlike traditional in-person visits, telemedicine offers real-time video consultations, 
            remote patient monitoring, and digital health records access. This comparison highlights 
            how virtual care reduces geographical barriers while maintaining diagnostic accuracy."""
        },
        {
            "topic": "Financial Technology Evolution",
            "title": "Blockchain Technology Architecture",
            "content": """Blockchain represents a distributed ledger system where transactions are 
            recorded in blocks that are cryptographically linked together. Each block contains a 
            hash of the previous block, transaction data, and a timestamp, creating an immutable 
            chain. The decentralized architecture ensures that no single entity controls the entire 
            network, providing transparency and security for financial transactions."""
        }
    ]
    
    os.makedirs("ebook_images_mixed", exist_ok=True)
    
    results = []
    
    for i, section_data in enumerate(sections_data, 1):
        print(f"\n[{i}/{len(sections_data)}] Processing: {section_data['title']}")
        print(f"   Topic: {section_data['topic']}")
        
        safe_name = section_data['title'].lower().replace(' ', '_')[:40]
        output_path = f"ebook_images_mixed/{i:02d}_{safe_name}.png"
        
        success, message, path, prompt = generate_ebook_image(
            section_data['topic'],
            section_data['title'],
            output_path,
            section_data['content']
        )
        
        results.append({
            'topic': section_data['topic'],
            'section': section_data['title'],
            'success': success,
            'path': path,
            'message': message
        })
        
        # Rate limiting between images
        if i < len(sections_data):
            print("\n⏳ Waiting 5 seconds before next image...")
            time.sleep(5)
    
    # Summary
    print(f"\n{'='*70}")
    print("BATCH GENERATION COMPLETE")
    print(f"{'='*70}")
    successful = sum(1 for r in results if r['success'])
    print(f"\n✅ Successful: {successful}/{len(results)}")
    
    for r in results:
        status = "✅" if r['success'] else "❌"
        print(f"{status} {r['topic']} - {r['section']}")
        if r['success']:
            print(f"   → {r['path']}")
    
    return successful == len(results)


def main():
    """Run comprehensive tests"""
    
    print("\n" + "="*70)
    print("TWO-STAGE IMAGE GENERATION SYSTEM")
    print("Stage 1: Detailed Prompt Generation (Gemini Text)")
    print("Stage 2: Image Generation (Gemini Image)")
    print("="*70)
    
    print(f"\n📋 Configuration:")
    print(f"   Text Model: {TEXT_MODEL}")
    print(f"   Image Model: {IMAGE_MODEL}")
    print(f"   Genres: {len(GENRE_CHARACTERISTICS)}")
    print(f"   Content Types: {len(CONTENT_TYPE_SPECS)}")
    
    print("\n💡 Features:")
    print("   ✓ Pixel-level prompt precision")
    print("   ✓ Genre-adaptive styling")
    print("   ✓ Content-type specific layouts")
    print("   ✓ Semantic understanding")
    print("   ✓ Publication-ready quality")
    
    # Test 1: Single image
    input("\n\nPress Enter to start Test 1 (Single Image)...")
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
    print(f"\n✅ Test 1 (Single): {'PASSED' if success1 else 'FAILED'}")
    print(f"{'✅' if success2 else '⚠️ '} Test 2 (Batch): {'PASSED' if success2 else 'SKIPPED/FAILED'}")
    
    print("\n📁 Generated files:")
    print("   • test_quantum_computing.png (Science genre)")
    print("   • ebook_images_mixed/ (Environment, Healthcare, Finance)")
    print("   • generated_prompts/ (ultra-detailed 500-700 word prompts)")
    
    print("\n✨ Two-stage workflow ensures:")
    print("   • Extreme precision in visual specifications")
    print("   • Genre and content-type adaptation")
    print("   • Semantic relevance to content")
    print("   • Publication-quality output")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
