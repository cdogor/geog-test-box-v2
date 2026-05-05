import streamlit as st
import os, json, re
from datetime import datetime
from openai import OpenAI

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GEOG V7.4 — Hybrid Physics Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #080c10; color: #dce4f0; }

/* ── Header ── */
.geog-header {
  background: #0c1118;
  border: 1px solid #1c2636;
  border-top: 3px solid #3b82f6;
  border-radius: 10px;
  padding: 26px 34px 22px;
  margin-bottom: 26px;
  position: relative; overflow: hidden;
}
.geog-header::after {
  content: '';
  position: absolute; top: 0; right: 0;
  width: 300px; height: 100%;
  background: linear-gradient(90deg, transparent, rgba(59,130,246,0.04));
}
.geog-header h1 {
  font-family: 'Space Mono', monospace;
  font-size: 1.7rem; font-weight: 700;
  color: #f1f5f9; margin: 0 0 5px; letter-spacing: -0.5px;
}
.geog-header p { font-size: 0.88rem; color: #5a7a9a; margin: 0; }
.version-chip {
  display: inline-block;
  background: #0f2040; color: #3b82f6;
  border: 1px solid #1d3a6a;
  border-radius: 5px; padding: 2px 9px;
  font-family: 'Space Mono', monospace;
  font-size: 0.68rem; margin-right: 8px;
}

/* ── Section label ── */
.slabel {
  font-family: 'Space Mono', monospace;
  font-size: 0.65rem; font-weight: 700;
  letter-spacing: 2.5px; text-transform: uppercase;
  color: #3b82f6; margin-bottom: 10px;
}

/* ── Card ── */
.card {
  background: #0c1118;
  border: 1px solid #1c2636;
  border-radius: 10px;
  padding: 20px 22px;
  height: 100%;
}
.card-title {
  font-family: 'Space Mono', monospace;
  font-size: 0.78rem; font-weight: 700;
  color: #3b82f6; letter-spacing: 1.5px;
  text-transform: uppercase; margin-bottom: 18px;
}

/* ── Score row ── */
.score-row {
  display: flex; gap: 12px; margin-bottom: 18px;
}
.score-box {
  flex: 1; background: #111820;
  border: 1px solid #1c2636; border-radius: 8px;
  padding: 10px 14px; text-align: center;
}
.score-box-val {
  font-family: 'Space Mono', monospace;
  font-size: 1.5rem; font-weight: 700;
  line-height: 1; margin-bottom: 4px;
}
.score-box-label { font-size: 0.72rem; color: #5a7a9a; }
.val-blue  { color: #3b82f6; }
.val-green { color: #22c55e; }
.val-red   { color: #ef4444; }

/* ── Auto-correction badge ── */
.autocorr-banner {
  background: #1c1200; border: 1px solid #5c3800;
  border-left: 3px solid #f59e0b;
  border-radius: 6px; padding: 8px 14px;
  font-size: 0.82rem; color: #f59e0b;
  margin-bottom: 16px;
}

/* ── Field rows ── */
.field-grid { display: flex; flex-direction: column; gap: 5px; }
.field-row-item {
  display: flex; gap: 10px; align-items: flex-start;
  padding: 6px 10px; background: #111820;
  border-radius: 6px; border-left: 2px solid #1c2636;
}
.field-row-item.corrected { border-left-color: #f59e0b; }
.fkey {
  font-family: 'Space Mono', monospace;
  font-size: 0.7rem; color: #3b82f6;
  min-width: 96px; flex-shrink: 0; padding-top: 1px;
}
.fval { font-size: 0.82rem; color: #dce4f0; line-height: 1.4; }

/* ── Method bars ── */
.method-bar-item { margin-bottom: 12px; }
.mbar-header {
  display: flex; justify-content: space-between;
  align-items: baseline; margin-bottom: 5px;
}
.mbar-name {
  font-family: 'Space Mono', monospace;
  font-size: 0.82rem; font-weight: 700; color: #dce4f0;
}
.mbar-score {
  font-family: 'Space Mono', monospace;
  font-size: 0.78rem; color: #5a7a9a;
}
.mbar-bg {
  height: 6px; background: #111820;
  border-radius: 999px; overflow: hidden; margin-bottom: 4px;
}
.mbar-fill { height: 100%; border-radius: 999px; }
.mbar-sensor { font-size: 0.72rem; color: #5a7a9a; }

/* Score fill colors */
.fill-high   { background: linear-gradient(90deg, #22c55e, #16a34a); }
.fill-medium { background: linear-gradient(90deg, #f59e0b, #d97706); }
.fill-low    { background: linear-gradient(90deg, #ef4444, #b91c1c); }

/* ── Interpretation ── */
.interp-principle {
  font-size: 0.9rem; font-weight: 500;
  color: #dce4f0; line-height: 1.6;
  margin-bottom: 14px; padding-bottom: 14px;
  border-bottom: 1px solid #1c2636;
}
.interp-explanation {
  font-size: 0.82rem; color: #7a9ab8;
  line-height: 1.65;
  padding: 12px; background: #111820;
  border-radius: 8px; border-left: 3px solid #3b82f6;
}

/* ── Badges ── */
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 5px;
  font-family: 'Space Mono', monospace; font-size: 0.7rem;
}
.badge-blue  { background: #0f2040; color: #3b82f6;  border: 1px solid #1d3a6a; }
.badge-green { background: #0a2010; color: #22c55e;  border: 1px solid #14532d; }
.badge-amber { background: #1c1200; color: #f59e0b;  border: 1px solid #5c3800; }
.badge-gray  { background: #111820; color: #5a7a9a;  border: 1px solid #1c2636; }

/* ── Divider ── */
.div-line { border: none; border-top: 1px solid #1c2636; margin: 22px 0; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: #080c10; border-right: 1px solid #1c2636;
}
.db-row {
  display: flex; flex-direction: column; gap: 3px;
  margin-bottom: 14px;
}
.db-method-name {
  font-family: 'Space Mono', monospace;
  font-size: 0.78rem; font-weight: 700; color: #3b82f6;
}
.db-item {
  font-size: 0.76rem; color: #5a7a9a;
  padding: 3px 8px; background: #0c1118;
  border-radius: 4px;
}

/* ── Streamlit overrides ── */
textarea {
  background: #0c1118 !important; color: #dce4f0 !important;
  border: 1px solid #1c2636 !important; border-radius: 8px !important;
  font-family: 'Space Mono', monospace !important; font-size: 0.8rem !important;
}
.stButton > button {
  background: #0c1118; color: #dce4f0;
  border: 1px solid #1c2636; border-radius: 7px;
  font-family: 'Space Mono', monospace; font-size: 0.78rem;
  padding: 8px 20px; transition: all 0.2s;
}
.stButton > button:hover {
  background: #1c2636; border-color: #3b82f6; color: #f1f5f9;
}
.streamlit-expanderHeader {
  font-family: 'Space Mono', monospace !important;
  font-size: 0.75rem !important; color: #5a7a9a !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PHYSICS RULES & METHOD DB
# ─────────────────────────────────────────────
PHYSICS_RULES = {
    "electrical current":   ["diffusive", "quasi-static"],
    "mechanical vibration": ["wave"],
    "em excitation":        ["wave", "diffusive"],
    "chemical gradient":    ["diffusive"],
}

METHOD_DB = [
    {"name": "ERT",           "source": "electrical current",   "propagation": "diffusive", "observable": "voltage",      "sensor": "electrode"},
    {"name": "Seismic",       "source": "mechanical vibration", "propagation": "wave",      "observable": "displacement", "sensor": "geophone"},
    {"name": "EM",            "source": "em excitation",        "propagation": "wave",      "observable": "field",        "sensor": "antenna"},
    {"name": "Self Potential", "source": "chemical gradient",   "propagation": "diffusive", "observable": "potential",    "sensor": "electrode"},
]

# ─────────────────────────────────────────────
#  CLIENT
# ─────────────────────────────────────────────
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Missing `GROQ_API_KEY` environment variable.")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def safe_json(text):
    try:
        return json.loads(text)
    except:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return json.loads(m.group(0))
            except:
                pass
    return {}

def normalize(m):
    return {k: (v.lower().strip() if isinstance(v, str) else v) for k, v in m.items()}

def validate(m):
    src  = m.get("source")
    prop = m.get("propagation")
    if src in PHYSICS_RULES:
        return prop in PHYSICS_RULES[src]
    return True

def correct(m):
    src = m.get("source")
    if src in PHYSICS_RULES:
        m["propagation"] = PHYSICS_RULES[src][0]
    return m

def score_model(m):
    comp = sum(1 for k in ["source", "propagation", "medium", "observation"] if m.get(k)) / 4
    coh  = 1 if validate(m) else 0
    return comp, coh

def score_methods(model):
    results = []
    for method in METHOD_DB:
        s = 0
        if model.get("source")      == method["source"]:      s += 1
        if model.get("propagation") == method["propagation"]: s += 1
        if model.get("observation") == method["observable"]:  s += 1
        results.append({"name": method["name"], "score": round(s / 3, 2), "sensor": method["sensor"]})
    return sorted(results, key=lambda x: x["score"], reverse=True)

def fill_class(score):
    if score >= 0.67: return "fill-high"
    if score >= 0.34: return "fill-medium"
    return "fill-low"

def score_color(score):
    if score >= 0.67: return "val-green"
    if score >= 0.34: return "val-blue"
    return "val-red"

# ─────────────────────────────────────────────
#  LLM CALLS
# ─────────────────────────────────────────────
def forward(text):
    prompt = f"""Extract simple physics model. Return ONLY valid JSON:
{{"model":{{"source":"","propagation":"","medium":"","observation":"","coupling":""}}}}

TEXT:
{text}"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return safe_json(r.choices[0].message.content).get("model", {})

def interpret(m, text):
    prompt = f"""You are a geophysics expert. Given model: {json.dumps(m)}

Return ONLY valid JSON:
{{"principle":"","explanation":""}}"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return safe_json(r.choices[0].message.content)

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="slabel">Method Database</div>', unsafe_allow_html=True)
    for meth in METHOD_DB:
        st.markdown(f"""
<div class="db-row">
  <div class="db-method-name">{meth['name']}</div>
  <div class="db-item">source · {meth['source']}</div>
  <div class="db-item">propagation · {meth['propagation']}</div>
  <div class="db-item">observable · {meth['observable']}</div>
  <div class="db-item">sensor · {meth['sensor']}</div>
</div>
""", unsafe_allow_html=True)

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown('<div class="slabel">Physics Rules</div>', unsafe_allow_html=True)
    for src, props in PHYSICS_RULES.items():
        st.markdown(
            f'<div class="db-item" style="margin-bottom:4px">'
            f'<span style="color:#3b82f6">{src}</span> → {", ".join(props)}</div>',
            unsafe_allow_html=True,
        )

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.75rem;color:#5a7a9a;line-height:1.6">'
        'GEOG V7.4 · Hybrid Physics Engine<br>'
        'Rule-based validation + LLM forward pass<br>'
        'Auto-correction on incoherent models'
        '</p>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="geog-header">
  <h1>
    <span class="version-chip">V7.4</span>
    GEOG — Hybrid Physics Engine
  </h1>
  <p>Rule-based validation · LLM forward mapping · Method scoring · Physical interpretation</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="slabel">Problem Description</div>', unsafe_allow_html=True)
text = st.text_area(
    label="",
    placeholder="e.g. — We observe spontaneous potential anomalies near a buried sulfide body, likely due to electrochemical gradients…",
    height=120,
    label_visibility="collapsed",
)

run = st.button("▶  RUN V7.4", type="primary")

if run and not text.strip():
    st.warning("⚠ Please enter a problem description.")
    st.stop()

# ─────────────────────────────────────────────
#  PIPELINE
# ─────────────────────────────────────────────
if run and text.strip():

    with st.spinner("Forward pass…"):
        m = normalize(forward(text))

    was_corrected = not validate(m)
    if was_corrected:
        m = correct(m)

    comp, coh = score_model(m)
    methods   = score_methods(m)

    with st.spinner("Interpretation…"):
        interp = interpret(m, text)

    # ── Status row ────────────────────────────
    badges = []
    if was_corrected:
        badges.append('<span class="badge badge-amber">⚡ Auto-correction applied</span>')
    badges.append(
        f'<span class="badge badge-{"green" if coh else "red"}">{"✓ Coherent" if coh else "✗ Incoherent"} model</span>'
    )
    top_method = methods[0] if methods else None
    if top_method and top_method["score"] > 0:
        badges.append(f'<span class="badge badge-blue">↑ Best match: {top_method["name"]}</span>')

    st.markdown("&nbsp;&nbsp;".join(badges), unsafe_allow_html=True)
    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    # ── Three columns ─────────────────────────
    col1, col2, col3 = st.columns(3, gap="medium")

    # ── COL 1 — Physics model ─────────────────
    with col1:
        comp_pct = int(comp * 100)
        coh_color = "val-green" if coh else "val-red"
        fields_html = ""
        for k, v in m.items():
            if v:
                corrected_cls = "corrected" if was_corrected and k == "propagation" else ""
                fields_html += f"""
<div class="field-row-item {corrected_cls}">
  <span class="fkey">{k}</span>
  <span class="fval">{v}</span>
</div>"""

        st.markdown(f"""
<div class="card">
  <div class="card-title">🧠 Physics Model</div>
  <div class="score-row">
    <div class="score-box">
      <div class="score-box-val val-blue">{comp:.2f}</div>
      <div class="score-box-label">Completeness</div>
    </div>
    <div class="score-box">
      <div class="score-box-val {coh_color}">{"1.0" if coh else "0.0"}</div>
      <div class="score-box-label">Coherence</div>
    </div>
  </div>
  {"<div class='autocorr-banner'>⚡ Propagation auto-corrected to match source rules</div>" if was_corrected else ""}
  <div class="field-grid">{fields_html}</div>
</div>
""", unsafe_allow_html=True)

    # ── COL 2 — Methods ranked ────────────────
    with col2:
        bars_html = ""
        for meth in methods:
            s     = meth["score"]
            s_pct = int(s * 100)
            fc    = fill_class(s)
            sc    = score_color(s)
            bars_html += f"""
<div class="method-bar-item">
  <div class="mbar-header">
    <div class="mbar-name">{meth['name']}</div>
    <div class="mbar-score {sc}">{s:.2f}</div>
  </div>
  <div class="mbar-bg">
    <div class="mbar-fill {fc}" style="width:{s_pct}%"></div>
  </div>
  <div class="mbar-sensor">sensor · {meth['sensor']}</div>
</div>"""

        st.markdown(f"""
<div class="card">
  <div class="card-title">🔁 Methods Ranked</div>
  {bars_html}
</div>
""", unsafe_allow_html=True)

    # ── COL 3 — Interpretation ────────────────
    with col3:
        principle   = interp.get("principle", "—")
        explanation = interp.get("explanation", "—")

        st.markdown(f"""
<div class="card">
  <div class="card-title">📘 Interpretation</div>
  <div class="interp-principle">{principle}</div>
  <div class="interp-explanation">{explanation}</div>
</div>
""", unsafe_allow_html=True)

    # ── Final output ──────────────────────────
    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    final = {
        "version":         "v7.4",
        "timestamp":       datetime.now().isoformat(),
        "model":           m,
        "auto_corrected":  was_corrected,
        "score":           {"completeness": round(comp, 2), "coherence": coh},
        "methods_ranked":  methods,
        "interpretation":  interp,
    }

    with st.expander("📦 View full JSON output", expanded=False):
        st.json(final)

    st.download_button(
        label="⬇  Download geog_v7_4.json",
        data=json.dumps(final, indent=2),
        file_name="geog_v7_4.json",
        mime="application/json",
    )
