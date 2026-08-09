# 🌾 AI Crop Doctor
### Instant, multilingual plant-disease diagnosis for farmers — built for HackDevengers 1.0

## The Problem
Crop disease is one of the leading causes of yield loss for smallholder
farmers worldwide — often **20–40% of production is lost** to pests and
disease every year. Most farmers don't have easy access to an agricultural
expert when they first spot a problem, and by the time help arrives, it's
often too late. Existing digital tools are usually text-heavy, in English,
and assume a level of literacy or tech comfort many farmers don't have.

## The Solution
**AI Crop Doctor** turns a smartphone photo into an instant expert opinion.

1. 📷 Farmer photographs the affected leaf/plant
2. ✍️ Optionally describes the symptoms in their own words
3. 🤖 A multimodal AI model (Claude) diagnoses the disease and generates a
   simple, actionable treatment plan — both **organic/low-cost** and
   **chemical** options
4. 🌐 The advice is delivered in the farmer's **own language** (Hindi,
   Telugu, Tamil, Kannada, Bengali, English)
5. 🔊 An **audio version** is generated automatically, so low-literacy
   users can just listen

This isn't a generic chatbot — it's a focused, visual, high-impact tool
that solves a real problem for one of the world's largest and most
underserved user groups: farmers.

## Tech Stack
- **Frontend:** Streamlit (fast, clean, demo-ready UI)
- **AI:** Google Gemini (multimodal vision + language model, free tier) for
  diagnosis, explanation, and translation in a single call
- **Accessibility:** gTTS (Google Text-to-Speech) for audio output
- **Language:** Python

## Why This Approach
- **Multimodal, not just text:** the AI actually looks at the photo — this
  is technically more interesting than a text-only chatbot and far more
  useful to a farmer who can't describe a disease in words.
- **One model call, multiple outputs:** diagnosis, treatment plan, and
  translation all happen together, keeping the app fast and the codebase
  simple — important for an 8-hour build.
- **Accessibility-first:** language selection + audio output means this
  tool works for users with low literacy, which is the reality for a large
  share of the target audience.

## Running It Locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set your Gemini API key (get one free at aistudio.google.com/apikey)
export GEMINI_API_KEY="your-key-here"         # macOS/Linux
setx GEMINI_API_KEY "your-key-here"           # Windows

# 3. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## Demo Flow (for judges)
1. Open the app, pick a language (e.g. Hindi)
2. Upload a sample photo of a diseased leaf (a quick Google Images search
   for "tomato leaf blight" or "wheat rust" gives good test photos)
3. Optionally type a one-line symptom description
4. Click **Diagnose** — within seconds, get a structured diagnosis,
   treatment plan, and audio playback in the selected language

## Future Roadmap
- Offline-first mode with a lightweight on-device model for low-connectivity
  areas
- WhatsApp bot integration (huge reach in rural India with zero app install)
- Community disease-outbreak map — aggregate anonymized diagnoses to warn
  nearby farmers of spreading outbreaks
- Integration with local agri-extension helplines for escalation on
  high-value/large-scale crops

## Team / Track
- **Track:** Artificial Intelligence / Generative AI
- **Type:** Individual participation
- **Built for:** HackDevengers 1.0
