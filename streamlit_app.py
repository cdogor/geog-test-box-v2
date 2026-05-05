import streamlit as st
import os, json, re
from datetime import datetime
from openai import OpenAI

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GEOG V7.1 — Physics Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

.stApp { background: #0b0f17; color: #cdd6f4; }

/* ── Header ── */
.geog-header {
  background: linear-gradient(135deg, #11141e 0%, #1a1f2e 60%, #0d1117 100%);
  border: 1px solid #2a2d3e;
  border-radius: 14px;
  padding: 28px 36px 24px;
  margin-bottom: 28px;
  position: relative;
  overflow: hidden;
}
.geog-header::before {
  content: '';
  position: absolute; top: -60px; right: -60px;
  width: 260px; height: 260px;
  background: radial-gradient(circle, rgba(137,180,250,0.10) 0%, transparent 70%);
  border-radius: 50%;
}
.geog-header::after {
  content: '';
  position: absolute; bottom: -40px; left: 20px;
  width: 160px; height: 160px;
  background: radial-gradient(circle, rgba(166,227,161,0.07) 0%, transparent 70%);
  border-radius: 50%;
}
.geog-header h1 {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 1.9rem; font-weight: 600;
  color: #cdd6f4; margin: 0 0 6px; letter-spacing: -0.5px;
}
.geog-header p { font-size: 0.9rem; color: #6c7086; margin: 0; }

/* ── Section labels ── */
.section-label {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem; font-weight: 600;
  letter-spacing: 2.5px; text-transform: uppercase;
  color: #89b4fa; margin-bottom: 10px;
}

/* ── Cards ── */
.card {
  background: #11141e;
  border: 1px solid #2a2d3e;
  border-radius: 12px;
  padding: 20px 22px;
  height: 100%;
}
.card h3 {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.85rem; font-weight: 600;
  color: #89b4fa; margin: 0 0 16px;
  letter-spacing: 1px; text-transform: uppercase;
}

/* ── Score gauge ── */
.gauge-wrap { margin-bottom: 16px; }
.gauge-row { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
.gauge-bg {
  flex: 1; height: 8px;
  background: #1e2235; border-radius: 999px; overflow: hidden;
}
.gauge-fill {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, #89b4fa, #cba6f7);
  transition: width 0.8s ease;
}
.gauge-val {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.9rem; font-weight: 600; color: #cba6f7;
  min-width: 38px; text-align: right;
}
.gauge-label { font-size: 0.75rem; color: #6c7086; }

/* ── Field tags ── */
.field-row { display: flex; flex-direction: column; gap: 6px; }
.field-item {
  display: flex; align-items: baseline; gap: 8px;
  padding: 6px 10px;
  background: #1e2235; border-radius: 6px;
}
.field-key {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem; color: #89b4fa;
  min-width: 90px; flex-shrink: 0;
}
.field-val { font-size: 0.82rem; color: #cdd6f4; line-height: 1.4; }

/* ── Method cards ── */
.method-item {
  background: #1e2235;
  border: 1px solid #2a2d3e;
  border-radius: 8px;
  padding: 14px 16px; margin-bottom: 8px;
}
.method-name {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.88rem; font-weight: 600; color: #cdd6f4;
  margin-bottom: 6px;
}
.method-conf-bar-bg {
  height: 4px; background: #11141e;
  border-radius: 999px; overflow: hidden; margin-bottom: 8px;
}
.method-conf-bar-fill {
  height: 100%; border-radius: 999px;
  background: linear-gradient(90deg, #a6e3a1, #94e2d5);
}
.method-reason { font-size: 0.8rem; color: #6c7086; line-height: 1.5; }

/* ── Interpretation list ── */
.interp-principle {
  font-size: 0.9rem; color: #cdd6f4;
  line-height: 1.6; margin-bottom: 12px;
}
.law-tag {
  display: inline-block;
  background: #1e2235; border: 1px solid #313552;
  border-radius: 6px; padding: 3px 10px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem; color: #f38ba8;
  margin: 3px 3px 0 0;
}
.method-tag {
  display: inline-block;
  background: #1e2235; border: 1px solid #313552;
  border-radius: 6px; padding: 3px 10px;
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.72rem; color: #a6e3a1;
  margin: 3px 3px 0 0;
}
.interp-free {
  font-size: 0.82rem; color: #9399b2;
  line-height: 1.6; margin-top: 12px;
  padding: 12px; background: #1e2235;
  border-radius: 8px; border-left: 3px solid #89b4fa;
}

/* ── Badges ── */
.badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 12px; border-radius: 999px;
  font-family: 'IBM Plex Mono', monospace; font-size: 0.73rem;
}
.badge-blue  { background: #1a2a40; color: #89b4fa;  border: 1px solid #2a4a6e; }
.badge-green { background: #1a2e20; color: #a6e3a1;  border: 1px solid #2a5c38; }
.badge-gray  { background: #1e2235; color: #6c7086;  border: 1px solid #2a2d3e; }

/* ── Divider ── */
.div-line { border: none; border-top: 1px solid #1e2235; margin: 22px 0; }

/* ── Ontology grid ── */
.onto-group { margin-bottom: 16px; }
.onto-group-title {
  font-family: 'IBM Plex Mono', monospace;
  font-size: 0.68rem; font-weight: 600;
  letter-spacing: 2px; text-transform: uppercase;
  color: #6c7086; margin-bottom: 6px;
}
.onto-item {
  font-size: 0.78rem; color: #9399b2;
  padding: 4px 8px; background: #1e2235;
  border-radius: 5px; margin-bottom: 4px;
}

/* ── Streamlit overrides ── */
textarea {
  background: #11141e !important; color: #cdd6f4 !important;
  border: 1px solid #2a2d3e !important; border-radius: 8px !important;
  font-family: 'IBM Plex Mono', monospace !important; font-size: 0.83rem !important;
}
.stButton > button {
  background: #1e2235; color: #cdd6f4;
  border: 1px solid #2a2d3e; border-radius: 8px;
  font-family: 'IBM Plex Mono', monospace; font-size: 0.82rem;
  padding: 8px 20px; transition: all 0.2s;
}
.stButton > button:hover { background: #2a2d3e; border-color: #89b4fa; color: #cdd6f4; }
section[data-testid="stSidebar"] {
  background: #0b0f17; border-right: 1px solid #1e2235;
}
.streamlit-expanderHeader {
  font-family: 'IBM Plex Mono', monospace !important;
  font-size: 0.8rem !important; color: #6c7086 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  ONTOLOGY
# ─────────────────────────────────────────────
ONTOLOGY = {
    "source": [
        "electrical potential gradient", "mechanical stress/strain",
        "electromagnetic excitation", "chemical potential gradient",
        "thermal gradient", "fluid pressure gradient"
    ],
    "propagation": [
        "diffusive transport", "wave propagation",
        "quasi-static field", "advective transport", "poroelastic coupling"
    ],
    "medium": [
        "porous medium", "fractured rock",
        "electrolyte solution", "elastic solid"
    ],
    "observation": [
        "voltage difference", "electrode potential",
        "wave amplitude", "apparent resistivity"
    ]
}

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
    if not text:
        return {}
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
    return {}

def score(m):
    keys = ["source", "propagation", "medium", "observation"]
    return sum(1 for k in keys if m.get(k)) / len(keys)

def detect_time(text):
    return any(k in text.lower() for k in ["suivi", "monitoring", "evolution", "time", "lapse"])

# ─────────────────────────────────────────────
#  LLM CALLS
# ─────────────────────────────────────────────
def forward(text):
    prompt = f"""Return ONLY valid JSON:

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
{text}"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return safe_json(r.choices[0].message.content)

def reverse(model):
    prompt = f"""Given physics model:

{json.dumps(model)}

Return ONLY valid JSON:

{{
 "methods": [
  {{
   "name": "",
   "confidence": 0.0,
   "reason": ""
  }}
 ]
}}"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return safe_json(r.choices[0].message.content)

def interpret(model, text):
    prompt = f"""You are a geophysics expert.

Given:

Model:
{json.dumps(model)}

Text:
{text}

Return ONLY valid JSON:

{{
 "principle": "",
 "laws": [],
 "identified_methods": [],
 "free_explanation": ""
}}"""
    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    try:
        return json.loads(r.choices[0].message.content)
    except:
        return {
            "principle": "unparsed",
            "laws": [],
            "identified_methods": [],
            "free_explanation": r.choices[0].message.content,
        }

# ─────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)
    expert = st.toggle("Expert mode", value=False, help="Edit raw JSON model before export")

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Ontology Examples</div>', unsafe_allow_html=True)

    for cat, items in ONTOLOGY.items():
        st.markdown(f'<div class="onto-group-title">{cat}</div>', unsafe_allow_html=True)
        for item in items:
            st.markdown(f'<div class="onto-item">· {item}</div>', unsafe_allow_html=True)
        st.markdown("")

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.78rem;color:#6c7086;line-height:1.6">'
        'GEOG V7.1 · Integrated Geo Physics Engine<br>'
        'Forward mapping · Reverse mapping · Physical interpretation'
        '</p>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="geog-header">
  <h1>🌍 GEOG V7.1 — Integrated Geo Physics Engine</h1>
  <p>Forward mapping · Reverse mapping · Physical interpretation · LLM-powered geophysics reasoning</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Problem Description</div>', unsafe_allow_html=True)
text = st.text_area(
    label="",
    placeholder="e.g. — We want to image a conductive saline plume in a porous aquifer using surface measurements, with time-lapse monitoring over 6 months…",
    height=120,
    label_visibility="collapsed",
)

run = st.button("▶  RUN V7.1", type="primary")

if run and not text.strip():
    st.warning("⚠ Please enter a problem description.")
    st.stop()

# ─────────────────────────────────────────────
#  PIPELINE
# ─────────────────────────────────────────────
if run and text.strip():

    time_flag = detect_time(text)

    # ── Three parallel LLM calls ──────────────
    with st.spinner("Running forward pass…"):
        fwd_result = forward(text)
        model = fwd_result.get("model", {})

    col_spin1, col_spin2 = st.columns(2)
    with col_spin1:
        with st.spinner("Running reverse mapping…"):
            rev = reverse(model)
    with col_spin2:
        with st.spinner("Running interpretation…"):
            interp = interpret(model, text)

    # ── Status row ───────────────────────────
    badges = []
    if time_flag:
        badges.append('<span class="badge badge-blue">⏱ Time-lapse detected</span>')
    s = score(model)
    if s >= 0.75:
        badges.append('<span class="badge badge-green">✓ Complete model</span>')
    else:
        badges.append('<span class="badge badge-gray">⚠ Partial model</span>')

    st.markdown("&nbsp;&nbsp;".join(badges), unsafe_allow_html=True)
    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    # ── Three columns ────────────────────────
    col1, col2, col3 = st.columns(3, gap="medium")

    # ── COL 1 — Physics model ─────────────────
    with col1:
        sc = score(model)
        sc_pct = int(sc * 100)
        fields_html = "".join(
            f'<div class="field-item"><span class="field-key">{k}</span><span class="field-val">{v}</span></div>'
            for k, v in model.items() if v
        )
        st.markdown(f"""
<div class="card">
  <h3>🧠 Physics Model</h3>
  <div class="gauge-wrap">
    <div class="gauge-row">
      <div class="gauge-bg">
        <div class="gauge-fill" style="width:{sc_pct}%"></div>
      </div>
      <div class="gauge-val">{sc:.2f}</div>
    </div>
    <div class="gauge-label">Completeness score</div>
  </div>
  <div class="field-row">{fields_html}</div>
</div>
""", unsafe_allow_html=True)

    # ── COL 2 — Reverse methods ───────────────
    with col2:
        methods = rev.get("methods", [])
        methods_html = ""
        for meth in methods:
            conf = float(meth.get("confidence", 0)) if isinstance(meth.get("confidence"), (int, float)) else 0.5
            conf_pct = int(conf * 100)
            methods_html += f"""
<div class="method-item">
  <div class="method-name">{meth.get('name','—')}</div>
  <div class="method-conf-bar-bg">
    <div class="method-conf-bar-fill" style="width:{conf_pct}%"></div>
  </div>
  <div class="method-reason">{meth.get('reason','')}</div>
</div>"""

        st.markdown(f"""
<div class="card">
  <h3>🔁 Reverse Methods</h3>
  {methods_html if methods_html else '<div class="method-reason">No methods returned.</div>'}
</div>
""", unsafe_allow_html=True)

    # ── COL 3 — Interpretation ────────────────
    with col3:
        laws = interp.get("laws", [])
        id_methods = interp.get("identified_methods", [])
        laws_html    = "".join(f'<span class="law-tag">{l}</span>' for l in laws) or "—"
        methods_html2 = "".join(f'<span class="method-tag">{m}</span>' for m in id_methods) or "—"
        principle = interp.get("principle", "")
        free_exp  = interp.get("free_explanation", "")

        st.markdown(f"""
<div class="card">
  <h3>📘 Interpretation</h3>
  <div class="interp-principle">{principle}</div>
  <div class="section-label" style="margin-bottom:6px">Physical Laws</div>
  <div style="margin-bottom:12px">{laws_html}</div>
  <div class="section-label" style="margin-bottom:6px">Identified Methods</div>
  <div style="margin-bottom:12px">{methods_html2}</div>
  <div class="interp-free">{free_exp}</div>
</div>
""", unsafe_allow_html=True)

    # ── Expert edit ───────────────────────────
    if expert:
        st.markdown('<hr class="div-line">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Expert — JSON Model Edit</div>', unsafe_allow_html=True)
        edited_str = st.text_area(
            "Edit model JSON",
            value=json.dumps(model, indent=2),
            height=240,
            label_visibility="collapsed",
        )
        try:
            model = json.loads(edited_str)
            st.markdown('<span class="badge badge-green">✓ Valid JSON</span>', unsafe_allow_html=True)
        except json.JSONDecodeError as e:
            st.warning(f"Invalid JSON — keeping current model. ({e})")

    # ── Final output + export ─────────────────
    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Structured Output</div>', unsafe_allow_html=True)

    final = {
        "geog_version": "v7.1",
        "timestamp":    datetime.now().isoformat(),
        "time_lapse":   time_flag,
        "model":        model,
        "interpretation": interp,
        "reverse":      rev,
    }

    with st.expander("📦 View full JSON output", expanded=False):
        st.json(final)

    st.download_button(
        label="⬇  Download geog_v7_1.json",
        data=json.dumps(final, indent=2),
        file_name="geog_v7_1.json",
        mime="application/json",
    )
