import streamlit as st
import os, json, re
from openai import OpenAI

# ---------------- CONFIG ----------------
st.set_page_config(page_title="GEOG SIMPLE", layout="centered")
st.title("🌍 GEOG — Simple Interpreter")

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

# ---------------- STEP 1: LLM INTERPRET ----------------
def llm_interpret(text):

    prompt = f"""
Rewrite this as a SIMPLE physical description.

TEXT:
{text}

Return JSON:
{{
 "description": ""
}}
"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role":"user","content":prompt}],
        temperature=0
    )

    return safe_json(r.choices[0].message.content).get("description", "")

# ---------------- STEP 2: SIMPLE MAPPING ----------------
def map_physics(desc):

    d = desc.lower()

    source = ""
    propagation = ""
    medium = ""
    observation = ""

    # SOURCE
    if "electr" in d or "current" in d:
        source = "electrical"

    elif "wave" in d or "seismic" in d:
        source = "mechanical"

    elif "chem" in d:
        source = "chemical"

    # PROPAGATION
    if "wave" in d:
        propagation = "wave"
    elif "diffus" in d or "conduct" in d:
        propagation = "diffusive"

    # MEDIUM
    if "porous" in d or "soil" in d:
        medium = "porous"
    elif "rock" in d:
        medium = "solid"

    # OBSERVATION
    if "potential" in d or "voltage" in d:
        observation = "potential"
    elif "displacement" in d:
        observation = "displacement"

    return {
        "source": source,
        "propagation": propagation,
        "medium": medium,
        "observation": observation
    }

# ---------------- UI ----------------
text = st.text_area("🧠 Describe a geophysical method or problem")

if st.button("RUN"):

    desc = llm_interpret(text)

    model = map_physics(desc)

    st.subheader("🧠 LLM interpretation")
    st.write(desc)

    st.subheader("📊 Standardized physics")
    st.json(model)

    final = {
        "description": desc,
        "model": model
    }

    st.subheader("📦 Output")
    st.json(final)