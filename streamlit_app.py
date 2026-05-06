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
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
.stApp { background:#0e1117; color:#e2e8f0; }

.geog-header { text-align:center; padding:34px 24px 24px; margin-bottom:18px; }
.geog-globe  { font-size:2.6rem; line-height:1; margin-bottom:9px; }
.geog-header h1 {
  font-family:'JetBrains Mono',monospace; font-size:1.45rem; font-weight:600;
  color:#f8fafc; margin:0 0 5px; letter-spacing:-0.5px;
}
.geog-header p { font-size:0.82rem; color:#64748b; margin:0; }
.chip {
  display:inline-block; background:#1e2d3d; color:#60a5fa;
  border:1px solid #2a4a6e; border-radius:4px;
  padding:2px 8px; font-family:'JetBrains Mono',monospace;
  font-size:0.61rem; margin-bottom:9px;
}

.slabel {
  font-family:'JetBrains Mono',monospace; font-size:0.60rem; font-weight:600;
  letter-spacing:2.5px; text-transform:uppercase; color:#60a5fa; margin-bottom:8px;
}

.prose-card {
  background:#131920; border:1px solid #1e2d3d; border-left:3px solid #60a5fa;
  border-radius:10px; padding:14px 18px; margin-bottom:16px;
}
.prose-card p { font-size:0.89rem; color:#cbd5e1; line-height:1.8; margin:0; font-style:italic; }

/* badges */
.badge-row { display:flex; flex-wrap:wrap; gap:6px; margin-bottom:16px; }
.badge {
  display:inline-flex; align-items:center; gap:5px;
  padding:3px 9px; border-radius:5px;
  font-family:'JetBrains Mono',monospace; font-size:0.66rem;
}
.b-blue   { background:#0f2040; color:#60a5fa;  border:1px solid #2a4a6e; }
.b-green  { background:#0a2010; color:#22c55e;  border:1px solid #166534; }
.b-amber  { background:#1c1200; color:#f59e0b;  border:1px solid #5c3800; }
.b-red    { background:#200a0a; color:#ef4444;  border:1px solid #6b1a1a; }
.b-purple { background:#180f2a; color:#a78bfa;  border:1px solid #4c1d95; }
.b-teal   { background:#0a1f1f; color:#2dd4bf;  border:1px solid #0d4040; }
.b-gray   { background:#131920; color:#64748b;  border:1px solid #1e2d3d; }
.b-orange { background:#1a0f00; color:#fb923c;  border:1px solid #7c3010; }

/* ── Physics block card ── */
.pblock {
  background:#131920; border:1px solid #1e2d3d;
  border-radius:10px; padding:14px 16px; margin-bottom:12px;
}
.pblock-header {
  display:flex; align-items:center; justify-content:space-between; margin-bottom:12px;
}
.pblock-name {
  font-family:'JetBrains Mono',monospace; font-size:0.88rem; font-weight:600; color:#f1f5f9;
}
.pblock-idx {
  font-family:'JetBrains Mono',monospace; font-size:0.61rem; color:#334155;
  background:#0e1117; border:1px solid #1e2d3d; padding:2px 7px; border-radius:4px;
}

/* field rows inside block */
.frow {
  display:flex; align-items:flex-start; gap:10px;
  padding:7px 10px; border-radius:6px; margin-bottom:4px;
}
.frow.on  { background:#0d1825; border-left:2px solid #3b82f6; }
.frow.off { background:#0e1117; border-left:2px solid #1e2d3d; opacity:0.38; }
.ficon { font-size:0.95rem; line-height:1.3; flex-shrink:0; }
.fbody { flex:1; min-width:0; }
.fkey {
  font-family:'JetBrains Mono',monospace; font-size:0.57rem; font-weight:600;
  letter-spacing:2px; text-transform:uppercase; color:#60a5fa; margin-bottom:2px;
}
.fval   { font-size:0.85rem; color:#f1f5f9; line-height:1.4; }
.fempty { font-size:0.78rem; color:#243040; font-style:italic; }

/* unit / model tags inline */
.utag {
  font-family:'JetBrains Mono',monospace; font-size:0.69rem;
  color:#a78bfa; background:#180f2a; border:1px solid #4c1d95;
  border-radius:4px; padding:1px 6px; margin-left:6px; display:inline-block;
}
.mtag {
  font-family:'JetBrains Mono',monospace; font-size:0.69rem;
  color:#2dd4bf; background:#0a1f1f; border:1px solid #0d4040;
  border-radius:4px; padding:1px 6px; margin-left:6px; display:inline-block;
}

/* model parameters list */
.mparam-list { display:flex; flex-direction:column; gap:4px; margin-top:4px; }
.mparam-row {
  display:flex; align-items:center; gap:8px;
  padding:5px 10px; background:#0d1825;
  border-radius:5px; border-left:2px solid #2dd4bf;
}
.mparam-name { font-size:0.85rem; color:#f1f5f9; flex:1; }
.mparam-unit {
  font-family:'JetBrains Mono',monospace; font-size:0.68rem;
  color:#2dd4bf; background:#0a1f1f; border:1px solid #0d4040;
  border-radius:4px; padding:1px 6px;
}

/* 2-col meta */
.two-col { display:grid; grid-template-columns:1fr 1fr; gap:8px; margin-bottom:12px; }
.meta-cell {
  background:#131920; border:1px solid #1e2d3d; border-radius:8px; padding:10px 13px;
}
.meta-key {
  font-family:'JetBrains Mono',monospace; font-size:0.57rem; font-weight:600;
  letter-spacing:2px; text-transform:uppercase; color:#60a5fa; margin-bottom:3px;
}
.meta-val { font-size:0.85rem; color:#f1f5f9; }
.meta-sub { font-size:0.72rem; color:#64748b; margin-top:2px; }

/* method cards */
.mcard {
  background:#131920; border:1px solid #1e2d3d; border-radius:10px;
  padding:12px 15px; margin-bottom:9px;
}
.mcard-header {
  display:flex; align-items:center; justify-content:space-between; margin-bottom:8px;
}
.mcard-name {
  font-family:'JetBrains Mono',monospace; font-size:0.88rem; font-weight:600; color:#f1f5f9;
}
.mcard-idx {
  font-family:'JetBrains Mono',monospace; font-size:0.61rem; color:#334155;
  background:#0e1117; border:1px solid #1e2d3d; padding:2px 7px; border-radius:4px;
}
.conf-bar-bg { height:3px; background:#0e1117; border-radius:999px; overflow:hidden; margin-bottom:8px; }
.conf-bar-fill { height:100%; border-radius:999px; }
.cfill-high   { background:linear-gradient(90deg,#22c55e,#16a34a); }
.cfill-medium { background:linear-gradient(90deg,#f59e0b,#d97706); }
.cfill-low    { background:linear-gradient(90deg,#ef4444,#b91c1c); }
.mcard-grid { display:grid; grid-template-columns:1fr 1fr; gap:4px; margin-bottom:7px; }
.mcard-field { background:#0d1825; border-radius:5px; padding:5px 8px; }
.mcard-fkey {
  font-family:'JetBrains Mono',monospace; font-size:0.55rem; font-weight:600;
  letter-spacing:1.5px; text-transform:uppercase; color:#475569; margin-bottom:2px;
}
.mcard-fval { font-size:0.77rem; color:#cbd5e1; }
.mcard-ratio {
  margin-top:7px; padding-top:7px; border-top:1px solid #1e2d3d;
  font-size:0.78rem; color:#64748b; line-height:1.5;
}

/* score band */
.score-band {
  background:#131920; border:1px solid #1e2d3d; border-radius:8px;
  padding:11px 15px; display:flex; align-items:center; gap:12px; margin-bottom:16px;
}
.score-num {
  font-family:'JetBrains Mono',monospace; font-size:1.7rem; font-weight:600;
  color:#60a5fa; line-height:1; min-width:50px;
}
.score-bar-bg { height:5px; background:#1e2d3d; border-radius:999px; overflow:hidden; margin-bottom:4px; }
.score-bar-fill { height:100%; border-radius:999px; background:linear-gradient(90deg,#60a5fa,#a78bfa); }
.score-lbl { font-size:0.71rem; color:#475569; }

.div-line { border:none; border-top:1px solid #1e2d3d; margin:18px 0; }

textarea {
  background:#131920 !important; color:#e2e8f0 !important;
  border:1px solid #1e2d3d !important; border-radius:8px !important;
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.81rem !important; line-height:1.6 !important;
}
.stButton > button {
  width:100%;
  background:linear-gradient(135deg,#1d4ed8 0%,#2563eb 100%);
  color:#fff; border:none; border-radius:8px;
  font-family:'JetBrains Mono',monospace;
  font-size:0.80rem; font-weight:600; padding:10px 24px;
  letter-spacing:0.5px; transition:all 0.2s;
}
.stButton > button:hover {
  background:linear-gradient(135deg,#2563eb 0%,#3b82f6 100%);
  box-shadow:0 0 14px rgba(96,165,250,0.20);
}
.streamlit-expanderHeader {
  font-family:'JetBrains Mono',monospace !important;
  font-size:0.71rem !important; color:#475569 !important;
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
#  PROMPT
# ─────────────────────────────────────────────
PROMPT = """You are a geophysics expert. The user describes a geophysical problem in any
language, formal or informal, complete or vague.

Your task: extract a structured physics schema.

KEY RULES:
1. MULTI-PHYSICS: if the description involves more than one physical phenomenon
   (e.g. seismic + electrical, or P-wave + S-wave with different receivers),
   return ONE entry per physical component in the "physics" array.
   Each entry is fully self-contained.

2. SOURCE vs RECEIVER: in each physics block, distinguish:
   - source   : what emits or injects energy (hammer, electrode, coil…)
   - receiver : what records the response (geophone, electrode, magnetometer…)

3. OBSERVABLE vs MODEL PARAMETER:
   - observable      : what the receiver physically records (travel time, voltage…)
   - observable_unit : its unit (ms, V, nT…)
   - model_parameters: LIST of what is reconstructed by inversion. Each item has
                       "name" and "unit". There can be 1, 2, 3 or more.
     Example for crosshole: [{"name":"Vp","unit":"m/s"},{"name":"Vs","unit":"m/s"},{"name":"Qp","unit":""}]
     Example for ERT:       [{"name":"electrical resistivity","unit":"Ω·m"}]

4. DOMAIN: "frequential" | "temporal" | "mixed"
5. TEMPORALITY: "one-shot" | "time-lapse"
   time_interval: fill only if time-lapse (e.g. "monthly over 1 year")
6. METHODS: up to 2 identified acquisition methods with sensor, acquisition mode,
   confidence (high/medium/low), rationale.
7. CONFIDENCE (global): high | medium | low

Return ONLY valid JSON — no markdown, no commentary:

{
  "description": "<2-4 sentence physical rewrite>",
  "domain":          "frequential | temporal | mixed",
  "temporality":     "one-shot | time-lapse",
  "time_interval":   "",
  "confidence":      "high | medium | low",
  "physics": [
    {
      "label":         "<short name for this physical component, e.g. P-wave, ERT, SP>",
      "source":        "<energy source>",
      "receiver":      "<sensor that records>",
      "propagation":   "<how the field/wave travels>",
      "medium":        "<geological/material context>",
      "coupling":      "<physical coupling if any, else empty>",
      "observable":      "<what the receiver records>",
      "observable_unit": "<unit>",
      "model_parameters": [
        {"name": "<parameter name>", "unit": "<unit>"}
      ]
    }
  ],
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

User input:
{text}
"""

# ─────────────────────────────────────────────
#  PIPELINE
# ─────────────────────────────────────────────
def clean_str(v, maxlen=140):
    v = str(v).strip()
    return v if v and len(v) < maxlen else ""

def run_pipeline(text: str) -> dict:
    prompt = PROMPT.replace("{text}", text)

    r = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    data = safe_json(r.choices[0].message.content)

    # Normalize scalar fields
    if data.get("domain") not in ("frequential", "temporal", "mixed"):
        data["domain"] = ""
    if data.get("temporality") not in ("one-shot", "time-lapse"):
        data["temporality"] = ""
    if data.get("confidence") not in ("high", "medium", "low"):
        data["confidence"] = "medium"
    for k in ("description", "time_interval"):
        data[k] = clean_str(data.get(k, ""), 600)

    # Normalize physics blocks
    physics_out = []
    for pb in (data.get("physics") or []):
        if not isinstance(pb, dict):
            continue
        for k in ("label","source","receiver","propagation","medium","coupling","observable","observable_unit"):
            pb[k] = clean_str(pb.get(k, ""))
        # model_parameters — must be a list of {name, unit}
        raw_mp = pb.get("model_parameters") or []
        mp_out = []
        for mp in raw_mp:
            if isinstance(mp, dict) and mp.get("name"):
                mp_out.append({
                    "name": clean_str(mp.get("name","")),
                    "unit": clean_str(mp.get("unit",""), 30),
                })
        pb["model_parameters"] = mp_out
        if pb.get("label") or pb.get("source"):
            physics_out.append(pb)
    data["physics"] = physics_out

    # Normalize methods
    methods_out = []
    for m in (data.get("methods") or [])[:2]:
        if not isinstance(m, dict):
            continue
        for k in ("name","sensor","acquisition","rationale"):
            m[k] = clean_str(m.get(k,""))
        if m.get("confidence") not in ("high","medium","low"):
            m["confidence"] = "medium"
        if m.get("name"):
            methods_out.append(m)
    data["methods"] = methods_out

    return data

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def completeness(data: dict) -> float:
    """Score based on physics blocks richness."""
    blocks = data.get("physics", [])
    if not blocks:
        return 0.0
    core_keys = ["source","receiver","propagation","medium","observable","model_parameters"]
    scores = []
    for pb in blocks:
        filled = sum(1 for k in core_keys if pb.get(k))
        scores.append(filled / len(core_keys))
    return sum(scores) / len(scores)

def conf_fill(c):
    return {"high":"cfill-high","medium":"cfill-medium","low":"cfill-low"}.get(c,"cfill-medium")

def conf_pct(c):
    return {"high":100,"medium":60,"low":25}.get(c,60)

PHYSICS_COLORS = ["#3b82f6","#f59e0b","#22c55e","#a78bfa","#fb923c","#2dd4bf"]

def domain_icon(d):
    return {"frequential":"〰️","temporal":"⏱","mixed":"⚡"}.get(d,"·")

def time_icon(t):
    return {"one-shot":"📸","time-lapse":"🔁"}.get(t,"·")

# ─────────────────────────────────────────────
#  RENDER: single physics block card
# ─────────────────────────────────────────────
def render_physics_block(pb: dict, idx: int) -> str:
    color = PHYSICS_COLORS[idx % len(PHYSICS_COLORS)]

    def row(icon, key_label, val, extra=""):
        cls = "on" if val else "off"
        inner = f'<span class="fval">{val}{extra}</span>' if val else '<span class="fempty">—</span>'
        return f"""
<div class="frow {cls}">
  <div class="ficon">{icon}</div>
  <div class="fbody">
    <div class="fkey">{key_label}</div>
    {inner}
  </div>
</div>"""

    obs_unit_tag = f'<span class="utag">{pb["observable_unit"]}</span>' if pb.get("observable_unit") else ""

    # Model parameters list
    mp_list = pb.get("model_parameters", [])
    if mp_list:
       mp_rows = "".join( f'<div class="mparam-row">' f'<span class="mparam-name">{mp["name"]}</span>' + (f'<span class="mparam-unit">{mp["unit"]}</span>' if mp.get("unit") else "") + f'</div>'for mp in mp_list)
       mp_html = f'<div class="mparam-list">{mp_rows}</div>'
       mp_row = f"""
<div class="frow on">
  <div class="ficon">🧮</div>
  <div class="fbody">
    <div class="fkey">Model parameter(s)</div>
    {mp_html}
  </div>
</div>"""
    else:
        mp_row = row("🧮", "Model parameter(s)", "")

    rows_html = (
        row("⚡", "Source",      pb.get("source","")) +
        row("📡", "Receiver",    pb.get("receiver","")) +
        row("〰️", "Propagation", pb.get("propagation","")) +
        row("🪨", "Medium",      pb.get("medium","")) +
        row("🔗", "Coupling",    pb.get("coupling","")) +
        row("📊", "Observable",  pb.get("observable",""), obs_unit_tag) +
        mp_row
    )

    return f"""
<div class="pblock" style="border-left:3px solid {color}">
  <div class="pblock-header">
    <div class="pblock-name">{pb.get('label') or f'Physics {idx+1}'}</div>
    <div class="pblock-idx">COMPONENT {idx+1}</div>
  </div>
  {rows_html}
</div>"""

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="geog-header">
  <div class="geog-globe">🌍</div>
  <div class="chip">FREE INTERPRETER</div>
  <h1>GEOG — Free Interpreter</h1>
  <p>Multi-physics · Source / Receiver · Observable ≠ Model · Time-lapse</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="slabel">Your Description</div>', unsafe_allow_html=True)
text = st.text_area(
    label="",
    placeholder=(
        "Write anything — any language, informal, vague or precise.\n\n"
        "e.g. « crosshole entre deux forages, on mesure Vp et Vs »\n"
        "or — « joint ERT + seismic refraction survey on a landslide »\n"
        "or — « time-lapse SP monitoring near a dam, monthly »"
    ),
    height=140,
    label_visibility="collapsed",
)

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
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
    n_blocks = len(data.get("physics", []))
    n_methods = len(data.get("methods", []))
    conf     = data.get("confidence", "medium")

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    # ── Reformulation ─────────────────────────
    st.markdown('<div class="slabel">Physical Interpretation</div>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="prose-card">
  <p>{data.get('description') or 'No description returned.'}</p>
</div>""", unsafe_allow_html=True)

    # ── Status badges ─────────────────────────
    conf_cls = {"high":"b-green","medium":"b-amber","low":"b-red"}.get(conf,"b-amber")
    badges = [f'<span class="badge {conf_cls}">◉ {conf} confidence</span>']

    if n_blocks > 1:
        badges.append(f'<span class="badge b-orange">⚛ {n_blocks} physical components</span>')

    dom  = data.get("domain","")
    temp = data.get("temporality","")
    if dom:
        badges.append(f'<span class="badge b-purple">{domain_icon(dom)} {dom}</span>')
    if temp:
        c = "b-teal" if temp=="time-lapse" else "b-blue"
        badges.append(f'<span class="badge {c}">{time_icon(temp)} {temp}</span>')
        if temp=="time-lapse" and data.get("time_interval"):
            badges.append(f'<span class="badge b-gray">🗓 {data["time_interval"]}</span>')

    st.markdown(f'<div class="badge-row">{"".join(badges)}</div>', unsafe_allow_html=True)

    # ── Physics blocks ────────────────────────
    st.markdown('<div class="slabel">Physics Components</div>', unsafe_allow_html=True)
    for i, pb in enumerate(data.get("physics", [])):
        st.markdown(render_physics_block(pb, i), unsafe_allow_html=True)

    if not data.get("physics"):
        st.warning("No physics components extracted.")

    # ── Domain & Temporality ──────────────────
    ti = data.get("time_interval","")
    st.markdown(f"""
<div class="two-col">
  <div class="meta-cell">
    <div class="meta-key">Analysis domain</div>
    <div class="meta-val">{domain_icon(dom)+' '+dom if dom else '—'}</div>
  </div>
  <div class="meta-cell">
    <div class="meta-key">Temporality</div>
    <div class="meta-val">{time_icon(temp)+' '+temp if temp else '—'}</div>
    {'<div class="meta-sub">'+ti+'</div>' if ti else ''}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── Method cards ──────────────────────────
    methods = data.get("methods", [])
    if methods:
        st.markdown('<div class="slabel">Identified Methods</div>', unsafe_allow_html=True)
        for i, m in enumerate(methods):
            fc  = conf_fill(m.get("confidence","medium"))
            pct = conf_pct(m.get("confidence","medium"))
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
</div>""", unsafe_allow_html=True)

    # ── Score ─────────────────────────────────
    st.markdown(f"""
<div class="score-band">
  <div class="score-num">{comp:.2f}</div>
  <div style="flex:1">
    <div class="score-bar-bg">
      <div class="score-bar-fill" style="width:{comp_pct}%"></div>
    </div>
    <div class="score-lbl">Schema completeness · {n_blocks} physics block(s) · {n_methods} method(s)</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── JSON export ───────────────────────────
    with st.expander("📦 View full JSON output", expanded=False):
        st.json(data)

    st.download_button(
        label="⬇  Download geog_free.json",
        data=json.dumps(data, indent=2),
        file_name="geog_free.json",
        mime="application/json",
    )
