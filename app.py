"""
AI Crop Doctor — Instant Plant Disease Diagnosis for Farmers
Built for HackDevengers 1.0 (AI / GenAI track)

A multimodal AI assistant that lets a farmer upload a photo of a diseased
crop leaf and instantly get a diagnosis, an actionable treatment plan
(organic + chemical), and the advice translated into a local language —
with optional text-to-speech for low-literacy accessibility.

Uses Google Gemini (free tier) for the multimodal AI call.
"""

import os
import io

import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="AI Crop Doctor",
    page_icon="🌾",
    layout="centered",
)

MODEL = "gemini-2.0-flash"  # multimodal (vision) capable model, free tier

LANGUAGES = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Bengali (বাংলা)": "bn",
}


def get_model():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error(
            "No API key found. Set the GEMINI_API_KEY environment variable "
            "before running the app (see README)."
        )
        st.stop()
    genai.configure(api_key=api_key)
    return genai.GenerativeModel(MODEL)


def load_image(uploaded_file):
    """Read an uploaded image file and return a PIL Image."""
    return Image.open(uploaded_file)


def diagnose(model, image, symptoms_text, language):
    """Call Gemini's vision model to diagnose the crop disease."""
    prompt = f"""You are an expert agricultural plant pathologist helping a
farmer who may have limited literacy or technical background.

Look at the attached photo of a crop leaf/plant. The farmer additionally
describes the problem as: "{symptoms_text or 'No additional description given.'}"

Respond ENTIRELY in {language}. Structure your response with these exact
section headers (translated into {language}):

1. **Diagnosis** — Name of the likely disease/pest/deficiency (plain language,
   1-2 sentences), and how confident you are.
2. **Why this is happening** — A short, simple explanation a farmer can
   understand (2-3 sentences).
3. **Immediate treatment** — 3-5 concrete, actionable steps. Include BOTH an
   organic/low-cost option and a chemical option where relevant.
4. **Prevention** — 2-3 tips to stop this from happening again next season.

Keep language extremely simple and practical. Avoid jargon. If the image is
unclear or doesn't show a plant, say so honestly instead of guessing.
"""

    response = model.generate_content([prompt, image])
    return response.text


def text_to_speech(text, lang_code):
    """Convert diagnosis text to speech audio bytes (mp3) using gTTS."""
    try:
        tts = gTTS(text=text, lang=lang_code)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf
    except Exception:
        return None


# ----------------------------------------------------------------------
# UI
# ----------------------------------------------------------------------
st.title("🌾 AI Crop Doctor")
st.caption(
    "Upload a photo of a sick plant. Get an instant diagnosis and treatment "
    "plan — in your own language, with audio."
)

with st.sidebar:
    st.header("Settings")
    language_label = st.selectbox("Output language", list(LANGUAGES.keys()))
    language_code = LANGUAGES[language_label]
    enable_audio = st.checkbox("🔊 Read advice aloud", value=True)
    st.markdown("---")
    st.markdown(
        "**About**\n\n"
        "AI Crop Doctor uses a multimodal AI model to diagnose crop "
        "diseases from a single photo, then gives simple, actionable "
        "treatment advice in the farmer's own language."
    )

uploaded_file = st.file_uploader(
    "📷 Upload a photo of the affected leaf/plant",
    type=["jpg", "jpeg", "png", "webp"],
)

symptoms_text = st.text_area(
    "Describe what you're seeing (optional — any language)",
    placeholder="e.g. Yellow spots spreading on the leaves, started 3 days ago...",
)

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded photo", use_container_width=True)

diagnose_clicked = st.button("🔍 Diagnose", type="primary", disabled=uploaded_file is None)

if diagnose_clicked and uploaded_file is not None:
    with st.spinner("Analyzing the plant..."):
        model = get_model()
        image = load_image(uploaded_file)
        result_text = diagnose(model, image, symptoms_text, language_label)

    st.success("Diagnosis complete")
    st.markdown(result_text)

    if enable_audio:
        with st.spinner("Generating audio..."):
            audio_buf = text_to_speech(result_text, language_code)
        if audio_buf:
            st.audio(audio_buf, format="audio/mp3")
        else:
            st.info("Audio generation isn't available for this language right now.")

    st.markdown("---")
    st.caption(
        "⚠️ This tool provides general guidance only and is not a substitute "
        "for advice from a local agricultural extension officer, especially "
        "for large-scale or high-value crops."
    )
elif uploaded_file is None:
    st.info("Upload a photo to get started.")
