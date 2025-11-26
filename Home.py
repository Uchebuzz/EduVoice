import streamlit as st
import os
import tempfile
from orchestrator import run_document_orchestrator


st.set_page_config(page_title="Accessible AI Agent", layout="wide")

st.title("🎙️ AI Agent for Accessibility")
st.markdown("Upload a PDF to receive an audio summary and full narration.")

with st.sidebar:
    st.header("Settings")
    gen_summary = st.checkbox("Generate Summary", value=True)
    gen_full = st.checkbox("Generate Full Audio", value=True)

uploaded_file = st.file_uploader("Choose a PDF or Docx file", type=["pdf", "docx", "doc"])

if uploaded_file is not None:
    suffix = uploaded_file.name.split('.')[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix="."+suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    st.success("File Uploaded. Starting AI Agents...")
    
    if st.button("Start Processing"):

        with st.spinner("Agents are working... (Vision -> Clean -> Script -> Audio)"):
                final_output = run_document_orchestrator(tmp_file_path)  
                st.divider()
                st.header("🎧 Results")
        

st.divider()
st.caption("Powered by Google Vertex AI Agents & Gemini 1.5 Pro")
