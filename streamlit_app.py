import streamlit as st
import os, json, re
from openai import OpenAI

st.set_page_config(
    page_title="GEOG — Free Interpreter",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0e1117; color: #e2e8f0; }

.geog-header { text-align:center; padding:36px 24px 26px; margin-bottom:20px; }
.geog-globe  { font-size:2.8rem; line-height:1; margin-bottom:10px; }
.geog-header h1 {
  font-family:'JetBrains Mono',monospace; font-size:1.5rem; font-weight:600;
  color:#f8fafc; margin:0 0 6px; letter-spacing:-0.5px;
}
.geog-header p { font-size:0.83rem; color:#64748b; margin:0; }
.chip {
  display:inline-block; background:#1e2d3d; color:#60a5fa;
  border:1px solid #2a4a6e; border-radius:4px;
  padding:2px 8px; font-family:'JetBrains Mono',monospace;
  font-size:0.62rem; margin-bottom:10px;
}

.slabel {
  font-family:'JetBrains Mono',monospace; font-size:0.61rem; font-weight:600;
  letter-spacing:2.5px; text-transform:uppercase; color:#60a5fa; margin-bottom:9px;
}

.prose-card {
  background:#131920; border:1px solid #1e2d3d; border-left:3px solid #60a5fa;
  border-radius:10px; padding:15px 20px; margin-bottom:18px;
}
.prose-card p {
  font-size:0.9rem; color:#cbd5e1; line-height:1.8; margin:0; font-style:italic;
}

/* badges */
.badge-row { display:flex; flex-wrap:wrap; gap:7px; margin-bottom:18px; }
.badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 10px; border-radius:5px;
  font-family:'JetBrains Mono',monospace; font-size:0.67rem;
}
.b-blue   { background:#0f2040; color:#60a5fa;  border:1px solid #2a4a6e; }
.b-green  { background:#0a2010; color:#22c55e;  border:1px solid #166534; }
.b-amber  { background:#1c1200; color:#f59e0b;  border:1px solid #5c3800; }
.b-red    { background:#200a0a; color:#ef4444;  border:1px solid #6b1a1a; }
.b-purple { background:#180f2a; color:#a78bfa;  border:1px solid #4c1d95; }
.b-teal   { background:#0a1f1f; color:#2dd4bf;  border:1px solid #0d4040; }
.b-gray   { background:#131920; color:#64748b;  border:1px solid #1e2d3d; }

/* section block */
.block {
  background:#131920; border:1px solid #1e2d3d;
  border-radius:10px; padding:15px 17px; margin-bottom:14px;
}
.block-title {
  font-family:'JetBrains Mono',monospace; font-size:0.6rem; font-weight:600;
  letter-spacing:2px; text-transform:uppercase; color:#334155; margin-bottom:11px;
}

/* field rows */
.frow {
  display:flex; align-items:flex-start; gap:11px;
  padding:8px 11px; border-radius:7px; margin-bottom:5px;
}
.frow.on  { background:#0d1825; border-left:2px solid #3b82f6; }
.frow.off { background:#0e1117; border-left:2px solid #1e2d3d; opacity:0.42; }
.ficon { font-size:1rem; line-height:1.25; flex-shrink:0; }
.fbody { flex:1; min-width:0; }
.fkey {
  font-family:'JetBrains Mono',monospace; font-size:0.59rem; font-weight:600;
  letter-spacing:2px; text-transform:uppercase; color:#60a5fa; margin-bottom:3px;
}
.fval  { font-size:0.87rem; color:#f1f5f9; line-height:1.4; }
.fempty { font-size:0.79rem; color:#243040; font-style:italic; }
.funit {
  font-family:'JetBrains Mono',monospace; font-size:0.72rem;
  color:#a78bfa; background:#180f2a; border:1px solid #4c1d95;
  border-radius:4px; padding:1px 7px; margin-left:8px;
  display:inline-block; vertical-align:middle;
}
.fmodel-tag {
  font-family:'JetBrains Mono',monospace; font-size:0.72rem;
  color:#2dd4bf; background:#0a1f1f; border:1px solid #0d4040;
  border-radius:4px; padding:1px 7px; margin-left:8px;
  display:inline-block; vertical-align:middle;
}

/* 2-col grid for meta */
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:14px; }
.meta-cell {
  background:#131920; border:1px solid #1e2d3d; border-radius:8px; padding:11px 14px;
}
.meta-key {
  font-family:'JetBrains Mono',monospace; font-size:0.59rem; font-weight:600;
  letter-spacing:2px; text-transform:uppercase; color:#60a5fa; margin-bottom:4px;
}
.meta-val  { font-size:0.87rem; color:#f1f5f9; }
.meta-sub  { font-size:0.73rem; color:#64748b; margin-top:3px; }

/* method cards */
.mcard {
  background:#131920; border:1px solid #1e2d3d; border-radius:10px;
  padding:13px 16px; margin-bottom:10px;
}
.mcard-header {
  display:flex; align-items:center; justify-content:space-between; margin-bottom:9px;
}
.mcard-name {
  font-family:'JetBrains Mono',monospace; font-size:0.9rem; font-weight:600; color:#f1f5f9;
}
.mcard-idx {
  font-family:'JetBrains Mono',monospace; font-size:0.63rem; color:#334155;
  background:#0e1117; border:1px solid #1e2d3d; padding:2px 7px; border-radius:4px;
}
.conf-bar-bg {
  height:4px; background:#0e1117; border-radius:999px; overflow:hidden; margin-bottom:9px;
}
.conf-bar-fill { height:100%; border-radius:999px; }
.cfill-high   { background:linear-gradient(90deg,#22c55e,#16a34a); }
.cfill-medium { background:linear-gradient(90deg,#f59e0b,#d97706); }
.cfill-low    { background:linear-gradient(90deg,#ef4444,#b91c1c); }
.mcard-grid { display:grid; grid-template-columns:1fr 1fr; gap:5px; margin-bottom:8px; }
.mcard-field { background:#0d1825; border-radius:5px; padding:6px 9px; }
.mcard-fkey {
  font-family:'JetBrains Mono',monospace; font-size:0.57rem; font-weight:600;
  letter-spacing:1.5px; text-transform:uppercase; color:#475569; margin-bottom:2px;
}
.mcard-fval { font-size:0.78rem; color:#cbd5e1; }
.mcard-ratio {
  margin-top:8px; padding-top:8px; border-top:1px solid #1e2d3d;
  font-size:0.79rem; color:#64748b; line-height:1.5;
}

/* score band */
.score-band {
  background:#131920; border:1px solid #1e2d3d; border-radius:8px;
  padding:12px 16px; display:flex; align-items:center; gap:13px; margin-bottom:18px;
}
.score-num {
  font-family:'JetBrains Mono',monospace; font-size:1.75rem; font-weight:600;
  color:#60a5fa; line-height:1; min-width:52px;
}
.score-bar-bg {
  height:5px; background:#1e2d3d; border-radius:999px; overflow:hidden; margin-bottom:5px;
}
.score-bar-fill {
  height:100%; border-radius:999px;
  background:linear-gradient(90deg,#60a5fa,#a78bfa);
}
.score-lbl { font-size:0.73rem; color:#475569; }

.div-line { border:none; border-top:1px solid #1e2d3d; margin:20px 0; }

textarea {
  background:#131920 !important; color:#e2e8f0 !important;
  border:1px solid #1e2d3d !important; border-radius:8px !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.82rem !important; line-height:1.6 !important;
}
.stButton > button {
  width:100%;
  background:linear-gradient(135deg,#1d4ed8 0%,#2563eb 100%);
  color:#fff; border:none; border-radius:8px;
  font-family:'JetBrains Mono',monospace;
  font-size:0.81rem; font-weight:600; padding:10px 24px;
  letter-spacing:0.5px; transition:all 0.2s;
}
.stButton > button:hover {
  background:linear-gradient(135deg,#2563eb 0%,#3b82f6 100%);
  box-shadow:0 0 16px rgba(96,165,250,0.22);
}
.streamlit-expanderHeader {
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.72rem !important; color:#475569 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CLIENT
# ─────────────────────────────────────────────
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Missing GROQ_API_KEY environment variable.")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

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
#  LLM PIPELINE
#
#  Schéma enrichi :
#  MESURE
#    observable       — ce que le capteur enregistre directement
#    observable_unit  — unité de l'observable (V, ms, nT…)
#  MODÈLE
#    model_parameter  — ce qu'on reconstruit par inversion/interprétation
#    model_unit       — unité du paramètre de modèle (Ω·m, m/s, kg/m³…)
#  PHYSIQUE
#    source / propagation / medium / coupling
#  DOMAINE & TEMPS
#    domain           — frequential | temporal | mixed
#    temporality      — one-shot | time-lapse
#    time_interval    — si time-lapse : fréquence/durée estimée
#  MÉTHODES (jusqu'à 2)
#    name / sensor / acquisition / confidence / rationale
# ─────────────────────────────────────────────
PROMPT_TEMPLATE = """You are a geophysics expert. The user will describe any geophysical
problem, method, or observation — in any language, formal or informal, complete or vague.

Extract the following schema. Write concise free-form phrases (3-10 words).
Leave any field as empty string "" if it cannot be determined.

IMPORTANT DISTINCTION:
- observable      : what the sensor physically records (e.g. "travel time", "voltage difference", "magnetic field intensity")
- observable_unit : SI or common unit of the observable (e.g. "ms", "V", "nT", "counts")
- model_parameter : what is reconstructed by inversion or interpretation (e.g. "P-wave velocity", "electrical resistivity", "density")
- model_unit      : unit of the model parameter (e.g. "m/s", "Ω·m", "kg/m³")
These are epistemically distinct — do not confuse them.

For domain: respond with exactly one of: "frequential", "temporal", "mixed"
For temporality: respond with exactly one of: "one-shot", "time-lapse"
For confidence: respond with exactly one of: "high", "medium", "low"
For method confidence: respond with exactly one of: "high", "medium", "low"

Return ONLY valid JSON — no markdown, no commentary:
{
  "description":     "<2-4 sentence plain-language physical rewrite>",
  "source":          "",
  "propagation":     "",
  "medium":          "",
  "coupling":        "",
  "observable":      "",
  "observable_unit": "",
  "model_parameter": "",
  "model_unit":      "",
  "domain":          "frequential | temporal | mixed",
  "temporality":     "one-shot | time-lapse",
  "time_interval":   "<e.g. 'monthly over 2 years' or ''>",
  "confidence":      "high | medium | low",
  "methods": [
    {
      "name":        "",
      "sensor":      "",
      "acquisition": "",
      "confidence":  "high | medium | low",
      "rationale":   ""
    }
  ]
}

Rules:
- methods array must contain 1 or 2 entries only (include a second only if clearly supported)
- time_interval is only filled when temporality is "time-lapse"
- coupling is only filled if there is an explicit physical coupling between phenomena

User input:
{text}
"""

def run_pipeline(text: str) -> dict:
    prompt = PROMPT_TEMPLATE.replace("{text}", text)

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    data = safe_json(r.choices[0].message.content)

    # Light cleanup — reject suspiciously long free fields
    scalar_fields = [
        "source", "propagation", "medium", "coupling",
        "observable", "observable_unit",
        "model_parameter", "model_unit",
        "domain", "temporality", "time_interval",
    ]
    for f in scalar_fields:
        v = str(data.get(f, "")).strip()
        data[f] = v if v and len(v) < 120 else ""

    # Normalize controlled fields
    if data.get("domain") not in ("frequential", "temporal", "mixed"):
        data["domain"] = ""
    if data.get("temporality") not in ("one-shot", "time-lapse"):
        data["temporality"] = ""
    if data.get("confidence") not in ("high", "medium", "low"):
        data["confidence"] = "medium"

    # Methods — keep at most 2, clean each
    methods = []
    for m in (data.get("methods") or [])[:2]:
        if not isinstance(m, dict):
            continue
        for k in ["name", "sensor", "acquisition", "rationale"]:
            m[k] = str(m.get(k, "")).strip()[:160]
        if m.get("confidence") not in ("high", "medium", "low"):
            m["confidence"] = "medium"
        if m.get("name"):
            methods.append(m)
    data["methods"] = methods

    return data

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def completeness(data: dict) -> float:
    core = ["source", "propagation", "medium", "observable", "model_parameter"]
    return sum(1 for k in core if data.get(k)) / len(core)

def conf_fill_class(c: str) -> str:
    return {"high": "cfill-high", "medium": "cfill-medium", "low": "cfill-low"}.get(c, "cfill-medium")

def conf_bar_pct(c: str) -> int:
    return {"high": 100, "medium": 60, "low": 25}.get(c, 60)

def domain_icon(d: str) -> str:
    return {"frequential": "〰️", "temporal": "⏱", "mixed": "⚡"}.get(d, "·")

def time_icon(t: str) -> str:
    return {"one-shot": "📸", "time-lapse": "🔁"}.get(t, "·")

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="geog-header">
  <div class="geog-globe">🌍</div>
  <div class="chip">FREE INTERPRETER</div>
  <h1>GEOG — Free Interpreter</h1>
  <p>Describe anything · The LLM extracts the full physics schema</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="slabel">Your Description</div>', unsafe_allow_html=True)
text = st.text_area(
    label="",
    placeholder=(
        "Write anything — formal or informal, any language, complete or vague.\n\n"
        "e.g. « on mesure les temps de premiers arrivées pour reconstruire la vitesse des ondes P »\n"
        "or — « ERT time-lapse on a leaking dam, monthly acquisition »\n"
        "or — « SP anomaly near sulfide body, single survey »"
    ),
    height=145,
    label_visibility="collapsed",
)

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
run = st.button("▶  INTERPRET")

if run and not text.strip():
    st.warning("⚠ Please enter a description.")
    st.stop()

# ─────────────────────────────────────────────
#  PIPELINE + DISPLAY
# ─────────────────────────────────────────────
if run and text.strip():

    with st.spinner("Interpreting…"):
        data = run_pipeline(text)

    comp     = completeness(data)
    comp_pct = int(comp * 100)
    filled   = sum(1 for k in ["source","propagation","medium","observable","model_parameter"] if data.get(k))
    conf     = data.get("confidence", "medium")

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    # ── Reformulation ─────────────────────────
    st.markdown('<div class="slabel">Physical Interpretation</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="prose-card">
  <p>{data.get('description') or 'No description returned.'}</p>
</div>""", unsafe_allow_html=True)

    # ── Status badges ─────────────────────────
    conf_badge_cls = {"high":"b-green","medium":"b-amber","low":"b-red"}.get(conf,"b-amber")
    conf_label     = {"high":"High confidence","medium":"Medium confidence","low":"Low confidence"}.get(conf,"")

    dom  = data.get("domain","")
    temp = data.get("temporality","")

    badges = [f'<span class="badge {conf_badge_cls}">◉ {conf_label}</span>']
    if dom:
        badges.append(f'<span class="badge b-purple">{domain_icon(dom)} {dom}</span>')
    if temp:
        color = "b-teal" if temp == "time-lapse" else "b-blue"
        badges.append(f'<span class="badge {color}">{time_icon(temp)} {temp}</span>')
        if temp == "time-lapse" and data.get("time_interval"):
            badges.append(f'<span class="badge b-gray">🗓 {data["time_interval"]}</span>')

    st.markdown(f'<div class="badge-row">{"".join(badges)}</div>', unsafe_allow_html=True)

    # ── Physics block ─────────────────────────
    st.markdown('<div class="slabel">Physics</div>', unsafe_allow_html=True)

    def frow(icon, key, label, val, extra_html=""):
        cls = "on" if val else "off"
        inner = f'<span class="fval">{val}{extra_html}</span>' if val else f'<span class="fempty">not identified</span>'
        return f"""
<div class="frow {cls}">
  <div class="ficon">{icon}</div>
  <div class="fbody">
    <div class="fkey">{label}</div>
    {inner}
  </div>
</div>"""

    physics_rows = (
        frow("⚡", "source",      "Source",      data.get("source","")) +
        frow("〰️", "propagation", "Propagation", data.get("propagation","")) +
        frow("🪨", "medium",      "Medium",       data.get("medium","")) +
        frow("🔗", "coupling",    "Coupling",     data.get("coupling",""))
    )
    st.markdown(f'<div class="block"><div class="block-title">Excitation & propagation</div><div class="field-list">{physics_rows}</div></div>', unsafe_allow_html=True)

    # ── Observable vs Model parameter ─────────
    st.markdown('<div class="slabel">Measurement vs Model</div>', unsafe_allow_html=True)

    obs_unit  = data.get("observable_unit","")
    mod_unit  = data.get("model_unit","")
    obs_extra = f' <span class="funit">{obs_unit}</span>' if obs_unit else ""
    mod_extra = f' <span class="fmodel-tag">{mod_unit}</span>' if mod_unit else ""

    meas_rows = (
        frow("📡", "observable",      "Observable (measured)",           data.get("observable",""),      obs_extra) +
        frow("🧮", "model_parameter", "Model parameter (reconstructed)", data.get("model_parameter",""), mod_extra)
    )
    st.markdown(f'<div class="block"><div class="block-title">Observable ≠ Model</div><div class="field-list">{meas_rows}</div></div>', unsafe_allow_html=True)

    # ── Domain & Temporality ──────────────────
    st.markdown('<div class="slabel">Domain & Temporality</div>', unsafe_allow_html=True)

    dom_val  = f'{domain_icon(dom)} {dom}' if dom else '—'
    temp_val = f'{time_icon(temp)} {temp}' if temp else '—'
    ti       = data.get("time_interval","")

    st.markdown(f"""
<div class="two-col">
  <div class="meta-cell">
    <div class="meta-key">Analysis domain</div>
    <div class="meta-val">{dom_val}</div>
  </div>
  <div class="meta-cell">
    <div class="meta-key">Temporality</div>
    <div class="meta-val">{temp_val}</div>
    {'<div class="meta-sub">' + ti + '</div>' if ti else ''}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Method cards ──────────────────────────
    methods = data.get("methods", [])
    if methods:
        st.markdown('<div class="slabel">Identified Methods</div>', unsafe_allow_html=True)
        for i, m in enumerate(methods):
            fc  = conf_fill_class(m.get("confidence","medium"))
            pct = conf_bar_pct(m.get("confidence","medium"))
            st.markdown(f"""
<div class="mcard">
  <div class="mcard-header">
    <div class="mcard-name">{m.get('name','—')}</div>
    <div class="mcard-idx">METHOD {i+1}</div>
  </div>
  <div class="conf-bar-bg">
    <div class="conf-bar-fill {fc}" style="width:{pct}%"></div>
  </div>
  <div class="mcard-grid">
    <div class="mcard-field">
      <div class="mcard-fkey">Sensor</div>
      <div class="mcard-fval">{m.get('sensor','—')}</div>
    </div>
    <div class="mcard-field">
      <div class="mcard-fkey">Acquisition</div>
      <div class="mcard-fval">{m.get('acquisition','—')}</div>
    </div>
  </div>
  <div class="mcard-ratio">{m.get('rationale','')}</div>
</div>
""", unsafe_allow_html=True)

    # ── Score ─────────────────────────────────
    st.markdown(f"""
<div class="score-band">
  <div class="score-num">{comp:.2f}</div>
  <div style="flex:1">
    <div class="score-bar-bg">
      <div class="score-bar-fill" style="width:{comp_pct}%"></div>
    </div>
    <div class="score-lbl">Schema completeness · {filled}/5 core fields · {len(methods)} method(s) identified</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── JSON export ───────────────────────────
    with st.expander("📦 View full JSON output", expanded=False):
        st.json(data)

    st.download_button(
        label="⬇  Download geog_free.json",
        data=json.dumps(data, indent=2),
        file_name="geog_free.json",
        mime="application/json",
    )
