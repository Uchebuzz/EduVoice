
import streamlit as st
import tempfile
from orchestrator import Orchestrator
from chunker import chunk_text_for_narration
from NarratorAgent import NarratorAgent

orchestrator = Orchestrator()
narrator = NarratorAgent()

st.set_page_config(page_title="Accessible AI Agent", layout="wide")

st.title("EduNarrator")
st.markdown("Upload a PDF to receive an audio summary and full narration.")

with st.sidebar:
    st.header("Actions")
    
    gen_full = st.checkbox("Generate Full Audio", value=True )
    gen_summary = st.checkbox("Generate Summary", value=False, disabled=True)
    gen_quiz = st.checkbox("Generate Quiz", value=False, disabled=True)

st.session_state.clear()
uploaded_file = st.file_uploader("Choose a PDF or Docx file", type=["pdf", "docx", "doc"])

if uploaded_file is not None:
    st.success("File Uploaded ",icon='✅')
    suffix = uploaded_file.name.split('.')[1]

    with tempfile.NamedTemporaryFile(delete=False, suffix="."+suffix) as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name
    
    if st.button("Start Processing"):

        with st.spinner("Agents are working... (Read -> Vision -> Clean -> Chunk -> Audio)"):

            final_output = orchestrator.route_task(tmp_file_path)  

            st.success("File reading done.", icon='✅')
            st.session_state["processed_text"] = final_output
            
            chunks = chunk_text_for_narration(final_output)
            st.success("Text Chunking done.", icon='✅')

            final_audio_file = narrator.synthesize_speech(chunks)
            st.session_state["final_audio_file"] = final_audio_file

            st.success("Audio Generation Done", icon='✅')

    if "final_audio_file" in st.session_state:
                final_audio_file = st.session_state["final_audio_file"]
                st.divider()
                st.header("🎧 EduNarrator Results – MP3 Output")
                
                with open(final_audio_file, "rb") as f:
                    audio_bytes = f.read()

                # ---- MP3 audio player ----
                st.audio(audio_bytes, format="audio/mp3")

                # ---- Download MP3 ----
                st.download_button(
                    label="⬇️ Download MP3",
                    data=audio_bytes,
                    file_name=final_audio_file,
                    mime="audio/mpeg"   # correct MIME type for MP3
                )          
        

st.divider()
st.caption("Copyright EduNarrator")
