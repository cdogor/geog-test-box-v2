import streamlit as st
import os, json, re
from datetime import datetime
from openai import OpenAI

# ---------------- UI ----------------
st.set_page_config(page_title="GEOG V7.1", layout="wide")
st.title("🌍 GEOG V7.1 — Integrated Geo Physics Engine")

# ---------------- API ----------------
API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ---------------- ONTOLOGY (EXAMPLES ONLY) ----------------
ONTOLOGY = {
    "source_examples": [
        "electrical potential gradient",
        "mechanical stress/strain",
        "electromagnetic excitation",
        "chemical potential gradient",
        "thermal gradient",
        "fluid pressure gradient"
    ],
    "propagation_examples": [
        "diffusive transport",
        "wave propagation",
        "quasi-static field",
        "advective transport",
        "poroelastic coupling"
    ],
    "medium_examples": [
        "porous medium",
        "fractured rock",
        "electrolyte solution",
        "elastic solid"
    ],
    "observation_examples": [
        "voltage difference",
        "electrode potential",
        "wave amplitude",
        "apparent resistivity"
    ]
}

# ---------------- SAFE JSON ----------------
def safe_json(text):
    if not text:
        return {}

    try:
        return json.loads(text)
    except:
        pass

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    return {}

# ---------------- FORWARD ----------------
def forward(text):

    prompt = f"""
Return ONLY JSON.

{{
 "model": {{
  "source": "",
  "propagation": "",
  "medium": "",
  "observation": "",
  "coupling": ""
 }}
}}

TEXT:
{text}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return safe_json(r.choices[0].message.content)

# ---------------- REVERSE ----------------
def reverse(model):

    prompt = f"""
Given model:

{json.dumps(model)}

Return ONLY JSON:

{{
 "methods":[
  {{
   "name":"",
   "confidence":0.0,
   "reason":""
  }}
 ]
}}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return safe_json(r.choices[0].message.content)

# ---------------- INTERPRETATION (NEW) ----------------
def interpret(model, text):

    prompt = f"""
You are a geophysics expert.

Given:

Model:
{json.dumps(model)}

Text:
{text}

Return ONLY JSON:

{{
 "principle": "",
 "laws": [],
 "identified_methods": [],
 "free_explanation": ""
}}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    try:
        return json.loads(r.choices[0].message.content)
    except:
        return {
            "principle": "unparsed",
            "laws": [],
            "identified_methods": [],
            "free_explanation": r.choices[0].message.content
        }

# ---------------- TIME ----------------
def detect_time(text):
    return any(k in text.lower() for k in ["suivi", "monitoring", "evolution", "time", "lapse"])

# ---------------- SCORE ----------------
def score(m):
    keys = ["source", "propagation", "medium", "observation"]
    return sum([1 for k in keys if m.get(k)]) / len(keys)

# ---------------- INPUT ----------------
text = st.text_area("🧠 Describe geophysical problem")

expert = st.toggle("Expert mode")

if st.button("RUN V7.1"):

    model = forward(text).get("model", {})

    interp = interpret(model, text)

    time_flag = detect_time(text)

    # ---------------- ONTOLOGY ----------------
    with st.expander("📚 Ontology examples"):
        st.json(ONTOLOGY)

    # ---------------- 3 MAIN BLOCKS UI ----------------

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🧠 Physics model")
        st.metric("Completeness", round(score(model), 2))
        st.json(model)

    with col2:
        st.subheader("🔁 Reverse methods")
        rev = reverse(model)
        st.json(rev)

    with col3:
        st.subheader("📘 Interpretation")
        st.json(interp)

    # ---------------- EXPERT MODE ----------------
    if expert:
        st.subheader("🛠 Expert edit (model)")
        edited = st.text_area(
            "Edit JSON model",
            json.dumps(model, indent=2),
            height=250
        )
        try:
            model = json.loads(edited)
        except:
            st.warning("Invalid JSON")

    # ---------------- FINAL ----------------
    final = {
        "geog_version": "v7.1",
        "timestamp": datetime.now().isoformat(),
        "time_lapse": time_flag,
        "model": model,
        "interpretation": interp,
        "reverse": rev
    }

    st.subheader("📦 Final output")
    st.json(final)

    # ---------------- EXPORT ----------------
    st.download_button(
        "Download JSON",
        json.dumps(final, indent=2),
        "geog_v7_1.json"
    )