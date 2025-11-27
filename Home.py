import streamlit as st
import os
import tempfile
from pathlib import Path
from orchestrator import run_document_orchestrator
from agent4 import synthesize_speech
import google.generativeai as genai

# Configure Gemini for summary generation
# Note: You'll need to set your API key - consider using environment variables
try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY", "API key"))
    summary_model = genai.GenerativeModel("gemini-2.0-flash-lite-preview")
except:
    summary_model = None

st.set_page_config(page_title="EduVoice - AI Agent for Accessibility", layout="wide")

st.title("🎙️ EduVoice - AI Agent for Accessibility")
st.markdown("Upload a PDF or Word document to receive processed text and audio narration.")

with st.sidebar:
    st.header("⚙️ Settings")
    gen_summary = st.checkbox("Generate Summary Audio", value=True)
    gen_full = st.checkbox("Generate Full Audio", value=True)
    
    st.divider()
    st.header("🎤 Voice Settings")
    voice_gender = st.selectbox("Voice Gender", ["NEUTRAL", "MALE", "FEMALE"], index=0)
    language_code = st.text_input("Language Code", value="en-US", help="BCP-47 language code (e.g., en-US, en-GB, fr-FR)")
    
    st.divider()
    if st.button("🗑️ Clear Results", help="Clear all processed results"):
        for key in ['processed_text', 'summary_text', 'summary_audio', 'full_audio']:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

uploaded_file = st.file_uploader("Choose a PDF or Word document", type=["pdf", "docx", "doc"])

# Initialize session state to store results
if 'processed_text' not in st.session_state:
    st.session_state.processed_text = None
if 'summary_text' not in st.session_state:
    st.session_state.summary_text = None
if 'summary_audio' not in st.session_state:
    st.session_state.summary_audio = None
if 'full_audio' not in st.session_state:
    st.session_state.full_audio = None
if 'temp_file_path' not in st.session_state:
    st.session_state.temp_file_path = None

if uploaded_file is not None:
    suffix = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'pdf'
    
    # Store uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        st.session_state.temp_file_path = tmp_file.name

    st.success(f"✅ File '{uploaded_file.name}' uploaded successfully!")
    
    if st.button("🚀 Start Processing", type="primary"):
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Document Processing
            status_text.text("📄 Processing document... (Extracting text, analyzing images)")
            progress_bar.progress(10)
            
            processed_text = run_document_orchestrator(st.session_state.temp_file_path)
            st.session_state.processed_text = processed_text
            
            progress_bar.progress(50)
            status_text.text("✅ Document processed! Text extracted and cleaned.")
            
            # Step 2: Generate Summary (if requested)
            summary_text = None
            if gen_summary and processed_text:
                status_text.text("📝 Generating summary...")
                progress_bar.progress(60)
                
                # Create a comprehensive summary of the full document
                if summary_model:
                    try:
                        # Create a better summary prompt for the full document
                        summary_input = processed_text[:10000] if len(processed_text) > 10000 else processed_text
                        prompt = f"""Create a comprehensive summary of this document in 3-5 sentences. 
                        Highlight the main topics, key points, and important information:
                        
                        {summary_input}
                        """
                        response = summary_model.generate_content(prompt)
                        summary_text = response.text.strip() if response.text else None
                    except Exception as e:
                        st.warning(f"Could not generate AI summary: {e}")
                        summary_text = None
                
                if not summary_text:
                    # Fallback: create a simple summary from first paragraphs
                    lines = processed_text.split('\n')[:15]
                    summary_text = ' '.join([line.strip() for line in lines if line.strip()])[:800]
                    summary_text = f"Document Summary:\n\n{summary_text}..."
                
                # Store summary text in session state
                st.session_state.summary_text = summary_text
                
                progress_bar.progress(70)
                status_text.text("🔊 Generating summary audio...")
                
                summary_audio_bytes = synthesize_speech(
                    text=summary_text,
                    gender=voice_gender,
                    language=language_code
                )
                st.session_state.summary_audio = summary_audio_bytes
                progress_bar.progress(80)
            
            # Step 3: Generate Full Audio (if requested)
            if gen_full and processed_text:
                status_text.text("🔊 Generating full audio... (This may take a while)")
                progress_bar.progress(85)
                
                # Split text into chunks if too long (TTS has limits)
                max_chunk_length = 4500  # Safe limit for TTS
                text_chunks = []
                
                if len(processed_text) > max_chunk_length:
                    # Split by paragraphs to avoid breaking sentences
                    paragraphs = processed_text.split('\n\n')
                    current_chunk = ""
                    
                    for para in paragraphs:
                        if len(current_chunk) + len(para) < max_chunk_length:
                            current_chunk += para + "\n\n"
                        else:
                            if current_chunk:
                                text_chunks.append(current_chunk.strip())
                            current_chunk = para + "\n\n"
                    
                    if current_chunk:
                        text_chunks.append(current_chunk.strip())
                else:
                    text_chunks = [processed_text]
                
                # Generate audio for each chunk
                audio_chunks = []
                for i, chunk in enumerate(text_chunks):
                    if chunk.strip():
                        chunk_audio = synthesize_speech(
                            text=chunk,
                            gender=voice_gender,
                            language=language_code
                        )
                        audio_chunks.append(chunk_audio)
                        progress_bar.progress(85 + int((i + 1) / len(text_chunks) * 10))
                
                # Combine all audio chunks (simple concatenation - for production, use pydub)
                if audio_chunks:
                    full_audio_bytes = b''.join(audio_chunks)
                    st.session_state.full_audio = full_audio_bytes
                
                progress_bar.progress(95)
            
            progress_bar.progress(100)
            status_text.text("✅ Processing complete!")
            
            # Clean up temp file after processing
            if st.session_state.temp_file_path and os.path.exists(st.session_state.temp_file_path):
                try:
                    os.unlink(st.session_state.temp_file_path)
                except:
                    pass
            
        except Exception as e:
            st.error(f"❌ Error during processing: {str(e)}")
            st.exception(e)
            progress_bar.progress(0)
            status_text.text("")

