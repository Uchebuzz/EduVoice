import streamlit as st
import os
import tempfile
from pathlib import Path
from orchestrator import run_document_orchestrator
from chunker import chunk_text_for_narration


st.set_page_config(page_title="Accessible AI Agent", layout="wide")

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

    st.success("File Uploaded. Starting AI Agents...")
    
    if st.button("Start Processing"):

        with st.spinner("Agents are working... (Read -> Vision -> Clean -> Chunk -> Audio)"):
                final_output = run_document_orchestrator(tmp_file_path)  

                st.success("File reading done. Chunking...")
                chunks = chunk_text_for_narration(final_output)
                print(len(chunks))
                st.divider()
                st.header("🎧 Results")
        

st.divider()
st.caption("Powered by Google Vertex AI, Gemini Models & Google Cloud Text-to-Speech")
