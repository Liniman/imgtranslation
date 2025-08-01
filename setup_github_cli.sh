#!/bin/bash

# Enhanced GitHub Repository Setup Script using GitHub CLI
# Run this after installing GitHub CLI: brew install gh

echo "🚀 Setting up GitHub repository with GitHub CLI..."

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI is not installed."
    echo "📦 Install it with: brew install gh"
    echo "🔗 Or visit: https://cli.github.com/"
    exit 1
fi

# Check if user is authenticated
if ! gh auth status &> /dev/null; then
    echo "🔐 Authenticating with GitHub..."
    gh auth login
fi

# Create repository on GitHub
echo "📁 Creating repository on GitHub..."
gh repo create imgtranslation \
    --description "AI-powered image translation tool with interactive text editing - translate text in images while preserving layout and design" \
    --public \
    --clone=false \
    --push=false

# Add remote and push
echo "🔗 Connecting local repository to GitHub..."
git remote add origin https://github.com/$(gh api user --jq .login)/imgtranslation.git

# Push main branch
echo "📤 Pushing main branch to GitHub..."
git push -u origin main

# Set up branch protection rules
echo "🛡️  Setting up branch protection for main..."
gh api repos/$(gh api user --jq .login)/imgtranslation/branches/main/protection \
    --method PUT \
    --field required_status_checks='{"strict":true,"contexts":["test"]}' \
    --field enforce_admins=true \
    --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
    --field restrictions=null \
    --field allow_force_pushes=false \
    --field allow_deletions=false || echo "⚠️  Branch protection setup failed (may need admin rights)"

# Enable repository features
echo "⚙️  Configuring repository settings..."
gh api repos/$(gh api user --jq .login)/imgtranslation \
    --method PATCH \
    --field has_issues=true \
    --field has_projects=true \
    --field has_wiki=false \
    --field has_discussions=true

# Create initial labels
echo "🏷️  Creating project labels..."
gh label create "priority:high" --color "d73a4a" --description "High priority items"
gh label create "priority:medium" --color "fbca04" --description "Medium priority items"  
gh label create "priority:low" --color "0075ca" --description "Low priority items"
gh label create "ui/ux" --color "c2e0c6" --description "User interface and experience"
gh label create "performance" --color "d4c5f9" --description "Performance improvements"
gh label create "translation" --color "7057ff" --description "Translation functionality"
gh label create "ocr" --color "008672" --description "OCR and text detection"

echo "✅ Repository successfully set up on GitHub!"
echo ""
echo "📋 Repository URL: https://github.com/$(gh api user --jq .login)/imgtranslation"
echo "📋 Next steps:"
echo "   1. Run ./setup_development.sh to create feature branches"
echo "   2. Set up Streamlit Cloud deployment"
echo "   3. Add DEEPL_API_KEY to repository secrets"
echo ""
echo "🔐 To add secrets:"
echo "   gh secret set DEEPL_API_KEY --body 'your-api-key-here'"