#!/bin/bash

# GitHub Repository Setup Script
# Run this after creating the repository on GitHub

echo "🚀 Setting up GitHub repository connection..."

# Add GitHub remote (replace USERNAME with your GitHub username)
echo "Adding GitHub remote..."
read -p "Enter your GitHub username: " USERNAME
git remote add origin https://github.com/$USERNAME/imgtranslation.git

# Verify remote was added
echo "Verifying remote connection..."
git remote -v

# Push all branches to GitHub
echo "Pushing main branch to GitHub..."
git push -u origin main

echo "✅ Repository successfully connected to GitHub!"
echo "📋 Next steps:"
echo "   1. Visit https://github.com/$USERNAME/imgtranslation"
echo "   2. Set up branch protection rules"
echo "   3. Configure repository settings"
echo "   4. Enable Issues and Discussions if desired"