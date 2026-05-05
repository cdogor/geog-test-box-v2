import streamlit as st
import os, json, re
from datetime import datetime
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GEOG V6", layout="wide")

st.title("🌍 GEOG V6 — Physics Engine")

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ---------------- PHYSICS ONTOLOGY ----------------
PHYSICS_CORE = {
    "source": ["current", "mechanical", "electromagnetic"],
    "field": ["electric", "elastic", "EM"],
    "propagation": ["diffusive", "wave", "quasi_static"],
    "medium": ["conductive", "elastic", "dielectric"],
    "observable": ["voltage", "displacement", "field"]
}

PHYSICS_RULES = {
    "electric": ["diffusive", "quasi_static"],
    "elastic": ["wave"],
    "EM": ["wave", "diffusive"]
}

# ---------------- SAFE JSON ----------------
def safe_json(text):

    if not text:
        return {"models": []}

    try:
        return json.loads(text)
    except:
        pass

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except:
            pass

    return {"models": []}

# ---------------- LLM FORWARD ----------------
def forward(text):

    prompt = f"""
Return ONLY JSON:

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

TEXT:
{text}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    return safe_json(r.choices[0].message.content)

# ---------------- REVERSE ----------------
def reverse(model):

    prompt = f"""
Given physics model:

{json.dumps(model)}

Return geophysical methods:

{{
 "methods":[
  {{
   "name":"",
   "confidence":"",
   "use_case":""
  }}
 ]
}}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    return safe_json(r.choices[0].message.content)

# ---------------- SCORE ----------------
def score(m):
    keys = ["source", "field", "propagation", "medium"]
    return sum([1 for k in keys if m.get("physics", {}).get(k)]) / len(keys)

# ---------------- TIME ----------------
def detect_time(text):
    return any(k in text.lower() for k in ["suivi", "monitoring", "evolution", "time"])

# ---------------- UI INPUT ----------------
text = st.text_area("📝 Describe geophysical problem")

expert = st.toggle("Expert mode")

if st.button("RUN"):

    data = forward(text)
    models = data.get("models", [])

    # ---------------- ONTOLOGY DISPLAY ----------------
    with st.expander("📚 Physics Ontology"):
        st.json(PHYSICS_CORE)

    # ---------------- MODELS CARDS ----------------
    st.subheader("📊 Models")

    if not models:
        st.warning("No models returned")
        st.stop()

    ranked = sorted(models, key=lambda m: score(m), reverse=True)

    cols = st.columns(len(ranked))

    selected = None

    for i, m in enumerate(ranked):

        with cols[i]:

            st.markdown("### Model " + str(i+1))
            st.metric("Score", round(score(m), 2))

            st.json(m)

            if st.button("Select " + str(i)):
                selected = m

    if selected is None:
        selected = ranked[0]

    # ---------------- EXPERT EDIT ----------------
    if expert:
        st.subheader("🛠 Expert mode JSON edit")

        edited = st.text_area(
            "Edit model",
            json.dumps(selected, indent=2),
            height=300
        )

        try:
            selected = json.loads(edited)
        except:
            st.warning("Invalid JSON, keeping previous model")

    # ---------------- TIME ----------------
    tl = detect_time(text)

    # ---------------- REVERSE SECTION ----------------
    st.subheader("🔁 Reverse (Physics → Methods)")

    if st.button("Generate methods"):

        methods = reverse(selected)

        with st.container():
            st.json(methods)

    # ---------------- FINAL OUTPUT ----------------
    final = {
        "version": "v6",
        "timestamp": datetime.now().isoformat(),
        "time_lapse": tl,
        "model": selected
    }

    st.subheader("📦 Final structured output")
    st.json(final)

    # ---------------- EXPORT ----------------
    st.download_button(
        "Download JSON",
        json.dumps(final, indent=2),
        "geog_v6.json"
    )