# Display Results Section
if st.session_state.processed_text:
    st.divider()
    st.header("🎧 Results")
    
    # Tab layout for different outputs
    tab1, tab2, tab3 = st.tabs(["📄 Processed Text", "📝 Summary Audio", "🎵 Full Audio"])
    
    with tab1:
        st.subheader("Processed and Cleaned Text")
        st.text_area(
            "Text Output",
            value=st.session_state.processed_text,
            height=400,
            disabled=True,
            label_visibility="collapsed"
        )
        
        # Download button for text
        st.download_button(
            label="📥 Download Text as .txt",
            data=st.session_state.processed_text,
            file_name="processed_text.txt",
            mime="text/plain"
        )
    
    with tab2:
        if gen_summary and st.session_state.processed_text:
            # Display summary text if we can extract it
            st.subheader("Summary")
            
            # Try to get summary text (we'll store it in session state if needed)
            if 'summary_text' in st.session_state and st.session_state.summary_text:
                st.text_area(
                    "Summary Text",
                    value=st.session_state.summary_text,
                    height=150,
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            if st.session_state.summary_audio:
                st.subheader("Summary Audio")
                st.audio(st.session_state.summary_audio, format="audio/mp3")
                
                st.download_button(
                    label="📥 Download Summary Audio (MP3)",
                    data=st.session_state.summary_audio,
                    file_name="summary_audio.mp3",
                    mime="audio/mp3"
                )
            else:
                st.info("⚠️ Summary audio generation is in progress or failed. Please try again.")
        else:
            st.info("ℹ️ Summary audio was not generated. Enable 'Generate Summary Audio' in settings.")
    
    with tab3:
        if st.session_state.full_audio:
            st.subheader("Full Audio Narration")
            st.audio(st.session_state.full_audio, format="audio/mp3")
            
            st.download_button(
                label="📥 Download Full Audio (MP3)",
                data=st.session_state.full_audio,
                file_name="full_audio.mp3",
                mime="audio/mp3"
            )
        else:
            st.info("ℹ️ Full audio was not generated. Enable 'Generate Full Audio' in settings.")

st.divider()
st.caption("Powered by Google Vertex AI, Gemini Models & Google Cloud Text-to-Speech")
