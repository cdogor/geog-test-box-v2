import streamlit as st
import os, json, re
from openai import OpenAI

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GEOG — Free Interpreter",
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

/* ── Prose card ── */
.prose-card {
  background: #131920; border: 1px solid #1e2d3d;
  border-left: 3px solid #60a5fa; border-radius: 10px;
  padding: 18px 22px; margin-bottom: 24px;
}
.prose-card p {
  font-size: 0.92rem; color: #cbd5e1;
  line-height: 1.8; margin: 0; font-style: italic;
}

/* ── Physics fields — vertical list ── */
.field-list { display: flex; flex-direction: column; gap: 8px; margin-bottom: 24px; }
.field-item {
  background: #131920; border: 1px solid #1e2d3d;
  border-radius: 8px; padding: 12px 16px;
  display: flex; align-items: flex-start; gap: 14px;
}
.field-item.filled { border-left: 3px solid #3b82f6; }
.field-item.empty  { border-left: 3px solid #1e2d3d; opacity: 0.5; }
.field-icon {
  font-size: 1.1rem; line-height: 1; margin-top: 1px; flex-shrink: 0;
}
.field-body { flex: 1; }
.field-key {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.63rem; font-weight: 600;
  letter-spacing: 2px; text-transform: uppercase;
  color: #60a5fa; margin-bottom: 4px;
}
.field-val { font-size: 0.9rem; color: #f1f5f9; line-height: 1.4; }
.field-empty { font-size: 0.82rem; color: #334155; font-style: italic; }

/* ── Score band ── */
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

/* ── Confidence badge ── */
.conf-row { display: flex; align-items: center; gap: 8px; margin-bottom: 20px; }
.conf-label { font-size: 0.75rem; color: #475569; }
.conf-dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}
.conf-high   { background: #22c55e; }
.conf-medium { background: #f59e0b; }
.conf-low    { background: #ef4444; }
.conf-text   { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }
.conf-text.high   { color: #22c55e; }
.conf-text.medium { color: #f59e0b; }
.conf-text.low    { color: #ef4444; }

.div-line { border: none; border-top: 1px solid #1e2d3d; margin: 22px 0; }

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
#  FIELD METADATA  (icônes + descriptions)
# ─────────────────────────────────────────────
FIELDS = {
    "source":      {"icon": "⚡", "hint": "Energy or excitation type"},
    "propagation": {"icon": "〰️", "hint": "How the signal travels"},
    "medium":      {"icon": "🪨", "hint": "Material the signal travels through"},
    "observation": {"icon": "📡", "hint": "What is measured at the sensor"},
    "coupling":    {"icon": "🔗", "hint": "Physical coupling between phenomena"},
}

# ─────────────────────────────────────────────
#  SAFE JSON
# ─────────────────────────────────────────────
def safe_json(text: str) -> dict:
    if not text:
        return {}
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
#  LLM PIPELINE  —  full free interpretation
# ─────────────────────────────────────────────
def run_pipeline(text: str) -> dict:
    """
    Le LLM fait tout :
    1. Reformule en description physique claire
    2. Extrait source / propagation / medium / observation / coupling
       en langage libre (pas de vocabulaire contrôlé)
    3. Évalue sa propre confiance globale
    """

    prompt = f"""You are a geophysics expert. The user will describe any geophysical problem,
method, or observation — possibly in informal, incomplete, or non-standard language.

Your job:
1. Rewrite their description as a clear, concise physical explanation (2-4 sentences).
   Use standard geophysics vocabulary but stay accessible.
2. Extract the five physics components listed below.
   Write free-form short phrases (3-8 words). Leave as "" if genuinely unknown.
3. Estimate your overall confidence in the extraction: "high", "medium", or "low".

Components to extract:
- source      : the energy or excitation driving the measurement
- propagation : how the signal or field travels through the subsurface
- medium      : the material or geological context
- observation : what the sensor actually measures
- coupling    : any physical coupling between phenomena (leave "" if none)

Return ONLY valid JSON, no markdown, no extra text:
{{
  "description": "",
  "source":      "",
  "propagation": "",
  "medium":      "",
  "observation": "",
  "coupling":    "",
  "confidence":  "high" | "medium" | "low"
}}

User input:
{text}"""

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    data = safe_json(r.choices[0].message.content)

    # Light cleanup only — no vocabulary enforcement
    model = {}
    for field in FIELDS:
        raw = str(data.get(field, "")).strip()
        # Reject suspiciously long values (likely hallucinated prose)
        model[field] = raw if raw and len(raw) < 120 else ""

    return {
        "description": data.get("description", ""),
        "confidence":  data.get("confidence", "medium"),
        "model":       model,
    }

def completeness(model: dict) -> float:
    # coupling is optional — don't penalize if absent
    core = {k: v for k, v in model.items() if k != "coupling"}
    return sum(1 for v in core.values() if v) / len(core)

def conf_class(c: str) -> str:
    return c if c in ("high", "medium", "low") else "medium"

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="geog-header">
  <div class="geog-globe">🌍</div>
  <div class="chip">FREE INTERPRETER</div>
  <h1>GEOG — Free Interpreter</h1>
  <p>Describe anything · The LLM reformulates and extracts the physics</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="slabel">Your Description</div>', unsafe_allow_html=True)
text = st.text_area(
    label="",
    placeholder=(
        "Write anything — formal or informal, in any language, complete or vague.\n\n"
        "e.g. — « on plante des électrodes dans le sol et on mesure comment le courant se diffuse »\n"
        "or — « hammer seismic on hard limestone, looking at reflections »\n"
        "or — « SP anomaly near a sulfide ore body »"
    ),
    height=150,
    label_visibility="collapsed",
)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
run = st.button("▶  INTERPRET")

if run and not text.strip():
    st.warning("⚠ Please enter a description.")
    st.stop()

# ─────────────────────────────────────────────
#  PIPELINE
# ─────────────────────────────────────────────
if run and text.strip():

    with st.spinner("Interpreting…"):
        result = run_pipeline(text)

    desc       = result["description"]
    model      = result["model"]
    confidence = conf_class(result["confidence"])
    comp       = completeness(model)
    comp_pct   = int(comp * 100)
    filled     = sum(1 for k, v in model.items() if v and k != "coupling")

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    # ── LLM reformulation ─────────────────────
    st.markdown('<div class="slabel">Physical Interpretation</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="prose-card">
  <p>{desc if desc else "No description returned."}</p>
</div>
""", unsafe_allow_html=True)

    # ── Confidence ────────────────────────────
    conf_labels = {"high": "High confidence", "medium": "Medium confidence", "low": "Low confidence — description may be ambiguous"}
    st.markdown(f"""
<div class="conf-row">
  <div class="conf-dot conf-{confidence}"></div>
  <span class="conf-text {confidence}">{conf_labels.get(confidence, "")}</span>
</div>
""", unsafe_allow_html=True)

    # ── Physics fields ────────────────────────
    st.markdown('<div class="slabel">Extracted Physics</div>', unsafe_allow_html=True)

    items_html = ""
    for key, meta in FIELDS.items():
        val = model.get(key, "")
        if val:
            items_html += f"""
<div class="field-item filled">
  <div class="field-icon">{meta['icon']}</div>
  <div class="field-body">
    <div class="field-key">{key}</div>
    <div class="field-val">{val}</div>
  </div>
</div>"""
        else:
            # Hide coupling if empty (optional field)
            if key == "coupling":
                continue
            items_html += f"""
<div class="field-item empty">
  <div class="field-icon">{meta['icon']}</div>
  <div class="field-body">
    <div class="field-key">{key}</div>
    <div class="field-empty">not identified</div>
  </div>
</div>"""

    st.markdown(f'<div class="field-list">{items_html}</div>', unsafe_allow_html=True)

    # ── Score band ────────────────────────────
    st.markdown(f"""
<div class="score-band">
  <div class="score-num">{comp:.2f}</div>
  <div class="score-right">
    <div class="score-bar-bg">
      <div class="score-bar-fill" style="width:{comp_pct}%"></div>
    </div>
    <div class="score-label">Completeness · {filled}/4 core fields extracted</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── JSON output ───────────────────────────
    final = {
        "description": desc,
        "confidence":  confidence,
        "model":       model,
    }

    with st.expander("📦 View JSON output", expanded=False):
        st.json(final)

    st.download_button(
        label="⬇  Download geog_free.json",
        data=json.dumps(final, indent=2),
        file_name="geog_free.json",
        mime="application/json",
    )
