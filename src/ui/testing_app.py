import os
import uuid
import asyncio
import streamlit as st
from src.nlp_engine.stt import get_stt_provider
from src.nlp_engine.tts import get_tts_provider

# Streamlit App Configuration
st.set_page_config(page_title="Syrian Arabic Voice Agent Tester", layout="wide")
st.title("🍗 Charco Chicken Voice Agent - Tester UI")

# Sidebar for Configuration
st.sidebar.header("⚙️ Configuration")
stt_provider_name = st.sidebar.selectbox("Select STT Provider", ["whisper", "google", "azure"], index=0) # Default to Whisper
tts_provider_name = st.sidebar.selectbox("Select TTS Provider", ["elevenlabs", "playht", "gtts"], index=0) # Default to ElevenLabs

# Initialize Session State for Audio Playback
if 'last_tts_audio_path' not in st.session_state:
    st.session_state.last_tts_audio_path = None

# Run Async Code
async def run_tts(tts_engine, text, path):
    """Helper to run TTS synthesize asynchronously."""
    return await tts_engine.synthesize(text, output_file_path=path)

async def run_stt(stt_engine, path):
    """Helper to run STT transcribe asynchronously."""
    return await stt_engine.transcribe(path)


# Main Content Area
st.header("🔤 Text-to-Speech (TTS) Test")
tts_input_text = st.text_area("Enter Syrian Arabic text for the agent to say:", height=100,
                              value="مرحباً! شو اقدر أساعدك فيه اليوم؟")
tts_button = st.button("🔊 Generate Speech")

if tts_button and tts_input_text:
    with st.spinner("Generating speech..."):
        try:
            # Get the TTS provider instance
            tts_engine = get_tts_provider(tts_provider_name)

            os.makedirs("data/ui_output", exist_ok=True)
            unique_filename = f"tts_output_{uuid.uuid4().hex}.mp3"
            tts_output_path = os.path.join("data/ui_output", unique_filename)

            # Run the async TTS function
            asyncio.run(run_tts(tts_engine, tts_input_text, tts_output_path))

            # Store the path in session state for playback
            st.session_state.last_tts_audio_path = tts_output_path

            st.success("✅ Speech generated successfully!")

        except Exception as e:
            st.error(f"❌ Error in TTS: {e}")

# Play the last generated TTS audio
if st.session_state.last_tts_audio_path and os.path.exists(st.session_state.last_tts_audio_path):
    st.audio(st.session_state.last_tts_audio_path, format='audio/mp3')
    with open(st.session_state.last_tts_audio_path, "rb") as audio_file:
        st.download_button(
            label="⬇️ Download TTS Audio",
            data=audio_file,
            file_name=os.path.basename(st.session_state.last_tts_audio_path),
            mime="audio/mp3"
        )


# Audio File Upload for STT
st.header("🎤 Speech-to-Text (STT) Test")
st.info("ℹ️ Upload an audio file containing Syrian Arabic speech.")
uploaded_audio_file = st.file_uploader("Choose an audio file (WAV, MP3)", type=['wav', 'mp3'])

if uploaded_audio_file is not None:
    with st.spinner("Transcribing audio..."):
        try:
            # Save the uploaded file
            os.makedirs("data/ui_temp", exist_ok=True)
            temp_audio_path = os.path.join("data/ui_temp", uploaded_audio_file.name)
            with open(temp_audio_path, "wb") as f:
                f.write(uploaded_audio_file.getbuffer())

            # Get the STT provider instance
            stt_engine = get_stt_provider(stt_provider_name)

            # Run the async STT function
            transcription = asyncio.run(run_stt(stt_engine, temp_audio_path))

            st.success("✅ Audio transcribed successfully!")
            st.subheader("📝 Transcribed Text:")
            st.markdown(f"**{transcription}**")

            # Display the uploaded audio
            st.audio(temp_audio_path)

        except Exception as e:
            st.error(f"❌ Error in STT: {e}")
        finally:
            # Clean the temporary file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

# Agent Interaction Simulation (Placeholder)
st.header("Agent Interaction (Placeholder)")
st.write("This section will simulate the full agent interaction once core components are integrated.")
st.write("It will involve:")
st.markdown("- Taking audio input (via upload or potentially live mic in advanced setups)")
st.markdown("- Sending it to STT")
st.markdown("- Processing the text (intent detection, dialogue management - coming later)")
st.markdown("- Generating a response text")
st.markdown("- Sending the response to TTS")
st.markdown("- Playing back the generated audio")