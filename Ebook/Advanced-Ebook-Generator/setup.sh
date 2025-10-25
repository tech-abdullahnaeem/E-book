#!/bin/bash

# Advanced E-Book Generator - Setup Script
# This script helps you set up the e-book generator on macOS/Linux

echo "🚀 Advanced E-Book Generator - Setup Script"
echo "============================================"
echo ""

# Check Python version
echo "📌 Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION found"
else
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Check if pip is installed
echo ""
echo "📌 Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "✓ pip3 found"
else
    echo "❌ pip3 not found. Please install pip."
    exit 1
fi

# Check if Pandoc is installed
echo ""
echo "📌 Checking Pandoc..."
if command -v pandoc &> /dev/null; then
    PANDOC_VERSION=$(pandoc --version | head -n 1)
    echo "✓ $PANDOC_VERSION found"
else
    echo "⚠️  Pandoc not found."
    echo "   Install with: brew install pandoc (macOS) or sudo apt-get install pandoc (Linux)"
fi

# Check if LaTeX is installed
echo ""
echo "📌 Checking LaTeX..."
if command -v xelatex &> /dev/null; then
    echo "✓ XeLaTeX found"
elif command -v pdflatex &> /dev/null; then
    echo "✓ PDFLaTeX found"
else
    echo "⚠️  LaTeX not found."
    echo "   Install with: brew install --cask mactex (macOS) or sudo apt-get install texlive-xetex (Linux)"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Create .env file if it doesn't exist
echo ""
echo "🔧 Setting up environment file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env file from .env.example"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env and add your API keys:"
    echo "   - GEMINI_API_KEY (required)"
    echo "   - GOOGLE_API_KEY (optional, for research)"
    echo "   - SEARCH_ENGINE_ID (optional, for research)"
else
    echo "✓ .env file already exists"
fi

# Create output directory
echo ""
echo "📁 Creating output directory..."
mkdir -p output
mkdir -p chapters
echo "✓ Directories created"

echo ""
echo "============================================"
echo "✅ Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys"
echo "2. Run: python3 main.py create"
echo ""
echo "For help: python3 main.py --help"
echo "============================================"
