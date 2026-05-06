import streamlit as st
import os, json, re
from openai import OpenAI

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GEOG — Free Interpreter",
    layout="centered",
)

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Missing GROQ_API_KEY")
    st.stop()

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# ─────────────────────────────────────────────
# SAFE JSON
# ─────────────────────────────────────────────
def safe_json(text: str) -> dict:
    if not text:
        return {}

    text = re.sub(r"```(?:json)?", "", text).strip()

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

# ─────────────────────────────────────────────
# CLEAN
# ─────────────────────────────────────────────
def clean(v, maxlen=140):
    v = str(v).strip()
    return v if v and len(v) < maxlen else ""

# ─────────────────────────────────────────────
# PROMPT
# ─────────────────────────────────────────────
PROMPT = """Return ONLY valid JSON.

User:
{text}
"""

# ─────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────
def run_pipeline(text: str) -> dict:

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": PROMPT.replace("{text}", text)}],
        temperature=0,
    )

    data = safe_json(r.choices[0].message.content)

    # Normalize
    data["description"] = clean(data.get("description", ""), 600)

    # Physics
    physics = []
    for pb in data.get("physics", []):
        if not isinstance(pb, dict):
            continue

        for k in ["label","source","receiver","propagation","medium","observable"]:
            pb[k] = clean(pb.get(k,""))

        mp = []
        for m in pb.get("model_parameters", []):
            if isinstance(m, dict) and m.get("name"):
                mp.append({
                    "name": clean(m.get("name","")),
                    "unit": clean(m.get("unit",""))
                })

        pb["model_parameters"] = mp

        if pb.get("label") or pb.get("source"):
            physics.append(pb)

    data["physics"] = physics

    return data

# ─────────────────────────────────────────────
# RENDER PHYSICS (FIXED BUG HERE)
# ─────────────────────────────────────────────
def render_physics(pb):

    mp_html = ""

    for mp in pb.get("model_parameters", []):
        unit_html = f'<span style="color:#888">{mp["unit"]}</span>' if mp.get("unit") else ""

        mp_html += (
            f"<div>"
            f"{mp['name']} {unit_html}"
            f"</div>"
        )

    return f"""
    <div style="border:1px solid #333;padding:10px;margin-bottom:10px">
        <b>{pb.get('label','Physics')}</b><br>
        Source: {pb.get('source','—')}<br>
        Receiver: {pb.get('receiver','—')}<br>
        Observable: {pb.get('observable','—')}<br>
        <div>{mp_html}</div>
    </div>
    """

# ─────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────
st.title("🌍 GEOG — Free Interpreter")

text = st.text_area("Describe your geophysical problem")

if st.button("INTERPRET"):

    if not text.strip():
        st.warning("Enter something")
        st.stop()

    with st.spinner("Processing..."):
        data = run_pipeline(text)

    st.subheader("Interpretation")
    st.write(data.get("description","—"))

    st.subheader("Physics")

    if not data.get("physics"):
        st.warning("No physics detected")

    for pb in data.get("physics", []):
        st.markdown(render_physics(pb), unsafe_allow_html=True)

    with st.expander("JSON"):
        st.json(data)