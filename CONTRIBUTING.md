# Contributing to Image Translation Tool

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Development Lifecycle & Git Workflow

### Branch Strategy (GitFlow)

We use a GitFlow workflow with the following branches:

- **`main`** - Production-ready releases only
- **`develop`** - Integration branch for all features  
- **`feature/*`** - Feature development branches
- **`hotfix/*`** - Emergency fixes for production
- **`release/*`** - Release preparation branches

### Workflow Steps

1. **Create Feature Branch**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Work on Your Feature**
   - Make commits with clear, descriptive messages
   - Follow the commit message format: `type: description`
   - Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

3. **Test Your Changes**
   ```bash
   # Run tests
   python -m pytest tests/
   
   # Test the main application
   streamlit run direct_edit_app.py
   ```

4. **Create Pull Request**
   - Push your feature branch to GitHub
   - Create PR against `develop` branch
   - Include description of changes and testing performed

5. **Code Review & Merge**
   - Address any feedback from code review
   - Once approved, merge to `develop`
   - Delete feature branch after merge

## Revert Strategies & Safety

### How to Revert Different Scenarios

#### 1. Revert Last Commit (Not Pushed)
```bash
git reset --soft HEAD~1    # Keep changes staged
git reset --hard HEAD~1    # Discard changes completely
```

#### 2. Revert Specific Commit (Already Pushed)
```bash
git revert <commit-hash>   # Creates new commit that undoes changes
git push origin <branch>
```

#### 3. Revert Merge to Main
```bash
git checkout main
git revert -m 1 <merge-commit-hash>
git push origin main
```

#### 4. Emergency Rollback (Production)
```bash
# Create hotfix branch from last known good commit
git checkout main
git checkout -b hotfix/emergency-rollback <last-good-commit>
git push -u origin hotfix/emergency-rollback
# Create PR to merge hotfix to main
```

#### 5. Revert Entire Feature
```bash
# If feature was merged via PR, revert the merge commit
git revert -m 1 <merge-commit-hash>

# If feature has multiple commits, revert range
git revert <oldest-commit>..<newest-commit>
```

### Backup Strategy
- All feature branches are backed up on remote
- Critical branches are protected with PR requirements
- Use `git stash` for temporary work backup
- Tag releases for easy rollback points

## Code Standards

### Python Code Style
- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Maximum line length: 100 characters

### Commit Message Format
```
type: brief description (50 chars max)

Longer description if needed, explaining the why
and what, not the how. Wrap at 72 characters.

- Use bullet points for multiple changes
- Reference issues: Fixes #123
- Include breaking changes: BREAKING CHANGE: description
```

**Commit Types:**
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pre-commit Hooks
The repository has pre-commit hooks that check:
- Python syntax validation
- Potential secrets detection  
- File size limits
- Code formatting

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_enhanced_app.py

# Run with coverage
python -m pytest --cov=core tests/
```

### Test Structure
- Unit tests in `tests/`
- Integration tests for core modules
- UI tests for Streamlit components
- Performance tests for memory/speed

### Adding New Tests
- Create test files with `test_` prefix
- Use descriptive test function names
- Include both positive and negative test cases
- Mock external dependencies (API calls, file I/O)

## Development Environment

### Setup
```bash
# Clone repository
git clone https://github.com/your-username/imgtranslation.git
cd imgtranslation

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Development Scripts
- `setup_github.sh` - Connect to GitHub repository
- `setup_development.sh` - Create development branches
- `scripts/start_app.sh` - Start Streamlit app
- `scripts/run_tests.sh` - Run full test suite

## Deployment

### Streamlit Cloud Deployment
1. Connect GitHub repository to Streamlit Cloud
2. Set environment variables in Streamlit Cloud dashboard
3. Deploy from `main` branch only
4. Test in staging environment before production

### Environment Variables Required
- `DEEPL_API_KEY` - DeepL translation API key

## Issue Reporting

### Bug Reports
Include:
- Steps to reproduce
- Expected vs actual behavior
- Screenshots/error messages
- Environment details (OS, Python version)
- Minimal code example if applicable

### Feature Requests
Include:
- Clear description of desired functionality
- Use cases and benefits
- Possible implementation approach
- Any related issues or discussions

## Code Review Guidelines

### For Authors
- Keep PRs focused and reasonably sized
- Write clear PR descriptions
- Include tests for new features
- Update documentation as needed
- Respond promptly to review feedback

### For Reviewers
- Focus on code quality, not style preferences
- Suggest improvements, don't just point out problems
- Test the changes locally when possible
- Be respectful and constructive in feedback

## Questions?

- Create an issue for questions about contributing
- Check existing issues and discussions first
- Tag maintainers for urgent questions

Thank you for contributing to make image translation better for everyone! 🚀