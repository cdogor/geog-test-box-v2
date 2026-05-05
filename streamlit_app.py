import streamlit as st
import os, json, re
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GEOG V7.6", layout="wide")
st.title("🌍 GEOG V7.6 — Multi-Physics Engine")

API_KEY = os.getenv("GROQ_API_KEY")

if not API_KEY:
    st.error("Missing GROQ_API_KEY")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ---------------- SAFE JSON ----------------
def safe_json(text):
    try:
        return json.loads(text)
    except:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
    return {}

# ---------------- LLM UNDERSTAND ----------------
def llm_understand(text):

    prompt = f"""
Rewrite in simple physical description.

TEXT:
{text}

Return JSON:
{{"description":""}}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    return safe_json(r.choices[0].message.content).get("description", "")

# ---------------- MULTI-PHYSICS MAPPING ----------------
def map_multi_physics(desc):

    d = desc.lower()

    model = {
        "sources": [],
        "sources_detail": desc,
        "propagations": [],
        "propagations_detail": "",
        "mediums": [],
        "mediums_detail": "",
        "observations": [],
        "observations_detail": "",
        "couplings": []
    }

    # -------- SOURCES --------
    if any(k in d for k in ["electr", "current", "voltage"]):
        model["sources"].append("electrical")

    if any(k in d for k in ["chem", "reaction", "redox"]):
        model["sources"].append("chemical")

    if any(k in d for k in ["vibration", "wave", "seismic"]):
        model["sources"].append("mechanical")

    if any(k in d for k in ["temperature", "heat"]):
        model["sources"].append("thermal")

    # -------- PROPAGATIONS --------
    if any(k in d for k in ["wave", "propagation"]):
        model["propagations"].append("wave")

    if any(k in d for k in ["diffusion", "conduct"]):
        model["propagations"].append("diffusive")

    if any(k in d for k in ["flow", "fluid"]):
        model["propagations"].append("advective")

    # -------- MEDIUM --------
    if any(k in d for k in ["porous", "soil"]):
        model["mediums"].append("porous")

    if any(k in d for k in ["rock", "solid"]):
        model["mediums"].append("solid")

    if any(k in d for k in ["water", "fluid"]):
        model["mediums"].append("fluid")

    # -------- OBSERVATION --------
    if any(k in d for k in ["potential", "voltage"]):
        model["observations"].append("potential")

    if any(k in d for k in ["displacement", "amplitude"]):
        model["observations"].append("displacement")

    if any(k in d for k in ["field"]):
        model["observations"].append("field")

    # -------- COUPLING DETECTION --------
    if "electrical" in model["sources"] and "chemical" in model["sources"]:
        model["couplings"].append("electrochemical")

    if "mechanical" in model["sources"] and "fluid" in model["mediums"]:
        model["couplings"].append("poroelastic")

    return model

# ---------------- METHOD SCORING ----------------
METHOD_DB = [
    {"name": "ERT", "sources": ["electrical"], "propagation": "diffusive"},
    {"name": "Seismic", "sources": ["mechanical"], "propagation": "wave"},
    {"name": "EM", "sources": ["electrical"], "propagation": "wave"},
    {"name": "Self Potential", "sources": ["chemical","electrical"], "propagation": "diffusive"}
]

def score_methods(model):

    results = []

    for m in METHOD_DB:

        score = 0

        overlap = set(model["sources"]).intersection(set(m["sources"]))
        score += len(overlap)

        if m["propagation"] in model["propagations"]:
            score += 1

        results.append({
            "name": m["name"],
            "score": score
        })

    return sorted(results, key=lambda x: x["score"], reverse=True)

# ---------------- INTERPRET ----------------
def interpret(model):

    prompt = f"""
Explain this multi-physics system:

{json.dumps(model)}

Return JSON:
{{"summary":"","explanation":""}}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    return safe_json(r.choices[0].message.content)

# ---------------- UI ----------------
text = st.text_area("🧠 Describe method or system")

if st.button("RUN V7.6"):

    desc = llm_understand(text)

    model = map_multi_physics(desc)

    methods = score_methods(model)

    interp = interpret(model)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🧠 Multi-Physics Model")
        st.json(model)

    with col2:
        st.subheader("🔁 Methods (ranked)")
        st.json(methods)

    with col3:
        st.subheader("📘 Interpretation")
        st.json(interp)

    final = {
        "version": "v7.6",
        "description": desc,
        "model": model,
        "methods": methods,
        "interpretation": interp
    }

    st.subheader("📦 Output")
    st.json(final)

    st.download_button(
        "Download JSON",
        json.dumps(final, indent=2),
        "geog_v7_6.json"
    )