#!/bin/bash

# Test script for Advanced E-Book Generator
# Creates a simple test e-book about Python

echo "🧪 Testing Advanced E-Book Generator..."
echo ""

cd /Users/abdullah/Desktop/Techinoid/E-book/Ebook/Advanced-Ebook-Generator

# Run the generator with automated inputs
/usr/local/opt/python@3.12/bin/python3.12 main.py create << 'EOF'
Introduction to Python Programming
1
1
3
n
n
1
1
n
n
n
n
EOF

echo ""
echo "✅ Test complete! Check the output/ directory for results."
