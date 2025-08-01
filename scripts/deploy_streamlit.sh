#!/bin/bash

# Streamlit Cloud Deployment Preparation Script
# Ensures everything is ready for Streamlit Cloud deployment

echo "🚀 Preparing for Streamlit Cloud deployment..."

# Check if we're on main branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "⚠️  Warning: Not on main branch (current: $CURRENT_BRANCH)"
    echo "🔄 Switching to main branch..."
    git checkout main
    git pull origin main
fi

# Deployment checklist
echo ""
echo "📋 Deployment Checklist:"

# Check required files exist
echo "📁 Checking required files..."
REQUIRED_FILES=("direct_edit_app.py" "requirements.txt" "packages.txt" ".streamlit/config.toml")
ALL_FILES_EXIST=true

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        ALL_FILES_EXIST=false
    fi
done

# Check core modules
echo "📦 Checking core modules..."
CORE_FILES=("core/__init__.py" "core/ocr_engine.py" "core/translator.py" "core/image_processor.py")
for file in "${CORE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    else
        echo "  ❌ $file (MISSING)"
        ALL_FILES_EXIST=false
    fi
done

# Check if DeepL API key is set as GitHub secret
echo "🔐 Checking GitHub secrets..."
if gh secret list | grep -q "DEEPL_API_KEY"; then
    echo "  ✅ DEEPL_API_KEY secret is set"
else
    echo "  ❌ DEEPL_API_KEY secret not found"
    echo "  🔧 Run: gh secret set DEEPL_API_KEY --body 'your-api-key-here'"
    ALL_FILES_EXIST=false
fi

# Test Python syntax
echo "🐍 Testing Python syntax..."
if python -m py_compile direct_edit_app.py; then
    echo "  ✅ Main app syntax is valid"
else
    echo "  ❌ Main app has syntax errors"
    ALL_FILES_EXIST=false
fi

# Check core module imports
echo "📥 Testing core module imports..."
if python -c "from core import OCREngine, TranslationEngine, ImageProcessor; print('✅ Core imports successful')" 2>/dev/null; then
    echo "  ✅ Core modules import successfully"
else
    echo "  ❌ Core module import failed"
    ALL_FILES_EXIST=false
fi

# Check requirements.txt completeness
echo "📋 Checking dependencies..."
REQUIRED_DEPS=("streamlit" "easyocr" "opencv-python-headless" "Pillow" "requests" "psutil")
for dep in "${REQUIRED_DEPS[@]}"; do
    if grep -q "$dep" requirements.txt; then
        echo "  ✅ $dep"
    else
        echo "  ❌ $dep (missing from requirements.txt)"
        ALL_FILES_EXIST=false
    fi
done

# Push latest changes
echo "📤 Ensuring latest changes are pushed..."
if git diff --quiet && git diff --cached --quiet; then
    echo "  ✅ No uncommitted changes"
else
    echo "  ⚠️  Uncommitted changes detected"
    echo "  🔧 Commit and push changes before deploying"
    ALL_FILES_EXIST=false
fi

# Check if remote is up to date
git fetch origin main
if git diff --quiet HEAD origin/main; then
    echo "  ✅ Local branch is up to date with remote"
else
    echo "  ⚠️  Local branch differs from remote"
    echo "  🔧 Push latest changes: git push origin main"
    ALL_FILES_EXIST=false
fi

echo ""
if [ "$ALL_FILES_EXIST" = true ]; then
    echo "🎉 Deployment Pre-check PASSED!"
    echo ""
    echo "🚀 Ready for Streamlit Cloud deployment:"
    echo "   1. Go to https://share.streamlit.io/"
    echo "   2. Click 'New app'"
    echo "   3. Repository: Liniman/imgtranslation"
    echo "   4. Branch: main"
    echo "   5. Main file: direct_edit_app.py"
    echo "   6. Add DEEPL_API_KEY in Advanced settings"
    echo "   7. Click Deploy!"
    echo ""
    echo "📖 Full deployment guide: ./DEPLOYMENT.md"
    echo "🌐 Repository: https://github.com/Liniman/imgtranslation"
else
    echo "❌ Deployment Pre-check FAILED!"
    echo "   Please fix the issues above before deploying"
    exit 1
fi