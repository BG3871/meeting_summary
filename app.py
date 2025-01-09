import streamlit as st
import os
from moviepy.editor import VideoFileClip
import google.generativeai as genai
from pathlib import Path
import tempfile
import whisper
import torch

# Configure page
st.set_page_config(page_title="Meeting Summarizer", layout="wide")

# Initialize Gemini API
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@st.cache_resource
def load_whisper_model():
    """Load Whisper model - cached to prevent reloading"""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    return whisper.load_model("base", device=device)

def extract_audio(video_path, output_path):
    """Extract audio from video file"""
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_path)
    video.close()
    audio.close()

def transcribe_audio(audio_path):
    """Transcribe audio using Whisper"""
    whisper_model = load_whisper_model()
    result = whisper_model.transcribe(audio_path)
    return result["text"]

def generate_summary(transcript):
    """Generate summary using Gemini"""
    prompt = f"""
    Based on the following meeting transcript, please provide a comprehensive summary:
    
    {transcript}
    
    Please structure the summary as follows:
    1. Key Discussion Points
    2. Action Items
    3. Decisions Made
    4. Next Steps
    
    Format the output in a clear, professional manner.
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("Meeting Summarization Tool")
    st.write("Upload your meeting recording (MP4) to get a comprehensive summary.")
    
    # Display model information
    device = "GPU 🚀" if torch.cuda.is_available() else "CPU"
    st.info(f"Running Whisper on: {device}")
    
    # File uploader
    video_file = st.file_uploader("Choose a video file", type=['mp4'])
    
    if video_file is not None:
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            tmp_video.write(video_file.read())
            video_path = tmp_video.name
            
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_audio:
            audio_path = tmp_audio.name
        
        try:
            # Progress bar
            progress_bar = st.progress(0)
            
            # Extract audio
            with st.spinner("Extracting audio from video..."):
                extract_audio(video_path, audio_path)
                progress_bar.progress(33)
            
            # Transcribe audio
            with st.spinner("Transcribing audio with Whisper..."):
                transcript = transcribe_audio(audio_path)
                progress_bar.progress(66)
                
                # Display transcript
                st.subheader("Meeting Transcript")
                transcript_area = st.text_area("Transcript", value=transcript, height=200)
            
            # Generate summary
            with st.spinner("Generating summary with Gemini..."):
                summary = generate_summary(transcript)
                progress_bar.progress(100)
                
                # Display summary
                st.subheader("Meeting Summary")
                summary_area = st.text_area("Summary", value=summary, height=300)
            
            # Copy buttons in columns
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Copy Transcript"):
                    st.code(transcript)
                    st.success("Transcript copied to clipboard!")
            
            with col2:
                if st.button("Copy Summary"):
                    st.code(summary)
                    st.success("Summary copied to clipboard!")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        finally:
            # Cleanup temporary files
            os.unlink(video_path)
            os.unlink(audio_path)

if __name__ == "__main__":
    main()
