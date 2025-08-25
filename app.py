import streamlit as st
import tempfile
import os
from audio_processor import AudioProcessor
from speech_analyzer import SpeechAnalyzer
from ai_analyzer import AIAnalyzer
from visualizations import create_visualizations

def main():
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Choose a page", ["🎙️ Speech Analysis", "👥 Our Team"])
    
    if page == "🎙️ Speech Analysis":
        speech_analysis_page()
    elif page == "👥 Our Team":
        team_page()

def speech_analysis_page():
    st.title("🎙️ AI-Powered Speech Analysis")
    st.markdown("Upload an audio file to get detailed analysis of your speaking performance")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an audio file", 
        type=['mp3', 'wav', 'flv', 'mp4', 'm4a', 'ogg', 'aac'],
        help="Upload your speech recording (supports MP3, WAV, MP4, M4A, OGG, AAC formats)"
    )
    
    # Manual transcript option
    st.markdown("### Or provide manual transcript (optional)")
    manual_transcript = st.text_area(
        "If automatic transcription fails, you can paste your speech text here:",
        placeholder="Paste the text of what was spoken in the audio file...",
        height=100,
        help="This will be used if automatic speech recognition doesn't work"
    )
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"File uploaded: {uploaded_file.name} ({uploaded_file.size} bytes)")
        
        # Process button
        if st.button("Analyze Speech", type="primary"):
            temp_file_path = None  # Initialize variable
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_file_path = tmp_file.name
                
                # Initialize processors
                audio_processor = AudioProcessor()
                speech_analyzer = SpeechAnalyzer()
                ai_analyzer = AIAnalyzer()
                
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Step 1: Load and process audio
                status_text.text("Loading audio file...")
                progress_bar.progress(0.1)
                
                audio_data, sample_rate = audio_processor.load_audio(temp_file_path)
                
                # Step 2: Transcribe audio
                status_text.text("Transcribing speech...")
                progress_bar.progress(0.3)
                
                transcript = audio_processor.transcribe_audio(temp_file_path)
                
                # Use manual transcript as fallback if automatic transcription failed
                if not transcript.strip() and manual_transcript.strip():
                    st.info("🔄 Using manual transcript since automatic transcription didn't detect speech.")
                    transcript = manual_transcript.strip()
                elif not transcript.strip() and not manual_transcript.strip():
                    st.error("No speech detected in the audio file. Please ensure the file contains clear speech and try again with a different file.")
                    st.info("💡 **Tips for better results:**\n- Ensure the audio is clear and not too quiet\n- Speak clearly without too much background noise\n- Try a different audio format if the issue persists\n- **Or use the manual transcript option above as a backup**")
                    return
                elif not transcript.strip():
                    st.info("🔄 Using manual transcript since automatic transcription didn't work.")
                    transcript = manual_transcript.strip()
                
                # Step 3: Analyze speech metrics
                status_text.text("Analyzing speech patterns...")
                progress_bar.progress(0.6)
                
                speech_metrics = speech_analyzer.analyze_speech(audio_data, sample_rate, transcript)
                
                # Step 4: Get AI insights
                status_text.text("Generating AI insights...")
                progress_bar.progress(0.8)
                
                ai_insights = ai_analyzer.analyze_speech_performance(transcript, speech_metrics)
                
                # Step 5: Display results
                status_text.text("Preparing results...")
                progress_bar.progress(1.0)
                
                # Clean up temporary file
                os.unlink(temp_file_path)
                
                # Display results
                st.success("Analysis complete!")
                display_results(transcript, speech_metrics, ai_insights)
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"Error during analysis: {error_msg}")
                
                # Provide specific help based on error type
                if "Failed to load audio file" in error_msg:
                    st.info("💡 **Audio Loading Tips:**\n- Try converting your file to MP3 or WAV format\n- Ensure the file is not corrupted\n- Check that the file actually contains audio data\n- Try a smaller file size if the current one is very large")
                elif "No speech detected" in error_msg or "transcription" in error_msg.lower():
                    st.info("💡 **Speech Recognition Tips:**\n- Speak more clearly and loudly\n- Reduce background noise\n- Try recording in a quieter environment\n- Ensure your microphone is working properly")
                else:
                    st.info("💡 **General Tips:**\n- Try a different audio file\n- Ensure the file is not too large (< 25MB recommended)\n- Check your internet connection for AI analysis features")
                
                # Clean up temporary file if it was created
                try:
                    if temp_file_path and os.path.exists(temp_file_path):
                        os.unlink(temp_file_path)
                except:
                    pass

