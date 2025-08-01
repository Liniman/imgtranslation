# Streamlit Cloud Deployment Guide

This guide walks you through deploying the Image Translation Tool to Streamlit Cloud.

## Prerequisites

✅ GitHub repository set up: https://github.com/Liniman/imgtranslation  
✅ DeepL API key added as GitHub secret  
✅ All deployment files configured  

## Quick Deploy to Streamlit Cloud

### 1. Access Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with your GitHub account
3. Click "New app"

### 2. App Configuration
```
Repository: Liniman/imgtranslation
Branch: main
Main file path: direct_edit_app.py
App URL: imgtranslation (or your preferred subdomain)
```

### 3. Environment Variables
In the "Advanced settings" section, add:
```
DEEPL_API_KEY = your_deepl_api_key_here
```

### 4. Deploy
Click "Deploy!" and wait for the build to complete.

## Files Configured for Deployment

### Core Application Files
- `direct_edit_app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `packages.txt` - System dependencies (OpenCV, GUI libraries)

### Configuration Files
- `.streamlit/config.toml` - Streamlit configuration
  - Upload limit: 200MB
  - Enhanced security settings
  - Custom theme colors
  - Performance optimizations

### Core Modules
- `core/` - All processing engines (OCR, Translation, Image Processing)
- `core/memory_tracker.py` - Performance monitoring
- `core/logging_config.py` - Structured logging

## Production Optimizations

### Performance
- Memory tracking enabled for monitoring
- Caching enabled for engines (`@st.cache_resource`)
- Optimized image processing pipeline
- Efficient font loading and caching

### Security
- XSRF protection enabled
- No CORS issues with proper configuration
- Environment variables for API keys
- Input validation and sanitization

### User Experience
- Responsive design for mobile/desktop
- Clean interface with proper spacing
- Step-by-step processing visualization
- Interactive text editing capabilities

## Monitoring & Maintenance

### Health Checks
The app includes built-in health monitoring:
- Memory usage tracking
- Processing time metrics
- Error logging and reporting
- Performance benchmarks

### Logs Access
View logs in Streamlit Cloud:
1. Go to your app dashboard
2. Click "Manage app"
3. View "Logs" tab for real-time monitoring

### Updates & Rollbacks
- Push to `main` branch for production updates
- Use feature branches for development
- GitHub Actions CI/CD runs tests before deployment
- Easy rollback via GitHub commit history

## Troubleshooting

### Common Issues

#### 1. Module Import Errors
**Issue**: `ModuleNotFoundError` for core modules  
**Solution**: Ensure all files are in repository root, check imports in direct_edit_app.py

#### 2. Memory Issues
**Issue**: App crashes with large images  
**Solution**: Images are automatically resized, monitor memory usage in logs

#### 3. API Key Issues
**Issue**: Translation fails  
**Solution**: Verify DEEPL_API_KEY is set in Streamlit Cloud secrets

#### 4. File Upload Issues
**Issue**: Upload fails or times out  
**Solution**: Check file size (max 200MB), supported formats (PNG, JPG, JPEG, WEBP)

### Performance Optimization
- Use smaller images for faster processing
- Monitor memory usage in real-time
- Check processing times in step-by-step view
- Use OCR confidence filtering for better results

## App Features Available in Production

### Core Functionality
✅ **Image Upload** - Drag & drop or file picker  
✅ **Multi-language Translation** - 11 supported languages  
✅ **OCR Text Detection** - EasyOCR with confidence filtering  
✅ **Interactive Text Editing** - Click to edit translated text  
✅ **Step-by-step Processing** - Visual pipeline with 4 tabs  
✅ **Memory Monitoring** - Real-time performance tracking  

### Advanced Features
✅ **Smart Font Matching** - Automatic font selection for different languages  
✅ **Content-aware Inpainting** - Clean text removal with background preservation  
✅ **Invisible UI Overlays** - Clean final images without visual artifacts  
✅ **Mobile Responsive** - Works on all device sizes  
✅ **Batch Processing** - Support for multiple images (future feature)  

## Production URLs

### Live Application
🚀 **Production**: https://imgtranslation.streamlit.app  
📊 **Monitoring**: Streamlit Cloud dashboard  
📋 **Repository**: https://github.com/Liniman/imgtranslation  

### Support & Issues
- Create issues at: https://github.com/Liniman/imgtranslation/issues
- View documentation: https://github.com/Liniman/imgtranslation/tree/main/docs
- Contributing guide: https://github.com/Liniman/imgtranslation/blob/main/CONTRIBUTING.md

## Success Criteria

Your deployment is successful when:
✅ App loads without errors  
✅ File upload works with sample images  
✅ OCR detection shows bounding boxes  
✅ Translation produces readable results  
✅ Step-by-step tabs all display content  
✅ Memory monitoring shows performance metrics  
✅ No console errors in browser developer tools  

Congratulations! Your AI-powered image translation tool is now live! 🎉