#!/bin/bash
# VQA Dataset Project - One-Time Global Setup
# Run this once to set up everything, then all scripts work independently

echo "🚀 VQA Dataset Project - Global Environment Setup"
echo "================================================="
echo "This sets up a global environment that all scripts can use"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "vqa_env" ]; then
    echo "📦 Creating global virtual environment in root..."
    python3 -m venv vqa_env
else
    echo "📦 Using existing global virtual environment..."
fi

# Activate virtual environment
echo "⚡ Activating environment..."
source vqa_env/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install all dependencies from requirements.txt
echo "📋 Installing all dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing core dependencies..."
    pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    pip install transformers easyocr pytesseract opencv-python pillow numpy pandas
    pip install scikit-learn matplotlib tqdm requests beautifulsoup4
fi

# Test installations
echo ""
echo "🧪 Testing installations..."
python3 -c "
import sys
print(f'Python: {sys.version}')
try:
    import torch, transformers, easyocr, cv2
    from PIL import Image
    print('✅ All core dependencies available')
except ImportError as e:
    print(f'❌ Missing dependency: {e}')
    exit(1)
"

echo ""
echo "🎉 Global setup complete!"
echo ""
echo "📋 Usage (from project root):"
echo ""
echo "   # Option 1: Activate once per terminal session"
echo "   source vqa_env/bin/activate"
echo "   python3 phase2_keywords/phase2_optimized_pipeline.py --input_dir data --language english --output_dir results"
echo ""
echo "   # Option 2: Direct execution (auto-detects environment)"  
echo "   python3 phase2_keywords/phase2_optimized_pipeline.py --input_dir data --language english --output_dir results"
echo ""
echo "✨ All scripts now work from anywhere in the project!"