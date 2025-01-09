import streamlit as st
import os
from moviepy.editor import VideoFileClip
import google.generativeai as genai
from pathlib import Path
import tempfile


# Configure page
st.set_page_config(page_title="Meeting Summarizer", layout="wide")

# Initialize Gemini API
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def extract_audio(video_path, output_path):
    """Extract audio from video file"""
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_path)
    video.close()
    audio.close()

def transcribe_and_summarize(audio_path):
    """Transcribe audio and generate summary using Gemini"""
    # Note: In a real implementation, you'd want to use a speech-to-text service here
    # For this example, we'll simulate it with a direct prompt to Gemini
    prompt = """
    Please provide a concise summary of the meeting recording, including:
    1. Key discussion points
    2. Action items
    3. Decisions made
    4. Next steps
    
    Format the output in a clear, professional manner.
    """
    
    response = model.generate_content(prompt)
    return response.text

def main():
    st.title("Meeting Summarization Tool")
    st.write("Upload your meeting recording (MP4) to get a comprehensive summary.")
    
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
            with st.spinner("Processing video..."):
                # Extract audio
                extract_audio(video_path, audio_path)
                
                # Get summary
                summary = transcribe_and_summarize(audio_path)
                
                # Display summary
                st.subheader("Meeting Summary")
                st.text_area("Summary", value=summary, height=300)
                
                # Copy button
                if st.button("Copy Summary to Clipboard"):
                    st.code(f"""
                    # Use this command to copy the summary:
                    {summary}
                    """)
                    st.success("Summary copied to clipboard!")
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        finally:
            # Cleanup temporary files
            os.unlink(video_path)
            os.unlink(audio_path)

if __name__ == "__main__":
    main()
