import streamlit as st
import os, json
from datetime import datetime
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GEOG V4", layout="wide")
st.title("🌍 GEOG V4 — Pro")

# ---------------- API ----------------
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("Missing API key")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ---------------- CORE ----------------
PHYSICS_CORE = {
    "source": ["current", "mechanical", "em_wave"],
    "field": ["electric", "elastic", "electromagnetic"],
    "propagation": ["diffusive", "wave", "quasi_static"],
    "medium": ["conductive", "elastic", "dielectric"]
}

PHYSICS_RULES = {
    "electric": ["diffusive", "quasi_static"],
    "elastic": ["wave"],
    "electromagnetic": ["wave", "diffusive"]
}

# ---------------- LLM ----------------
def llm_multi(text):

    prompt = f"""
Return 3 physical models JSON:

{{
 "models":[
  {{
   "name":"",
   "physics":{{"source":"","field":"","propagation":"","medium":""}},
   "observation":{{"sensor":"","measurand":""}}
  }}
 ]
}}
TEXT:{text}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    return json.loads(r.choices[0].message.content)

# ---------------- VALIDATION ----------------
def validate(m):

    field = m["physics"].get("field")
    prop = m["physics"].get("propagation")

    if field in PHYSICS_RULES:
        if prop not in PHYSICS_RULES[field]:
            return False

    return True

def score(m):

    keys = ["source","field","propagation","medium"]
    comp = sum([1 for k in keys if m["physics"].get(k)]) / len(keys)

    coh = 1 if validate(m) else 0

    return comp, coh

# ---------------- TIME ----------------
def detect_time(text):
    return any(k in text.lower() for k in ["suivi","monitoring","evolution"])

# ---------------- BUILD ----------------
def build(model, tl):

    out = {
        "geog_version": "v4",
        "timestamp": datetime.now().isoformat(),
        "physics": model["physics"],
        "observation": model["observation"],
        "time": {
            "type": "time_lapse" if tl else "static"
        },
        "validation": {
            "coherent": validate(model)
        }
    }

    return out

# ---------------- UI ----------------
text = st.text_area("📝 Describe your survey")

expert = st.toggle("Expert mode")

if st.button("Run"):

    data = llm_multi(text)
    models = data["models"]

    results = []

    for m in models:
        comp, coh = score(m)
        results.append({
            "model": m,
            "comp": comp,
            "coh": coh
        })

    # tri
    results.sort(key=lambda x: (x["coh"], x["comp"]), reverse=True)

    st.subheader("📊 Models")

    for i, r in enumerate(results):

        with st.container():
            st.markdown(f"### Model {i}")
            st.write(f"Completeness: {r['comp']:.2f}")
            st.write(f"Coherence: {'✅' if r['coh'] else '❌'}")
            st.json(r["model"])

    idx = st.selectbox("Select model", range(len(results)))
    selected = results[idx]["model"]

    # expert edit
    if expert:
        edited = st.text_area(
            "Edit JSON",
            json.dumps(selected, indent=2),
            height=300
        )
        selected = json.loads(edited)

    tl = detect_time(text)

    final = build(selected, tl)

    st.subheader("🏆 Final Model")
    st.json(final)

    # export
    st.download_button(
        "Download JSON",
        json.dumps(final, indent=2),
        "geog_v4.json"
    )

    # reverse
    if st.button("Suggest methods"):

        prompt = f"""
Given this physics:

{json.dumps(selected)}

Return geophysical methods.
"""

        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"user","content":prompt}],
            temperature=0
        )

        st.write(r.choices[0].message.content)