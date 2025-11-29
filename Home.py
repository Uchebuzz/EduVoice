import streamlit as st
import tempfile
from orchestrator import Orchestrator
from chunker import chunk_text_for_narration
from NarratorAgent import NarratorAgent

orchestrator = Orchestrator()
narrator = NarratorAgent()

st.set_page_config(page_title="EduNarrator", layout="wide")
st.title("EduNarrator")

st.sidebar.markdown("Upload a PDF to receive full narration.")
st.markdown(
    "<span style='font-size:17px; font-weight:600;'>🎧 This system produces complete, accessible narration to help blind and visually impaired students learn independently.</span>",
    unsafe_allow_html=True
)

#-------------Actions---------------
with st.sidebar:
    st.header("Actions")
    
    gen_full = st.checkbox("Generate Full Audio", value=True )
    gen_summary = st.checkbox("Generate Summary", value=False, disabled=True)
    gen_quiz = st.checkbox("Generate Quiz", value=False, disabled=True)

# -------------------- initialize session state defaults (only if absent) --------------------
defaults = {
    "file_uploaded": False,
    "tmp_file_path": None,
    "processing_started": False,
    "processed_text": None,
    "chunked_text": None,
    "audio_ready": False,
    "final_audio_file": None,
    # selected voice stored persistently
    "voice_key": "English (en-US)",
}
for k, v in defaults.items():
    st.session_state.setdefault(k, v)

# -------------------- upload UI -------------------
uploaded_file = st.file_uploader("Upload a PDF or DOCX", type=["pdf", "docx", "doc"])

# If user uploads a new file, save once and set flags. DON'T re-run this on ordinary reruns.
if uploaded_file is not None:
    # if new upload (no tmp or different filename), write tmp and reset processing state
    prev_tmp = st.session_state.get("tmp_file_path")
    # check name to avoid re-saving same file on rerun
    incoming_name = uploaded_file.name
    if (not prev_tmp) or (st.session_state.get("_uploaded_name") != incoming_name):
        # save file to tmp and set state
        suffix = "." + incoming_name.split(".")[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.getvalue())
            tmp_path = tmp.name
        st.session_state["tmp_file_path"] = tmp_path
        st.session_state["_uploaded_name"] = incoming_name

        # Reset pipeline state for new upload
        st.session_state["file_uploaded"] = True
        st.session_state["processing_started"] = False
        st.session_state["processed_text"] = None
        st.session_state["chunked_text"] = None
        st.session_state["audio_ready"] = False
        st.session_state["final_audio_file"] = None
        # voice_key keep default or user choice preserved

        st.success(f"Uploaded: {incoming_name}", icon="✅")

    if(st.session_state.processed_text):
        st.success("Processing complete ✅")
    else:    
    # If we already have a tmp file from previous upload, show filename
        if st.session_state.file_uploaded and st.session_state.tmp_file_path:
            st.info(f"Ready to process: {st.session_state.get('_uploaded_name')}")

        # -------------------- Start Processing button --------------------
        if st.button("Start Processing", key="start_processing_btn"):
            with st.spinner("Reading PDF → Vision → Cleaning → Chunking ..."):
                final_output = orchestrator.route_task(st.session_state.tmp_file_path)

                st.session_state.processed_text = final_output
                st.session_state.chunked_text = chunk_text_for_narration(final_output)
                st.success("Processing complete ✅")

        

    # -------------------- Voice selection (persistent) --------------------
    # Only show voice selector when we have chunked text
    if st.session_state.chunked_text is not None:

        LANGUAGE_CODE_MAP = {
            "Hindi (hi-IN)": "hi-IN",
            "English (en-IN)": "en-IN",
            "English (en-US)": "en-US",
            "English (en-GB)": "en-GB",
        }

        voice_options = list(LANGUAGE_CODE_MAP.keys())

        # ensure default in session (do not overwrite if user already selected)
        st.session_state.setdefault("voice_key", st.session_state["voice_key"])

        # IMPORTANT: give selectbox a stable key and set index using current session value
        try:
            default_index = voice_options.index(st.session_state["voice_key"])
        except ValueError:
            default_index = 0

        selected_voice = st.selectbox(
            "Select Narration Voice",
            options=voice_options,
            index=default_index,
            key="voice_selection_box",  # persistent key
            help="Choose voice (selection won't trigger processing — press Generate Audio when ready).",
        )

        # Save the user's choice to session_state.voice_key exactly once (this persists across reruns)
        if selected_voice != st.session_state.get("voice_key"):
            st.session_state["voice_key"] = selected_voice

        # Only synthesize when user explicitly clicks this button
        if st.button("Generate Audio", key="generate_audio_btn"):
            with st.spinner("Generating audio..."):
                voice_code = LANGUAGE_CODE_MAP[st.session_state["voice_key"]]
                # narrator.synthesize_speech should return path to saved mp3 file
                final_audio_path = narrator.synthesize_speech(
                    chunks=st.session_state.chunked_text, language=voice_code
                )
                st.session_state["final_audio_file"] = final_audio_path
                st.session_state["audio_ready"] = True
            st.success("Audio generation done ✅")

    # -------------------- Audio playback + download (persistent) --------------------
    if st.session_state.audio_ready and st.session_state.final_audio_file:
        st.divider()
        st.markdown("<b style='font-size:18px;'>🎧 EduNarrator – MP3 Output</b>", unsafe_allow_html=True)

        try:
            with open(st.session_state.final_audio_file, "rb") as fh:
                audio_bytes = fh.read()

            st.audio(audio_bytes, format="audio/mp3")

            # download button — will rerun the script BUT state is preserved in st.session_state
            st.download_button(
                label="⬇️ Download MP3",
                data=audio_bytes,
                file_name="edunarrator_output.mp3",
                mime="audio/mpeg",
                key="download_btn",
            )
        except FileNotFoundError:
            st.error("Audio file not found. Please re-generate.")

st.caption("© EduNarrator AI")