def display_results(transcript, speech_metrics, ai_insights):
    """Display analysis results with visualizations and insights"""
    
    # Transcript section
    with st.expander("📝 Transcript", expanded=False):
        st.text_area("Recognized Speech", transcript, height=200, disabled=True)
    
    # Key metrics overview
    st.header("📊 Speech Metrics Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Speaking Pace", f"{speech_metrics['words_per_minute']:.1f} WPM")
    
    with col2:
        confidence_score = speech_metrics['confidence_score']
        st.metric("Confidence Score", f"{confidence_score:.1f}/10")
    
    with col3:
        filler_percentage = speech_metrics['filler_percentage']
        st.metric("Filler Words", f"{filler_percentage:.1f}%")
    
    with col4:
        volume_stability = speech_metrics['volume_stability']
        st.metric("Volume Stability", f"{volume_stability:.1f}/10")
    
    # Detailed analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizations", "🎯 Detailed Metrics", "🤖 AI Insights", "📋 Recommendations"])
    
    with tab1:
        create_visualizations(speech_metrics)
    
    with tab2:
        st.subheader("Detailed Speech Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Speaking Statistics:**")
            st.write(f"• Total words: {speech_metrics['total_words']}")
            st.write(f"• Total duration: {speech_metrics['duration']:.2f} seconds")
            st.write(f"• Average word length: {speech_metrics['avg_word_length']:.1f} characters")
            st.write(f"• Speaking pace: {speech_metrics['words_per_minute']:.1f} WPM")
        
        with col2:
            st.markdown("**Filler Word Analysis:**")
            st.write(f"• Total filler words: {speech_metrics['filler_count']}")
            st.write(f"• Filler percentage: {speech_metrics['filler_percentage']:.1f}%")
            st.write(f"• Most common fillers: {', '.join(speech_metrics['common_fillers'][:3])}")
            
        st.markdown("**Volume Analysis:**")
        st.write(f"• Volume stability score: {speech_metrics['volume_stability']:.1f}/10")
        st.write(f"• Average volume: {speech_metrics['avg_volume']:.2f} dB")
        st.write(f"• Volume variance: {speech_metrics['volume_variance']:.2f}")
    
    with tab3:
        st.subheader("AI-Powered Analysis")
        
        if ai_insights:
            st.markdown("**Overall Assessment:**")
            st.write(ai_insights.get('overall_assessment', 'No assessment available'))
            
            st.markdown("**Language Proficiency:**")
            proficiency = ai_insights.get('language_proficiency', {})
            if proficiency:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Grammar Score", f"{proficiency.get('grammar_score', 0)}/10")
                    st.metric("Vocabulary Score", f"{proficiency.get('vocabulary_score', 0)}/10")
                with col2:
                    st.metric("Fluency Score", f"{proficiency.get('fluency_score', 0)}/10")
                    st.metric("Overall Proficiency", proficiency.get('level', 'Not assessed'))
            
            st.markdown("**Strengths:**")
            strengths = ai_insights.get('strengths', [])
            for strength in strengths:
                st.write(f"• {strength}")
            
            st.markdown("**Areas for Improvement:**")
            improvements = ai_insights.get('areas_for_improvement', [])
            for improvement in improvements:
                st.write(f"• {improvement}")
    
    with tab4:
        st.subheader("Personalized Recommendations")
        
        if ai_insights and 'recommendations' in ai_insights:
            recommendations = ai_insights['recommendations']
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"**{i}. {rec['title']}**")
                st.write(rec['description'])
                st.markdown("---")
        else:
            st.info("No specific recommendations available. Focus on maintaining good speaking pace and reducing filler words.")

def team_page():
    st.title("👥 Our Team")
    st.markdown("### Meet the brilliant minds behind this AI-Powered Speech Analysis Application")
    
    # Team members
    team_members = [
        "Rohan Mundhe",
        "Ritesh Yadav", 
        "Aditya Parmale",
        "Harshad Panchal",
        "Yash Kharat",
        "Yash Devkar"
    ]
    
    # Display team in a nice grid layout
    st.markdown("---")
    
    # Create columns for team member display
    cols = st.columns(3)
    
    for i, member in enumerate(team_members):
        with cols[i % 3]:
            st.markdown(f"""
            <div style="
                border: 2px solid #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
                margin: 10px 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            ">
                <h3 style="margin: 0; font-size: 18px;">{member}</h3>
                <p style="margin: 5px 0 0 0; font-size: 14px; opacity: 0.9;">Developer</p>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("""
    ### 🚀 Project Vision
    Our team is dedicated to creating innovative AI solutions that help people improve their communication skills. 
    This speech analysis application represents our commitment to combining cutting-edge technology with practical, 
    user-friendly design.
    
    ### 💡 What We Built
    - **Advanced Audio Processing**: Multi-format support with robust error handling
    - **AI-Powered Analysis**: Comprehensive speech pattern recognition
    - **Interactive Visualizations**: Real-time feedback through engaging charts
    - **User-Centric Design**: Simple, intuitive interface for all skill levels
    
    ### 🎯 Our Mission
    To democratize access to professional speech coaching through AI technology, 
    helping individuals and organizations communicate more effectively.
    """)

if __name__ == "__main__":
    main()
