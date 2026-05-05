import streamlit as st
import os, json, re
from datetime import datetime
from openai import OpenAI

# ---------------- UI ----------------
st.set_page_config(page_title="GEOG SAFE V5", layout="centered")
st.title("🌍 GEOG V5 — SAFE MODE")

# ---------------- API ----------------
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("Missing GROQ_API_KEY in Streamlit Secrets")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ---------------- SAFE JSON PARSER ----------------
def safe_json_parse(text: str):

    if not text:
        return {"models": []}

    # 1. try direct JSON
    try:
        return json.loads(text)
    except:
        pass

    # 2. extract JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    # 3. fallback safe structure
    return {
        "models": [
            {
                "name": "fallback_model",
                "physics": {
                    "source": "unknown",
                    "field": "unknown",
                    "propagation": "unknown",
                    "medium": "unknown"
                },
                "observation": {
                    "sensor": "unknown",
                    "measurand": "unknown"
                }
            }
        ]
    }

# ---------------- LLM SAFE CALL ----------------
def llm_multi(text):

    prompt = f"""
Return ONLY valid JSON.

No text, no markdown, no explanation.

Format:
{{
 "models":[
  {{
   "name":"",
   "physics":{{
    "source":"",
    "field":"",
    "propagation":"",
    "medium":""
   }},
   "observation":{{
    "sensor":"",
    "measurand":""
   }}
  }}
 ]
}}

Input:
{text}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Return strict JSON only"},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = r.choices[0].message.content

    return safe_json_parse(content), content

# ---------------- TIME DETECTION ----------------
def detect_time(text):
    keys = ["suivi", "monitoring", "evolution", "time", "lapse"]
    return any(k in text.lower() for k in keys)

# ---------------- SCORE SIMPLE ----------------
def score(m):
    keys = ["source", "field", "propagation", "medium"]
    present = sum([1 for k in keys if m.get("physics", {}).get(k)])
    return present / len(keys)

# ---------------- UI INPUT ----------------
text = st.text_area("Describe geophysical survey")

if st.button("Run"):

    data, raw = llm_multi(text)
    models = data.get("models", [])

    st.subheader("Raw LLM output (debug)")
    st.code(raw)

    st.subheader("Models")

    if not models:
        st.warning("No models found → fallback used")
        st.json(data)

    ranked = sorted(models, key=lambda m: score(m), reverse=True)

    for i, m in enumerate(ranked):
        st.markdown(f"### Model {i+1}")
        st.write("Score:", round(score(m), 2))
        st.json(m)

    # selection safe
    idx = st.selectbox("Select model", range(len(ranked)) if ranked else [0])

    selected = ranked[idx] if ranked else models[0]

    # time-lapse
    time_flag = detect_time(text)

    final = {
        "geog_version": "v5_safe",
        "timestamp": datetime.now().isoformat(),
        "time_lapse": time_flag,
        "model": selected
    }

    st.subheader("Final output")
    st.json(final)

    # export safe
    st.download_button(
        "Download JSON",
        json.dumps(final, indent=2),
        "geog_v5_safe.json"
    )