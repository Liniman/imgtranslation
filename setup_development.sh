#!/bin/bash

# Development Workflow Setup Script
# Sets up feature branch workflow and development environment

echo "🛠️  Setting up development workflow..."

# Create develop branch
echo "Creating develop branch..."
git checkout -b develop
git push -u origin develop

# Set up feature branch for current UI work
echo "Creating feature branch for ongoing work..."
git checkout -b feature/ui-enhancements develop
git push -u origin feature/ui-enhancements

# Create additional feature branches for planned work
git checkout develop
git checkout -b feature/deployment-setup
git push -u origin feature/deployment-setup

git checkout develop
git checkout -b feature/memory-optimization  
git push -u origin feature/memory-optimization

# Return to main branch
git checkout main

echo "✅ Development branches created:"
echo "   📝 main        - Production-ready releases"
echo "   🚧 develop     - Integration branch for features"
echo "   ✨ feature/ui-enhancements     - Current UI work"
echo "   🚀 feature/deployment-setup   - Streamlit Cloud deployment"
echo "   ⚡ feature/memory-optimization - Performance improvements"

echo ""
echo "📋 Development Workflow:"
echo "   1. Create feature branches from 'develop'"
echo "   2. Work on features in separate branches"
echo "   3. Merge features back to 'develop' via PR"
echo "   4. Merge 'develop' to 'main' for releases"

echo ""
echo "🔄 To start working on a feature:"
echo "   git checkout develop"
echo "   git pull origin develop"
echo "   git checkout -b feature/your-feature-name"