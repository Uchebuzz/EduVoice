import streamlit as st
import os
import tempfile
# from src.agents.planner import AgentPlanner
# from src.utils.protocol import ProcessingRequest

st.set_page_config(page_title="Accessible AI Agent", layout="wide")

st.title("🎙️ AI Agent for Accessibility")
st.markdown("Upload a PDF to receive an audio summary and full narration.")

with st.sidebar:
    st.header("Settings")
    gen_summary = st.checkbox("Generate Summary", value=True)
    gen_full = st.checkbox("Generate Full Audio", value=True)

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    st.success("File Uploaded. Starting AI Agents...")
    
    if st.button("Start Processing"):
        # planner = AgentPlanner()
        # request = ProcessingRequest(
        #     file_path=tmp_file_path,
        #     generate_summary=gen_summary,
        #     generate_full_audio=gen_full
        # )
        
        with st.spinner("Agents are working... (Vision -> Clean -> Script -> Audio)"):
            # try:
            #     # result = planner.execute_pipeline(request)
                
                st.divider()
                st.header("🎧 Results")
                
            #     # if result.summary_audio_path:
            #     #     st.subheader("Executive Summary")
            #     #     st.audio(result.summary_audio_path)
            #     #     with open(result.summary_audio_path, "rb") as f:
            #     #         st.download_button("Download Summary", f, "summary.mp3")

            #     # if result.full_audio_paths:
            #     #     st.subheader("Full Narration (Preview Part 1)")
            #     #     st.audio(result.full_audio_paths[0])
            
            # except Exception as e:
            #     st.error(f"An error occurred: {str(e)}")
            
            # finally:
            #     os.remove(tmp_file_path)

st.divider()
st.caption("Powered by Google Vertex AI Agents & Gemini 1.5 Pro")
