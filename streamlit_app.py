import streamlit as st
import os, json, re
from datetime import datetime
from openai import OpenAI

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="GEOG V6 — Physics Engine",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* Google Font */
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@300;400;600&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
  }

  /* Background */
  .stApp {
    background: #0d1117;
    color: #c9d1d9;
  }

  /* Header banner */
  .geog-header {
    background: linear-gradient(135deg, #161b22 0%, #1f2937 60%, #0f172a 100%);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
  }
  .geog-header::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(56,189,248,0.12) 0%, transparent 70%);
    border-radius: 50%;
  }
  .geog-header h1 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    color: #f0f6fc;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
  }
  .geog-header p {
    font-size: 0.95rem;
    color: #8b949e;
    margin: 0;
  }

  /* Section labels */
  .section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #38bdf8;
    margin-bottom: 10px;
  }

  /* Model card */
  .model-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
  }
  .model-card:hover {
    border-color: #58a6ff;
  }
  .model-card.selected {
    border-color: #38bdf8;
    box-shadow: 0 0 0 1px #38bdf8;
  }
  .model-card h3 {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.95rem;
    color: #f0f6fc;
    margin: 0 0 14px 0;
  }

  /* Score bar */
  .score-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
  }
  .score-bar-bg {
    flex: 1;
    background: #21262d;
    border-radius: 999px;
    height: 6px;
    overflow: hidden;
  }
  .score-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #38bdf8, #818cf8);
  }
  .score-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.85rem;
    color: #38bdf8;
    min-width: 36px;
    text-align: right;
  }

  /* Physics tags */
  .tag-row {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
  }
  .tag {
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 3px 10px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    color: #8b949e;
  }
  .tag .tag-key {
    color: #58a6ff;
    margin-right: 4px;
  }

  /* Method card */
  .method-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px 20px;
    margin-bottom: 10px;
  }
  .method-card .method-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.9rem;
    font-weight: 600;
    color: #f0f6fc;
    margin-bottom: 4px;
  }
  .method-card .method-conf {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 8px;
  }
  .conf-high   { background: #0d4a1a; color: #3fb950; border: 1px solid #238636; }
  .conf-medium { background: #3a2a00; color: #e3b341; border: 1px solid #9e6a03; }
  .conf-low    { background: #3d1616; color: #f85149; border: 1px solid #da3633; }
  .method-card .method-use {
    font-size: 0.82rem;
    color: #8b949e;
    line-height: 1.5;
  }

  /* Final output box */
  .output-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 20px 24px;
  }

  /* Status badge */
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-family: 'IBM Plex Mono', monospace;
  }
  .badge-blue { background: #0d2137; color: #38bdf8; border: 1px solid #1d4ed8; }
  .badge-green { background: #0d4a1a; color: #3fb950; border: 1px solid #238636; }
  .badge-gray { background: #21262d; color: #8b949e; border: 1px solid #30363d; }

  /* Divider */
  .div-line {
    border: none;
    border-top: 1px solid #21262d;
    margin: 24px 0;
  }

  /* Override Streamlit button */
  .stButton > button {
    background: #21262d;
    color: #c9d1d9;
    border: 1px solid #30363d;
    border-radius: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.82rem;
    padding: 8px 18px;
    transition: all 0.2s;
  }
  .stButton > button:hover {
    background: #30363d;
    border-color: #58a6ff;
    color: #f0f6fc;
  }

  /* Primary action button */
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1d4ed8, #0ea5e9);
    border: none;
    color: white;
    font-weight: 600;
  }

  /* Streamlit text area */
  textarea {
    background: #161b22 !important;
    color: #c9d1d9 !important;
    border: 1px solid #30363d !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
  }

  /* Expander */
  .streamlit-expanderHeader {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    color: #8b949e !important;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #0d1117;
    border-right: 1px solid #21262d;
  }

  /* JSON display override */
  .stJson {
    background: #161b22 !important;
    border: 1px solid #21262d !important;
    border-radius: 8px !important;
  }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  CLIENT INIT
# ─────────────────────────────────────────────
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    st.error("🔑 Missing `GROQ_API_KEY` environment variable.")
    st.stop()

client = OpenAI(api_key=API_KEY, base_url="https://api.groq.com/openai/v1")

# ─────────────────────────────────────────────
#  PHYSICS ONTOLOGY
# ─────────────────────────────────────────────
PHYSICS_CORE = {
    "source":      ["current", "mechanical", "electromagnetic"],
    "field":       ["electric", "elastic", "EM"],
    "propagation": ["diffusive", "wave", "quasi_static"],
    "medium":      ["conductive", "elastic", "dielectric"],
    "observable":  ["voltage", "displacement", "field"]
}

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def safe_json(text):
    if not text:
        return {"models": []}
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
    return {"models": []}

def score(m):
    keys = ["source", "field", "propagation", "medium"]
    return sum(1 for k in keys if m.get("physics", {}).get(k)) / len(keys)

def detect_time(text):
    return any(k in text.lower() for k in ["suivi", "monitoring", "evolution", "time"])

def conf_class(conf_str):
    c = str(conf_str).lower()
    if any(w in c for w in ["high", "élevé", "fort"]):
        return "conf-high"
    if any(w in c for w in ["medium", "moyen", "moderate"]):
        return "conf-medium"
    return "conf-low"

# ─────────────────────────────────────────────
#  LLM CALLS
# ─────────────────────────────────────────────
def forward(text):
    prompt = f"""Return ONLY valid JSON:

{{
 "models":[
  {{
   "name":"",
   "physics":{{"source":"","field":"","propagation":"","medium":""}},
   "observation":{{"sensor":"","measurand":""}}
  }}
 ]
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
 "methods":[
  {{
   "name":"",
   "confidence":"",
   "use_case":""
  }}
 ]
}}"""
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
    st.markdown('<div class="section-label">Configuration</div>', unsafe_allow_html=True)
    expert = st.toggle("Expert mode", value=False, help="Edit raw JSON model before reverse mapping")
    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    st.markdown('<div class="section-label">Physics Ontology</div>', unsafe_allow_html=True)
    for cat, vals in PHYSICS_CORE.items():
        with st.expander(cat.capitalize()):
            for v in vals:
                st.markdown(f'<span class="badge badge-gray">⬡ {v}</span>', unsafe_allow_html=True)
            st.markdown("")

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">About</div>', unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.78rem;color:#8b949e;line-height:1.6">'
        'GEOG V6 maps natural language geophysical descriptions '
        'to structured physics models and suggests acquisition methods.'
        '</p>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────
st.markdown("""
<div class="geog-header">
  <h1>🌍 GEOG V6 — Physics Engine</h1>
  <p>Forward & reverse mapping · Geophysical problem → structured physics model → acquisition methods</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  INPUT
# ─────────────────────────────────────────────
st.markdown('<div class="section-label">Problem Description</div>', unsafe_allow_html=True)
text = st.text_area(
    label="",
    placeholder="e.g. — We want to image a conductive layer at 50 m depth using surface electrodes in a time-lapse monitoring setup…",
    height=130,
    label_visibility="collapsed",
)

col_btn, col_info = st.columns([1, 5])
with col_btn:
    run = st.button("▶  RUN", type="primary", use_container_width=True)

if run and not text.strip():
    st.warning("⚠ Please enter a problem description first.")
    st.stop()

# ─────────────────────────────────────────────
#  MAIN PIPELINE
# ─────────────────────────────────────────────
if run and text.strip():

    tl = detect_time(text)

    # ── FORWARD ──────────────────────────────
    with st.spinner("Running forward pass…"):
        data = forward(text)

    models = data.get("models", [])

    if not models:
        st.error("No models returned. Try rephrasing your description.")
        st.stop()

    ranked = sorted(models, key=score, reverse=True)

    # ── TIME LAPSE BADGE ──────────────────────
    if tl:
        st.markdown(
            '<span class="badge badge-blue">⏱ Time-lapse mode detected</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

    st.markdown('<hr class="div-line">', unsafe_allow_html=True)

    # ── MODEL CARDS ──────────────────────────
    st.markdown('<div class="section-label">Physics Models</div>', unsafe_allow_html=True)

    selected_idx = st.radio(
        "Select model for reverse mapping",
        options=list(range(len(ranked))),
        format_func=lambda i: ranked[i].get("name", f"Model {i+1}"),
        horizontal=True,
        label_visibility="collapsed",
    )

    cols = st.columns(len(ranked))

    for i, m in enumerate(ranked):
        s = score(m)
        phys = m.get("physics", {})
        obs  = m.get("observation", {})
        is_sel = i == selected_idx

        with cols[i]:
            card_class = "model-card selected" if is_sel else "model-card"
            score_pct  = int(s * 100)

            tags_html = "".join(
                f'<span class="tag"><span class="tag-key">{k}</span>{v}</span>'
                for k, v in phys.items() if v
            )
            if obs.get("sensor"):
                tags_html += f'<span class="tag"><span class="tag-key">sensor</span>{obs["sensor"]}</span>'
            if obs.get("measurand"):
                tags_html += f'<span class="tag"><span class="tag-key">measurand</span>{obs["measurand"]}</span>'

            st.markdown(f"""
<div class="{card_class}">
  <h3>{'★ ' if is_sel else ''}{m.get('name', f'Model {i+1}')}</h3>
  <div class="score-wrap">
    <div class="score-bar-bg">
      <div class="score-bar-fill" style="width:{score_pct}%"></div>
    </div>
    <div class="score-label">{s:.2f}</div>
  </div>
  <div class="tag-row">{tags_html}</div>
</div>
""", unsafe_allow_html=True)

    selected = ranked[selected_idx]

    # ── EXPERT EDIT ──────────────────────────
    if expert:
        st.markdown('<hr class="div-line">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Expert — JSON Edit</div>', unsafe_allow_html=True)
        edited_str = st.text_area(
            "Edit selected model",
            value=json.dumps(selected, indent=2),
            height=260,
            label_visibility="collapsed",
        )
        try:
            selected = json.loads(edited_str)
            st.markdown(
                '<span class="badge badge-green">✓ Valid JSON</span>',
                unsafe_allow_html=True,
            )
        except json.JSONDecodeError as e:
            st.warning(f"Invalid JSON — keeping previous model. ({e})")

    # ── REVERSE ──────────────────────────────
    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Reverse Mapping — Physics → Methods</div>', unsafe_allow_html=True)

    if st.button("🔁 Generate acquisition methods"):

        with st.spinner("Running reverse pass…"):
            result = reverse(selected)

        methods = result.get("methods", [])

        if not methods:
            st.warning("No methods returned.")
        else:
            mcols = st.columns(min(len(methods), 3))
            for j, meth in enumerate(methods):
                cc = conf_class(meth.get("confidence", ""))
                with mcols[j % 3]:
                    st.markdown(f"""
<div class="method-card">
  <div class="method-name">{meth.get('name','—')}</div>
  <span class="method-conf {cc}">{meth.get('confidence','—')}</span>
  <div class="method-use">{meth.get('use_case','')}</div>
</div>
""", unsafe_allow_html=True)

    # ── FINAL OUTPUT ─────────────────────────
    st.markdown('<hr class="div-line">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Structured Output</div>', unsafe_allow_html=True)

    final = {
        "version":    "v6",
        "timestamp":  datetime.now().isoformat(),
        "time_lapse": tl,
        "model":      selected,
    }

    with st.expander("📦 View JSON output", expanded=False):
        st.json(final)

    st.download_button(
        label="⬇  Download geog_v6.json",
        data=json.dumps(final, indent=2),
        file_name="geog_v6.json",
        mime="application/json",
        use_container_width=False,
    )
