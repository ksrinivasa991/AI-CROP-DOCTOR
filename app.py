"""
AI Crop Doctor — Instant Plant Disease Diagnosis for Farmers
Built for HackDevengers 1.0 (AI / GenAI track)

A multimodal AI assistant that lets a farmer upload a photo of a diseased
crop leaf and instantly get a diagnosis, an actionable treatment plan
(organic + chemical), and the advice translated into a local language —
with optional text-to-speech for low-literacy accessibility.

Uses Groq (free tier, Llama 4 Scout vision model) for the multimodal AI call.
"""

import base64
import os
import io
import re

import streamlit as st
from groq import Groq
from gtts import gTTS

# ----------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="AI Crop Doctor",
    page_icon="🌾",
    layout="centered",
)

MODEL = "qwen/qwen3.6-27b"  # vision-capable, free tier

LANGUAGES = {
    "English": "en",
    "Hindi (हिंदी)": "hi",
    "Telugu (తెలుగు)": "te",
    "Tamil (தமிழ்)": "ta",
    "Kannada (ಕನ್ನಡ)": "kn",
    "Bengali (বাংলা)": "bn",
}


def get_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        st.error(
            "No API key found. Set the GROQ_API_KEY environment variable "
            "before running the app (see README)."
        )
        st.stop()
    return Groq(api_key=api_key)


def image_to_base64(uploaded_file):
    """Read an uploaded image file and return (base64_str, media_type)."""
    bytes_data = uploaded_file.getvalue()
    media_type = uploaded_file.type or "image/jpeg"
    b64 = base64.b64encode(bytes_data).decode("utf-8")
    return b64, media_type


def diagnose(client, image_b64, media_type, symptoms_text, language):
    """Call Groq's vision model to diagnose the crop disease."""
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

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_b64}"
                        },
                    },
                ],
            }
        ],
        max_tokens=1200,
        reasoning_effort="none",
    )
    raw_text = response.choices[0].message.content or ""
    # Safety net: strip any <think>...</think> block if the model adds one anyway
    clean_text = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
    return clean_text if clean_text else raw_text.strip()


def text_to_speech(text, lang_code):
    """Convert diagnosis text to speech audio bytes (mp3) using gTTS."""
    try:
        # Strip markdown symbols that can trip up the TTS engine
        clean_text = re.sub(r"[*#_`]", "", text)
        tts = gTTS(text=clean_text, lang=lang_code)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        buf.seek(0)
        return buf
    except Exception as e:
        st.caption(f"(Audio unavailable: {e})")
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
        client = get_client()
        img_b64, media_type = image_to_base64(uploaded_file)
        result_text = diagnose(client, img_b64, media_type, symptoms_text, language_label)

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
