# 🚀 Speech Analysis App - Vercel Deployment Guide

## 📦 Project Structure
Your project contains the following files ready for deployment:

### Core Application Files
- `app.py` - Main Streamlit application
- `audio_processor.py` - Audio processing and speech recognition
- `speech_analyzer.py` - Speech analysis algorithms
- `ai_analyzer.py` - AI-powered insights using OpenAI
- `visualizations.py` - Interactive charts and graphs

### Deployment Configuration Files
- `vercel.json` - Vercel deployment configuration
- `dependencies.txt` - Python dependencies (rename to requirements.txt)
- `main.py` - Vercel handler (alternative entry point)
- `Procfile` - Process file for deployment
- `runtime.txt` - Python version specification
- `.streamlit/config.toml` - Streamlit production configuration

## 🔧 Pre-Deployment Setup

### 1. Prepare Dependencies
```bash
# Rename dependencies.txt to requirements.txt
mv dependencies.txt requirements.txt
```

### 2. Environment Variables
Set up the following environment variable in Vercel:
- `OPENAI_API_KEY` - Your OpenAI API key for AI insights

## 🚀 Vercel Deployment Steps

### Method 1: GitHub Integration (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/speech-analysis-app.git
   git push -u origin main
   ```

2. **Deploy on Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Import your GitHub repository
   - Vercel will automatically detect it as a Python project
   - Add environment variable: `OPENAI_API_KEY`
   - Click "Deploy"

### Method 2: Direct Upload

1. **Create ZIP file**
   ```bash
   zip -r speech-analysis-app.zip . -x "*.git*" "*.DS_Store*" "__pycache__/*"
   ```

2. **Upload to Vercel**
   - Go to [vercel.com](https://vercel.com)
   - Click "New Project"
   - Select "Upload ZIP"
   - Upload your zip file
   - Configure environment variables
   - Deploy

### Method 3: Vercel CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   vercel login
   vercel --prod
   ```

## ⚙️ Configuration Details

### Environment Variables Required
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Vercel Settings
- **Framework Preset**: Other
- **Build Command**: `pip install -r requirements.txt`
- **Output Directory**: (leave empty)
- **Install Command**: `pip install -r requirements.txt`
- **Development Command**: `streamlit run app.py`

## 🔍 Troubleshooting

### Common Issues

1. **Dependencies Not Installing**
   - Ensure `requirements.txt` exists (rename from `dependencies.txt`)
   - Check Python version compatibility in `runtime.txt`

2. **Streamlit Not Starting**
   - Verify `.streamlit/config.toml` configuration
   - Check port configuration in `vercel.json`

3. **OpenAI API Errors**
   - Verify `OPENAI_API_KEY` environment variable is set
   - Ensure your OpenAI account has sufficient credits

4. **Audio Processing Issues**
   - Vercel has limitations with system packages like ffmpeg
   - Consider using cloud storage for large audio files
   - Implement fallback processing methods

### Alternative Deployment Platforms

If Vercel doesn't work optimally for this Streamlit app:

1. **Streamlit Cloud** (Recommended for Streamlit apps)
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect GitHub repository
   - Deploy directly

2. **Heroku**
   - Use the included `Procfile`
   - Add buildpacks for Python and system audio libraries

3. **Railway**
   - Deploy directly from GitHub
   - Better support for system dependencies

## 📋 Final Checklist

Before deploying:
- [ ] Rename `dependencies.txt` to `requirements.txt`
- [ ] Set `OPENAI_API_KEY` environment variable
- [ ] Test audio file upload functionality
- [ ] Verify all team page content is correct
- [ ] Check responsive design on mobile

## 🎉 Post-Deployment

After successful deployment:
1. Test audio file upload and processing
2. Verify speech analysis features work
3. Check team page displays correctly
4. Test AI insights functionality
5. Monitor application performance and logs

Your speech analysis application is now ready for production use!