import streamlit as st
from moviepy import VideoFileClip
import os
import tempfile
from pathlib import Path

def extract_audio(video_path, output_path):
    """Extract audio from video file"""
    video = VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(output_path)
    video.close()
    audio.close()

def main():
    st.title("Video to Audio Converter")
    st.write("Upload your MP4 file to extract the audio as MP3.")
    
    # File uploader
    video_file = st.file_uploader("Choose a video file", type=['mp4'])
    
    if video_file is not None:
        # Get original filename without extension
        original_filename = Path(video_file.name).stem
        
        # Create temporary files for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_video:
            tmp_video.write(video_file.read())
            video_path = tmp_video.name
            
        output_path = f"{original_filename}.mp3"
        
        try:
            with st.spinner("Converting video to audio..."):
                # Extract audio
                extract_audio(video_path, output_path)
                
                # Read the generated MP3 file
                with open(output_path, 'rb') as audio_file:
                    audio_bytes = audio_file.read()
                
                # Create download button
                st.success("Conversion completed!")
                st.download_button(
                    label="Download MP3",
                    data=audio_bytes,
                    file_name=f"{original_filename}.mp3",
                    mime="audio/mpeg"
                )
                
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            
        finally:
            # Cleanup temporary files
            os.unlink(video_path)
            if os.path.exists(output_path):
                os.unlink(output_path)

if __name__ == "__main__":
    main()
