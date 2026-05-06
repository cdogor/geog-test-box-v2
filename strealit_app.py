import streamlit as st
import os, json, re
from openai import OpenAI

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GEOG — Simple Interpreter",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0e1117; color: #e2e8f0; }

.geog-header { text-align: center; padding: 36px 24px 28px; margin-bottom: 28px; }
.geog-globe  { font-size: 3rem; line-height: 1; margin-bottom: 10px; }
.geog-header h1 {
  font-family: 'JetBrains Mono', monospace;
  font-size: 1.6rem; font-weight: 600;
  color: #f8fafc; margin: 0 0 6px; letter-spacing: -0.5px;
}
.geog-header p { font-size: 0.85rem; color: #64748b; margin: 0; }
.chip {
  display: inline-block;
  background: #1e2d3d; color: #60a5fa;
  border: 1px solid #2a4a6e; border-radius: 4px;
  padding: 2px 8px; font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem; margin-bottom: 10px;
}

.slabel {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.63rem; font-weight: 600;
  letter-spacing: 2.5px; text-transform: uppercase;
  color: #60a5fa; margin-bottom: 10px;
}

.prose-card {
  background: #131920; border: 1px solid #1e2d3d;
  border-left: 3px solid #60a5fa; border-radius: 10px;
  padding: 18px 22px; margin-bottom: 24px;
}
.prose-card p {
  font-size: 0.92rem; color: #cbd5e1;
  line-height: 1.75; margin: 0; font-style: italic;
}

.physics-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 10px; margin-bottom: 24px;
}
.physics-cell {
  background: #131920; border: 1px solid #1e2d3d;
  border-radius: 8px; padding: 14px 16px; position: relative;
}
.physics-cell.filled { border-color: #1e3a5f; }
.physics-cell.empty  { opacity: 0.45; }
.pcell-key {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.65rem; font-weight: 600;
  letter-spacing: 2px; text-transform: uppercase;
  color: #60a5fa; margin-bottom: 6px;
}
.pcell-val  { font-size: 0.95rem; font-weight: 500; color: #f1f5f9; }
.pcell-empty { font-size: 0.82rem; color: #334155; font-style: italic; }
.pcell-dot {
  position: absolute; top: 12px; right: 12px;
  width: 7px; height: 7px; border-radius: 50%;
}
.dot-on  { background: #22c55e; }
.dot-off { background: #1e2d3d; }

.score-band {
  background: #131920; border: 1px solid #1e2d3d;
  border-radius: 8px; padding: 14px 18px;
  display: flex; align-items: center; gap: 16px; margin-bottom: 24px;
}
.score-num {
  font-family: 'JetBrains Mono', monospace;
  font-size: 2rem; font-weight: 600; color: #60a5fa;
  line-height: 1; min-width: 56px;
}
.score-right { flex: 1; }
.score-bar-bg {
  height: 6px; background: #1e2d3d;
  border-radius: 999px; overflow: hidden; margin-bottom: 6px;
}
.score-bar-fill {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, #60a5fa, #a78bfa);
}
.score-label { font-size: 0.75rem; color: #475569; }

.div-line { border: none; border-top: 1px solid #1e2d3d; margin: 22px 0; }

.onto-grid {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 8px; margin-top: 8px;
}
.onto-cell {
  background: #131920; border: 1px solid #1e2d3d;
  border-radius: 6px; padding: 10px 12px;
}
.onto-cell-key {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.62rem; font-weight: 600;
  letter-spacing: 2px; text-transform: uppercase;
  color: #60a5fa; margin-bottom: 6px;
}
.onto-val {
  display: inline-block;
  background: #0e1117; border: 1px solid #1e2d3d;
  border-radius: 4px; padding: 2px 7px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.68rem; color: #94a3b8;
  margin: 2px 2px 0 0;
}

textarea {
  background: #131920 !important; color: #e2e8f0 !important;
  border: 1px solid #1e2d3d !important; border-radius: 8px !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.83rem !important; line-height: 1.6 !important;
}
.stButton > button {
  width: 100%;
  background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%);
  color: #fff; border: none; border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.82rem; font-weight: 600;
  padding: 10px 24px; letter-spacing: 0.5px; transition: all 0.2s;
}
.stButton > button:hover {
  background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
  box-shadow: 0 0 16px rgba(96,165,250,0.25);
}
.streamlit-expanderHeader {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 0.73rem !important; color: #475569 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CLIENT
# ─────────────────────────────────────────────
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Missing `GROQ_API_KEY` environment variable.")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

# ─────────────────────────────────────────────
#  CONTROLLED VOCABULARY
#  Le LLM doit choisir DANS ces listes.
#  Un post-traitement rejette toute valeur hors liste.
# ─────────────────────────────────────────────
VALID_VALUES = {
    "source":      ["electrical", "mechanical", "chemical", "electromagnetic", "thermal", "hydraulic"],
    "propagation": ["wave", "diffusive", "quasi-static", "advective", "poroelastic"],
    "medium":      ["porous", "solid", "fractured", "fluid", "layered"],
    "observation": ["potential", "displacement", "field", "temperature", "pressure", "amplitude"],
}

# ─────────────────────────────────────────────
#  SAFE JSON
# ─────────────────────────────────────────────
def safe_json(text: str) -> dict:
    if not text:
        return {}
    # strip markdown fences
    clean = re.sub(r"```(?:json)?", "", text).strip(" `\n")
    for candidate in [clean, text]:
        try:
            return json.loads(candidate)
        except:
            pass
        m = re.search(r"\{.*\}", candidate, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass
    return {}

# ─────────────────────────────────────────────
#  SINGLE LLM CALL  —  interp + mapping ensemble
#
#  Pourquoi ça marche mieux :
#  • Le LLM voit le texte original ET sa propre
#    interprétation dans le même contexte.
#  • Le vocabulaire contrôlé est explicite dans
#    le prompt → pas de paraphrase libre.
#  • Un post-traitement strict rejette toute
#    valeur hors-liste (hallucination impossible).
# ─────────────────────────────────────────────
def run_pipeline(text: str) -> dict:

    valid_str = json.dumps(VALID_VALUES, indent=2)

    prompt = f"""You are a geophysics expert. Given the user description below, do two things at once:

STEP 1 — Write a concise plain-language physical description (1-3 sentences max).
STEP 2 — Map that description to exactly one value per field using ONLY the allowed vocabulary.
          If a field cannot be determined with confidence, use an empty string "".

Allowed vocabulary (you MUST pick from these exact strings, nothing else):
{valid_str}

Return ONLY a valid JSON object, no commentary, no markdown, no extra keys:
{{
  "description": "<plain-language rewrite>",
  "source":      "<one value from allowed list or empty string>",
  "propagation": "<one value from allowed list or empty string>",
  "medium":      "<one value from allowed list or empty string>",
  "observation": "<one value from allowed list or empty string>"
}}

User description:
{text}"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    data = safe_json(r.choices[0].message.content)

    # Post-processing: hard validation against allowed vocabulary
    model = {}
    for field, allowed in VALID_VALUES.items():
        raw_val = str(data.get(field, "")).strip().lower()
        model[field] = raw_val if raw_val in allowed else ""

    return {
        "description": data.get("description", ""),
        "model": model,
    }

def completeness(model: dict) -> float:
    return sum(1 for v in model.values() if v) / len(model)

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="geog-header">
  <div class="geog-globe">🌍</div>
  <div class="chip">SIMPLE</div>
  <h1>GEOG — Simple Interpreter</h1>
  <p>LLM interpretation · Controlled-vocabulary physics mapping</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  VOCABULARY EXPANDER
# ─────────────────────────────────────────────
with st.expander("📖 Allowed vocabulary", expanded=False):
    cells = ""
    for field, vals in VALID_VALUES.items():
        tags = "".join(f'<span class="onto-val">{v}</span>' for v in vals)
        cells += f'<div class="onto-cell"><div class="onto-cell-key">{field}</div>{tags}</div>'
    st.markdown(f'<div class="onto-grid">{cells}</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────
st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown('<div class="slabel">Problem Description</div>', unsafe_allow_html=True)
text = st.text_area(
    label="",
    placeholder="e.g. — ERT survey on a conductive clay layer, current injected through electrodes, measuring voltage differences at surface…",
    height=130,
    label_visibility="collapsed",
)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
run = st.button("▶  RUN")

if run and not text.strip():
    st.warning("⚠ Please enter a problem description.")
    st.stop()

# ─────────────────────────────────────────────
#  PIPELINE
# ─────────────────────────────────────────────
if run and text.strip():

    with st.spinner("Interpreting & mapping…"):
        result = run_pipeline(text)

    desc     = result["description"]
    model    = result["model"]
    comp     = completeness(model)
    comp_pct = int(comp * 100)
    filled   = sum(1 for v in model.values() if v)

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    # ── LLM description ──────────────────────
    st.markdown('<div class="slabel">LLM Interpretation</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="prose-card">
  <p>{desc if desc else "No description returned."}</p>
</div>
""", unsafe_allow_html=True)

    # ── Physics grid ─────────────────────────
    st.markdown('<div class="slabel">Standardized Physics</div>', unsafe_allow_html=True)

    cells_html = ""
    for key in ["source", "propagation", "medium", "observation"]:
        val = model.get(key, "")
        if val:
            cells_html += f"""
<div class="physics-cell filled">
  <div class="pcell-dot dot-on"></div>
  <div class="pcell-key">{key}</div>
  <div class="pcell-val">{val}</div>
</div>"""
        else:
            cells_html += f"""
<div class="physics-cell empty">
  <div class="pcell-dot dot-off"></div>
  <div class="pcell-key">{key}</div>
  <div class="pcell-empty">not detected</div>
</div>"""

    st.markdown(f'<div class="physics-grid">{cells_html}</div>', unsafe_allow_html=True)

    # ── Score band ────────────────────────────
    st.markdown(f"""
<div class="score-band">
  <div class="score-num">{comp:.2f}</div>
  <div class="score-right">
    <div class="score-bar-bg">
      <div class="score-bar-fill" style="width:{comp_pct}%"></div>
    </div>
    <div class="score-label">{comp_pct}% · {filled}/{len(model)} fields mapped</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── JSON output ───────────────────────────
    final = {"description": desc, "model": model}

    with st.expander("📦 View JSON output", expanded=False):
        st.json(final)

    st.download_button(
        label="⬇  Download geog_simple.json",
        data=json.dumps(final, indent=2),
        file_name="geog_simple.json",
        mime="application/json",
    )
