# Speech Analysis Application

## Overview

This is an AI-powered speech analysis application built with Streamlit that analyzes MP3 audio recordings to provide comprehensive feedback on speaking performance. The application processes audio files to extract speech metrics, transcribe content, and generate AI-powered insights using OpenAI's GPT-5 model. Users can upload MP3 files and receive detailed analysis including speaking pace, volume stability, filler word usage, and confidence scoring with interactive visualizations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Interface**: Provides a simple, interactive web application for file uploads and results display
- **Component-based Structure**: Modular design with separate modules for audio processing, speech analysis, AI analysis, and visualizations
- **Progressive Loading**: Implements progress tracking and status updates during analysis phases

### Audio Processing Pipeline
- **Multi-format Support**: Uses librosa and pydub for audio file handling and format conversion
- **Speech Recognition**: Integrates Google Speech Recognition API for audio-to-text transcription
- **Audio Feature Extraction**: Analyzes volume stability, RMS values, and other acoustic properties using librosa

### Analysis Engine
- **Speech Metrics Calculation**: Calculates speaking pace (words per minute), confidence scores, and volume stability
- **Filler Word Detection**: Identifies and quantifies common filler words and speech patterns
- **Text Analysis**: Processes transcribed content for linguistic patterns and speaking habits

### AI Integration
- **OpenAI GPT-5 Integration**: Uses the latest OpenAI model for advanced speech performance analysis
- **Structured JSON Responses**: Implements response formatting for consistent AI-generated insights
- **Fallback Mechanism**: Provides basic analysis when AI services are unavailable

### Visualization System
- **Interactive Charts**: Uses Plotly for dynamic, interactive visualizations including radar charts and timeline plots
- **Performance Benchmarking**: Compares user metrics against established speaking performance standards
- **Real-time Feedback**: Displays analysis results with color-coded performance indicators

## External Dependencies

### AI Services
- **OpenAI API**: GPT-5 model for advanced speech analysis and feedback generation
- **Google Speech Recognition**: For audio transcription services

### Audio Processing Libraries
- **librosa**: Audio analysis and feature extraction
- **pydub**: Audio format conversion and manipulation
- **SpeechRecognition**: Python library for speech-to-text conversion

### Web Framework and Visualization
- **Streamlit**: Web application framework for the user interface
- **Plotly**: Interactive data visualization library for charts and graphs

### Data Processing
- **NumPy**: Numerical computing for audio signal processing
- **Pandas**: Data manipulation for metrics and analysis results

### System Dependencies
- **tempfile**: Temporary file handling for audio processing
- **os**: Environment variable management for API keys
- **json**: Data serialization for AI responses
- **re**: Regular expressions for text pattern matching
- **collections**: Data structure utilities for analysis calculations