# app1.py
# ─────────────────────────────────────────────
# Resume Builder Agentic System
# Streamlit UI — styled to match HTML mockup
# White cards, clean tabs, colored badges,
# tag pills, gap cards, project cards
# ─────────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from contextlib import contextmanager
from utils.pdf_extractor import extract_resume_text
from utils.jd_scraper import fetch_jd_from_url
from utils.resume_generator import generate_resume_docx
from graph.pipeline import run_pipeline

# ── Page Config ──
st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)


@contextmanager
def card(key: str | None = None):
    """
    A real card container. st.markdown('<div class="card">') / ... / st.markdown('</div>')
    does NOT actually nest — each st.markdown() call is its own isolated HTML fragment, so the
    opening div renders as an empty box and the content in between sits unstyled outside it.
    st.container(border=True) is a genuine Python-level nesting boundary, so it always wraps
    its contents correctly. CSS below (div[data-testid="stVerticalBlockBorderWrapper"]) makes
    it look like our .card style. Pass `key` to target one specific card for a style override.
    """
    with st.container(border=True, key=key):
        yield

# ── CSS — high-contrast app shell ──
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;0,9..144,700;1,9..144,500&family=Inter:wght@400;500;600;700;800&family=IBM+Plex+Mono:wght@500;600;700&display=swap');

:root {
    /* paper + ink */
    --paper: #edece3;
    --paper-raised: #ffffff;
    --ink: #191a20;
    --ink-soft: #5c5f68;
    --rule: #dedad0;
    --rule-strong: #c7c2b3;

    /* "pen" accent colors — each carries a job, not just decoration */
    --pen-blue: #1d3557;    /* brand / primary ink */
    --pen-blue-soft: rgba(29, 53, 87, 0.09);
    --pen-red: #a83a2c;     /* corrections, gaps, missing */
    --pen-red-soft: #fbecea;
    --pen-green: #2e6b4c;   /* matches, strengths, success */
    --pen-green-soft: #eaf4ee;
    --pen-amber: #93641c;   /* warnings, medium priority */
    --pen-amber-soft: #fbf1e2;
    --pen-violet: #57497f;  /* agent 4 / writer */
    --pen-violet-soft: #efecf6;

    --shadow-sm: 0 1px 2px rgba(23, 25, 32, 0.06);
    --shadow-md: 0 10px 24px rgba(23, 25, 32, 0.07);
}

html, body,
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stHeader"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: var(--ink) !important;
    background: var(--paper) !important;
}

#MainMenu, footer, header { visibility: hidden; }

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* Real card containers — st.container(border=True) via the card() helper.
   This is a genuine nesting boundary so it always wraps its content correctly,
   unlike the old string-split div pattern. */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--paper-raised) !important;
    border: 1px solid var(--rule) !important;
    border-radius: 10px !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 14px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
    padding: 22px 24px !important;
}
/* nested cards inside a column shouldn't double up on outer spacing */
div[data-testid="column"] div[data-testid="stVerticalBlockBorderWrapper"] {
    margin-bottom: 0 !important;
}
.st-key-ready_checklist div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #fafaf8 !important;
}
.st-key-resume_preview div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] {
    padding: 0 !important;
}

/* ── Header ── */
.app-header {
    margin: 20px auto 0;
    max-width: 1080px;
    padding: 16px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    background: var(--paper-raised);
    border: 1px solid var(--rule);
    border-radius: 12px;
    box-shadow: var(--shadow-sm);
}

.app-header > div { display: flex; align-items: center; gap: 14px; }

.brand-mark {
    width: 38px;
    height: 38px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    background: var(--pen-blue);
    color: #f2f1eb;
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-weight: 600;
    font-size: 17px;
}

.brand-copy h1 {
    font-family: 'Fraunces', serif;
    font-size: 21px;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin: 0;
    color: var(--ink);
}

.brand-copy span {
    display: block;
    margin-top: 2px;
    font-size: 12.5px;
    color: var(--ink-soft);
}

.header-stamp {
    padding: 7px 14px;
    border: 1.5px dashed var(--pen-blue);
    border-radius: 4px;
    color: var(--pen-blue);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    transform: rotate(-2deg);
    white-space: nowrap;
}

/* ── Hero ── */
.hero-shell {
    max-width: 1080px;
    margin: 14px auto 0;
    padding: 30px 32px;
    border-radius: 14px;
    border: 1px solid var(--rule);
    background: var(--paper-raised);
    box-shadow: var(--shadow-sm);
}

.hero-eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--pen-blue);
}
.hero-eyebrow::before {
    content: "";
    width: 16px;
    height: 1.5px;
    background: var(--pen-blue);
    display: inline-block;
}

.hero-shell h2 {
    margin: 12px 0 8px;
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: clamp(26px, 2.6vw, 38px);
    line-height: 1.12;
    letter-spacing: -0.015em;
    color: var(--ink);
    max-width: 22ch;
}

.hero-shell p {
    margin: 0 0 26px;
    color: var(--ink-soft);
    font-size: 15px;
    line-height: 1.7;
    max-width: 58ch;
}

/* pipeline rail — the four agents, in order, as a real sequence */
.pipeline-rail {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0;
    position: relative;
}
.pipeline-rail::before {
    content: "";
    position: absolute;
    top: 15px;
    left: 6%;
    right: 6%;
    height: 1.5px;
    background: var(--rule-strong);
    z-index: 0;
}
.pstage { position: relative; z-index: 1; padding-right: 10px; }
.pstage-dot {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: var(--paper-raised);
    border: 1.5px solid var(--rule-strong);
    display: grid;
    place-items: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 700;
    color: var(--ink-soft);
    margin-bottom: 10px;
}
.pstage.coral  .pstage-dot { border-color: var(--pen-red); color: var(--pen-red); }
.pstage.amber  .pstage-dot { border-color: var(--pen-amber); color: var(--pen-amber); }
.pstage.blue   .pstage-dot { border-color: var(--pen-blue); color: var(--pen-blue); }
.pstage.green  .pstage-dot { border-color: var(--pen-green); color: var(--pen-green); }
.pstage-label {
    font-size: 12.5px;
    font-weight: 700;
    color: var(--ink);
    margin-bottom: 2px;
}
.pstage-sub {
    font-size: 11.5px;
    color: var(--ink-soft);
    font-family: 'IBM Plex Mono', monospace;
}

/* ── Tab rail (workflow steps) ── */
.main-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 20px 40px;
}
/* the .main-content div above is only still used inside no_results(), where it's
   opened and closed in a single st.markdown() call so it nests correctly. Everywhere
   else, the tab panel itself now carries the same width constraint directly. */
div[data-testid="stTabsContent"] div[role="tabpanel"] > div[data-testid="stVerticalBlock"] {
    max-width: 900px;
    margin: 0 auto;
    padding: 24px 20px 40px;
}

.card {
    background: var(--paper-raised);
    border: 1px solid var(--rule);
    border-radius: 10px;
    padding: 22px 24px;
    margin-bottom: 14px;
    box-shadow: var(--shadow-sm);
}

.section-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: var(--ink-soft);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 12px;
}
.section-label::before {
    content: "";
    width: 3px;
    height: 12px;
    background: var(--pen-blue);
    display: inline-block;
}

.agent-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    color: #fff;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    font-weight: 700;
    padding: 6px 12px;
    border-radius: 5px;
    margin-bottom: 16px;
    letter-spacing: 0.02em;
}
.badge-coral  { background: var(--pen-red); }
.badge-amber  { background: var(--pen-amber); }
.badge-blue   { background: var(--pen-blue); }
.badge-green  { background: var(--pen-green); }
.badge-purple { background: var(--pen-violet); }

.tag-wrap { display: flex; flex-wrap: wrap; gap: 7px; margin-top: 8px; }
.tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    padding: 6px 10px;
    border-radius: 5px;
    border: 1px solid transparent;
}
.tag-blue  { background: var(--pen-blue-soft);  color: var(--pen-blue); }
.tag-green { background: var(--pen-green-soft); color: var(--pen-green); }
.tag-red   { background: var(--pen-red-soft);   color: var(--pen-red); }
.tag-gray  { background: var(--paper); color: var(--ink-soft); border-color: var(--rule); }

/* ── Score panel — graded, not gradient ── */
.score-big {
    text-align: center;
    padding: 20px 20px 24px;
    position: relative;
}
.score-circle-wrap {
    width: 130px;
    height: 130px;
    margin: 0 auto 10px;
    position: relative;
}
.score-num {
    font-family: 'Fraunces', serif;
    font-size: 40px;
    font-weight: 600;
    color: var(--ink);
    line-height: 1;
    letter-spacing: -0.02em;
    position: absolute;
    inset: 0;
    display: grid;
    place-items: center;
}
.score-num.amber { color: var(--pen-amber); }
.score-num.red   { color: var(--pen-red); }
.score-num.green { color: var(--pen-green); }
.score-label { font-size: 13px; color: var(--ink-soft); margin-top: 4px; }

.progress-item { margin-bottom: 15px; }
.progress-row  { display: flex; justify-content: space-between; font-size: 13.5px; margin-bottom: 6px; color: var(--ink); }
.progress-row span:last-child { font-family: 'IBM Plex Mono', monospace; font-weight: 600; }
.progress-track { height: 5px; background: var(--rule); border-radius: 3px; overflow: hidden; }
.progress-fill  { height: 100%; border-radius: 3px; background: var(--pen-blue); }
.progress-fill.green { background: var(--pen-green); }
.progress-fill.amber { background: var(--pen-amber); }

.verdict {
    background: var(--paper);
    border-left: 3px solid var(--pen-blue);
    border-radius: 0 8px 8px 0;
    padding: 15px 18px;
    font-family: 'Fraunces', serif;
    font-style: italic;
    font-size: 15px;
    color: var(--ink);
    line-height: 1.65;
}

.kv-row {
    display: flex;
    justify-content: space-between;
    gap: 16px;
    font-size: 14px;
    padding: 10px 0;
    border-bottom: 1px solid var(--rule);
}
.kv-row:last-child { border-bottom: none; }
.kv-key { color: var(--ink-soft); }
.kv-val { font-weight: 600; text-align: right; }

/* margin annotations — gap + project cards read like handwritten notes in the margin */
.gap-card {
    border-left: 3px solid var(--pen-red);
    padding: 14px 16px;
    background: var(--pen-red-soft);
    border-radius: 0 8px 8px 0;
    margin-bottom: 10px;
}
.gap-card-medium { border-left-color: var(--pen-amber) !important; background: var(--pen-amber-soft) !important; }
.gap-title { font-size: 14px; font-weight: 700; margin-bottom: 5px; color: var(--ink); }
.gap-fix   { font-size: 13px; color: var(--ink-soft); line-height: 1.6; }
.priority-high   { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:10.5px; font-weight:700; padding:3px 8px; border-radius:4px; background:#fff; color:var(--pen-red); margin-bottom:6px; text-transform:uppercase; letter-spacing:0.04em; }
.priority-medium { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:10.5px; font-weight:700; padding:3px 8px; border-radius:4px; background:#fff; color:var(--pen-amber); margin-bottom:6px; text-transform:uppercase; letter-spacing:0.04em; }
.priority-low    { display:inline-block; font-family:'IBM Plex Mono',monospace; font-size:10.5px; font-weight:700; padding:3px 8px; border-radius:4px; background:#fff; color:var(--ink-soft); margin-bottom:6px; text-transform:uppercase; letter-spacing:0.04em; }

.project-card {
    background: var(--pen-green-soft);
    border-left: 3px solid var(--pen-green);
    border-radius: 0 8px 8px 0;
    padding: 16px 18px;
    margin-bottom: 10px;
}
.project-title  { font-size: 14px; font-weight: 700; margin-bottom: 6px; color: var(--ink); }
.project-tech   { font-size: 12px; color: var(--pen-green); font-family: 'IBM Plex Mono', monospace; margin-bottom: 8px; }
.project-desc   { font-size: 13.5px; color: var(--ink); line-height: 1.6; margin-bottom: 8px; }
.project-metric { font-size: 11.5px; font-family: 'IBM Plex Mono', monospace; background: #fff; color: var(--pen-green); padding: 4px 9px; border-radius: 4px; display: inline-flex; font-weight: 700; }

/* resume preview — the actual paper document */
.resume-preview {
    background: #fff;
    border: 1px solid var(--rule);
    border-left: 3px solid var(--pen-blue);
    border-radius: 8px;
    padding: 32px 36px;
    font-family: 'Fraunces', serif;
    line-height: 1.65;
    font-size: 14px;
    color: #232430;
}
.resume-name    { font-size: 22px; font-weight: 600; text-align: center; margin-bottom: 4px; color: var(--ink); }
.resume-contact { text-align: center; font-family: 'IBM Plex Mono', monospace; font-size: 11.5px; color: var(--ink-soft); margin-bottom: 22px; }
.resume-section {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px; font-weight: 700; letter-spacing: 0.12em;
    text-transform: uppercase; color: var(--pen-blue);
    border-bottom: 1px solid var(--rule-strong);
    margin: 18px 0 8px; padding-bottom: 4px;
}

.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.success-box {
    background: var(--pen-green-soft);
    border-left: 3px solid var(--pen-green);
    border-radius: 0 8px 8px 0; padding: 12px 14px;
    font-size: 13.5px; color: var(--ink); margin-bottom: 14px;
}
.info-box {
    background: var(--paper);
    border-left: 3px solid var(--pen-blue);
    border-radius: 0 8px 8px 0; padding: 12px 14px;
    font-size: 13.5px; color: var(--ink); margin-bottom: 14px;
}

.upload-zone {
    border: 1.5px dashed var(--rule-strong);
    border-radius: 10px;
    padding: 36px 24px;
    text-align: center;
    background: var(--paper);
    cursor: pointer;
}
.upload-icon {
    width: 46px;
    height: 46px;
    margin: 0 auto 10px;
    border-radius: 8px;
    display: grid;
    place-items: center;
    background: #fff;
    border: 1px solid var(--rule);
    font-size: 22px;
}

/* ── Streamlit widget overrides ── */
div[data-testid="stTabs"] {
    background: transparent;
    border-bottom: 1px solid var(--rule-strong);
    border-radius: 0;
    padding: 0;
    max-width: 900px;
    margin: 22px auto 0;
}
div[data-testid="stTabs"] button {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 12.5px !important;
    font-weight: 600 !important;
    color: var(--ink-soft) !important;
    padding: 12px 16px !important;
    border-radius: 0 !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: var(--pen-blue) !important;
    background: transparent !important;
    border-bottom: 2px solid var(--pen-blue) !important;
}
div[data-testid="stFileUploader"] {
    background: var(--paper) !important;
    border: 1.5px dashed var(--rule-strong) !important;
    border-radius: 10px !important;
}
.stButton button {
    background: var(--pen-blue) !important;
    color: #f2f1eb !important;
    border: none !important;
    border-radius: 7px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: none !important;
}
.stButton button:hover { background: #142845 !important; }
.stTextInput input, .stTextArea textarea {
    border: 1.5px solid var(--rule-strong) !important;
    border-radius: 8px !important;
    font-size: 15px !important;
    background: #fff !important;
    color: var(--ink) !important;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder {
    color: #8b8b85 !important;
    opacity: 1 !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--pen-blue) !important;
    box-shadow: 0 0 0 3px var(--pen-blue-soft) !important;
}
div[data-testid="stRadio"] label,
div[data-testid="stCheckbox"] label,
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stFileUploader"] label,
div[data-testid="stSelectbox"] label,
div[data-testid="stNumberInput"] label {
    color: var(--ink) !important;
    opacity: 1 !important;
    font-size: 14px !important;
    font-weight: 600 !important;
}
/* Streamlit tints the *selected* radio option's own label text with its default
   theme accent (a low-opacity red), which reads as barely-visible pink on a light
   background. Force every descendant of these controls back to solid ink, and give
   the radio/checkbox dot itself one calm, consistent accent instead of the red. */
div[data-testid="stRadio"] *,
div[data-testid="stCheckbox"] * {
    color: var(--ink) !important;
    font-size: 14.5px !important;
}
div[data-testid="stRadio"] input,
div[data-testid="stCheckbox"] input {
    accent-color: var(--pen-blue) !important;
}
div[data-testid="stRadio"] svg,
div[data-testid="stCheckbox"] svg {
    fill: var(--pen-blue) !important;
}
div[data-testid="stCheckbox"] [aria-checked="true"] {
    background: var(--pen-blue) !important;
    border-color: var(--pen-blue) !important;
}
div[data-testid="stRadio"] [role="radiogroup"] > label {
    gap: 6px;
}
div[data-testid="stExpander"] {
    border: 1px solid var(--rule) !important;
    border-radius: 8px !important;
    background: #fff !important;
}
hr { border: none; border-top: 1px solid var(--rule); margin: 18px 0; }

@media (max-width: 900px) {
    .app-header { flex-wrap: wrap; }
    .pipeline-rail { grid-template-columns: 1fr 1fr; row-gap: 20px; }
    .pipeline-rail::before { display: none; }
    .hero-shell h2 { font-size: 30px; max-width: none; }
}
</style>
""", unsafe_allow_html=True)

# ── App Header ──
st.markdown("""
<div class="app-header">
    <div>
        <div class="brand-mark">AR</div>
        <div class="brand-copy">
            <h1>AI Resume Builder</h1>
            <span>Four agents. One tailored draft.</span>
        </div>
    </div>
    <div class="header-stamp">Docx Export Ready</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-shell">
    <div class="hero-eyebrow">Agentic resume tailoring</div>
    <h2>Turn a raw resume into a role-matched draft in one pass.</h2>
    <p>Upload a resume, paste a job description, and four agents parse the role, score the fit, surface the gaps, and write a resume tailored to it &mdash; ready to export as a docx.</p>
    <div class="pipeline-rail">
        <div class="pstage coral">
            <div class="pstage-dot">01</div>
            <div class="pstage-label">Parse the role</div>
            <div class="pstage-sub">jd_parser.py</div>
        </div>
        <div class="pstage amber">
            <div class="pstage-dot">02</div>
            <div class="pstage-label">Score the fit</div>
            <div class="pstage-sub">resume_evaluator.py</div>
        </div>
        <div class="pstage blue">
            <div class="pstage-dot">03</div>
            <div class="pstage-label">Surface the gaps</div>
            <div class="pstage-sub">gap_analyst.py</div>
        </div>
        <div class="pstage green">
            <div class="pstage-dot">04</div>
            <div class="pstage-label">Write the draft</div>
            <div class="pstage-sub">resume_writer.py</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Session State ──
if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

# ── Tabs ──
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📥 Input",
    "🔍 JD Analysis",
    "⭐ Score Card",
    "💡 Suggestions",
    "✅ Final Resume"
])


# ════════════════════════════════════════
# TAB 1 — INPUT
# ════════════════════════════════════════
with tab1:

    # Step 1 — Upload
    with card():
        st.markdown('<div class="section-label">Step 1 — Upload your resume</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload Resume (PDF or DOCX)",
            type=["pdf", "docx"],
            label_visibility="collapsed"
        )
        if uploaded_file:
            try:
                st.session_state.resume_text = extract_resume_text(uploaded_file)
                st.markdown(f"""
                <div class="success-box">
                    ✅ <strong>{uploaded_file.name}</strong> loaded —
                    {len(st.session_state.resume_text):,} characters extracted
                </div>
                """, unsafe_allow_html=True)
                with st.expander("👀 Preview extracted text"):
                    st.text(st.session_state.resume_text[:1500] + "...")
            except Exception as e:
                st.error(f"❌ Could not read file: {e}")
        else:
            st.markdown("""
            <div class="upload-zone">
                <div class="upload-icon">📎</div>
                <p style="font-size:14px;color:#666">Drag and drop your resume here</p>
                <small style="color:#aaa">Supports PDF and DOCX</small>
            </div>
            """, unsafe_allow_html=True)

    # Step 2 — Target Role
    with card():
        st.markdown('<div class="section-label">Step 2 — Target role</div>', unsafe_allow_html=True)
        target_role = st.text_input(
            "Target Role",
            placeholder="e.g. Senior Data Scientist, ML Engineer, Backend Developer",
            label_visibility="collapsed"
        )

    # Step 3 — Job Description
    with card():
        st.markdown('<div class="section-label">Step 3 — Job description</div>', unsafe_allow_html=True)
        jd_mode = st.radio(
            "JD Input Mode",
            ["🔗 Paste a Job URL", "📋 Paste JD Text Directly"],
            horizontal=True,
            label_visibility="collapsed"
        )
        if jd_mode == "🔗 Paste a Job URL":
            job_url = st.text_input(
                "Job URL",
                placeholder="https://linkedin.com/jobs/view/...",
                label_visibility="collapsed"
            )
            if job_url and st.button("🌐 Fetch JD from URL"):
                with st.spinner("Fetching job description..."):
                    try:
                        st.session_state.jd_text = fetch_jd_from_url(job_url)
                        st.markdown(f"""
                        <div class="success-box">
                            ✅ JD fetched — {len(st.session_state.jd_text):,} characters received
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ {e}")
        else:
            jd_paste = st.text_area(
                "Paste JD",
                height=180,
                placeholder="Copy and paste the complete job description here...",
                label_visibility="collapsed"
            )
            if jd_paste:
                st.session_state.jd_text = jd_paste
                st.markdown(f"""
                <div class="success-box">
                    ✅ JD received — {len(jd_paste):,} characters
                </div>
                """, unsafe_allow_html=True)

    # Step 4 — Options
    with card():
        st.markdown('<div class="section-label">Step 4 — Options</div>', unsafe_allow_html=True)
        include_projects = st.checkbox(
            "Include suggested projects in final resume",
            value=True
        )

    # Readiness checklist
    ready = (
        st.session_state.resume_text
        and st.session_state.jd_text
        and target_role
    )
    missing = []
    if not st.session_state.resume_text: missing.append("resume")
    if not target_role:                  missing.append("target role")
    if not st.session_state.jd_text:    missing.append("job description")

    with card(key="ready_checklist"):
        st.markdown('<div class="section-label">Ready checklist</div>', unsafe_allow_html=True)

        checks = {
            "Resume uploaded (PDF/DOCX)":    bool(st.session_state.resume_text),
            "Target role entered":            bool(target_role),
            "Job description provided":       bool(st.session_state.jd_text),
            "Click Analyze to start pipeline": False,
        }
        items_html = ""
        for label, done in checks.items():
            icon  = "✓" if done else "○"
            color = "#16a34a" if done else "#aaa"
            items_html += f'<li style="display:flex;gap:8px;font-size:14px;padding:4px 0"><span style="color:{color};font-weight:700">{icon}</span>{label}</li>'
        st.markdown(f'<ul style="list-style:none;padding:0">{items_html}</ul>', unsafe_allow_html=True)

        # Run button
        if st.button(
            "🚀 Analyze & Build My Resume",
            disabled=not ready,
            type="primary",
            use_container_width=True
        ):
            with st.status("🤖 Running 4-agent pipeline...", expanded=True) as status:
                st.write("🔍 Agent 1: Parsing job description...")
                st.write("⭐ Agent 2: Evaluating your resume...")
                st.write("💡 Agent 3: Analyzing gaps & suggesting projects...")
                st.write("✍️ Agent 4: Writing your tailored resume...")
                try:
                    result = run_pipeline(
                        resume_text=st.session_state.resume_text,
                        jd_text=st.session_state.jd_text,
                        include_suggested_projects=include_projects
                    )
                    if result.get("error"):
                        status.update(label="❌ Error occurred", state="error")
                        st.error(result["error"])
                    else:
                        st.session_state.pipeline_result = result
                        status.update(label="✅ All 4 agents completed!", state="complete")
                        st.success("Done! Check the other tabs for results →")
                except Exception as e:
                    status.update(label="❌ Pipeline failed", state="error")
                    st.error(f"Error: {e}")


# ── Helper ──
def no_results():
    st.markdown("""
    <div class="main-content">
    <div class="info-box">
        👈 Complete the <strong>Input</strong> tab first and
        click <strong>Analyze & Build My Resume</strong>
    </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════
# TAB 2 — JD ANALYSIS
# ════════════════════════════════════════
with tab2:
    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        st.markdown('<span class="agent-badge badge-coral">Agent 1 — JD Parser · jd_parser.py</span>', unsafe_allow_html=True)

        jd = result["parsed_jd"]

        # Role details card
        with card():
            st.markdown('<div class="section-label">Role details</div>', unsafe_allow_html=True)
            kv_items = [
                ("Role",       jd.get("role", "N/A")),
                ("Company",    jd.get("company", "N/A")),
                ("Experience", jd.get("experience_years", "N/A")),
                ("Education",  jd.get("education", "N/A")),
            ]
            kv_html = "".join([
                f'<div class="kv-row"><span class="kv-key">{k}</span><span class="kv-val">{v}</span></div>'
                for k, v in kv_items
            ])
            st.markdown(kv_html, unsafe_allow_html=True)
            st.markdown(f"""
            <div style="margin-top:14px">
                <div class="section-label">Summary</div>
                <div class="info-box">{jd.get("summary", "N/A")}</div>
            </div>
            """, unsafe_allow_html=True)

        # Skills grid
        col1, col2 = st.columns(2)
        with col1:
            with card():
                st.markdown('<div class="section-label">Required skills</div>', unsafe_allow_html=True)
                tags = "".join([f'<span class="tag tag-blue">{s}</span>' for s in jd.get("required_skills", [])])
                st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
        with col2:
            with card():
                st.markdown('<div class="section-label">Preferred skills</div>', unsafe_allow_html=True)
                tags = "".join([f'<span class="tag tag-gray">{s}</span>' for s in jd.get("preferred_skills", [])])
                st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)

        # Responsibilities
        with card():
            st.markdown('<div class="section-label">Key responsibilities</div>', unsafe_allow_html=True)
            items = "".join([f"<li style='font-size:14px;color:#444;padding:3px 0'>{r}</li>" for r in jd.get("responsibilities", [])])
            st.markdown(f'<ul style="padding-left:18px;line-height:2">{items}</ul>', unsafe_allow_html=True)

        # ATS Keywords
        with card():
            st.markdown('<div class="section-label">ATS keywords to include in resume</div>', unsafe_allow_html=True)
            tags = "".join([f'<span class="tag tag-blue">{k}</span>' for k in jd.get("keywords", [])])
            st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# TAB 3 — SCORE CARD
# ════════════════════════════════════════
with tab3:
    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        st.markdown('<span class="agent-badge badge-amber">Agent 2 — Resume Evaluator · resume_evaluator.py</span>', unsafe_allow_html=True)

        ev      = result["evaluation"]
        overall = ev.get("overall_score", 0)
        color_class = "green" if overall >= 7 else "amber" if overall >= 5 else "red"
        circle_color = "#2e6b4c" if overall >= 7 else "#93641c" if overall >= 5 else "#a83a2c"

        # Big score — graded like a paper, circled in pen
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.markdown(f"""
            <div class="score-big">
                <div class="score-circle-wrap">
                    <svg viewBox="0 0 130 130" width="130" height="130" style="position:absolute;inset:0">
                        <path d="M65,7 C97,5 124,29 126,61 C128,96 101,125 66,124
                                 C31,123 5,98 6,63 C7,30 34,6 65,7 Z"
                              fill="none" stroke="{circle_color}" stroke-width="3"
                              stroke-linecap="round" opacity="0.85"/>
                    </svg>
                    <div class="score-num {color_class}">{overall}/10</div>
                </div>
                <div class="score-label">Overall resume score for this role</div>
            </div>
            """, unsafe_allow_html=True)

        # Score breakdown
        with card():
            st.markdown('<div class="section-label">Score breakdown</div>', unsafe_allow_html=True)
            breakdown = ev.get("breakdown", {})
            for metric, score in breakdown.items():
                label  = metric.replace("_", " ").title()
                pct    = int((score / 10) * 100)
                fc     = "green" if score >= 7 else "amber" if score >= 5 else ""
                st.markdown(f"""
                <div class="progress-item">
                    <div class="progress-row">
                        <span>{label}</span>
                        <span style="font-weight:500">{score}/10</span>
                    </div>
                    <div class="progress-track">
                        <div class="progress-fill {fc}" style="width:{pct}%"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Matched vs Missing
        col1, col2 = st.columns(2)
        with col1:
            with card():
                st.markdown('<div class="section-label">Matched skills</div>', unsafe_allow_html=True)
                tags = "".join([f'<span class="tag tag-green">✅ {s}</span>' for s in ev.get("matched_skills", [])])
                st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-label" style="margin-top:16px">Strengths</div>', unsafe_allow_html=True)
                items = "".join([f"<li style='font-size:14px;color:#444;padding:2px 0'>{s}</li>" for s in ev.get("strengths", [])])
                st.markdown(f'<ul style="padding-left:16px;line-height:1.9">{items}</ul>', unsafe_allow_html=True)
        with col2:
            with card():
                st.markdown('<div class="section-label">Missing skills</div>', unsafe_allow_html=True)
                tags = "".join([f'<span class="tag tag-red">❌ {s}</span>' for s in ev.get("missing_skills", [])])
                st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
                st.markdown('<div class="section-label" style="margin-top:16px">Weaknesses</div>', unsafe_allow_html=True)
                items = "".join([f"<li style='font-size:14px;color:#444;padding:2px 0'>{s}</li>" for s in ev.get("weaknesses", [])])
                st.markdown(f'<ul style="padding-left:16px;line-height:1.9">{items}</ul>', unsafe_allow_html=True)

        # Verdict
        with card():
            st.markdown('<div class="section-label">Hiring manager\'s verdict</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="verdict">{ev.get("verdict", "N/A")}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# TAB 4 — SUGGESTIONS
# ════════════════════════════════════════
with tab4:
    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        st.markdown('<span class="agent-badge badge-blue">Agent 3 — Gap Analyst · gap_analyst.py</span>', unsafe_allow_html=True)

        gap = result["gap_analysis"]

        # What they want
        with card():
            st.markdown('<div class="section-label">What they\'re really looking for</div>', unsafe_allow_html=True)
            items = "".join([f"<li style='font-size:14px;color:#444;padding:3px 0'>{w}</li>" for w in gap.get("what_they_want", [])])
            st.markdown(f'<ul style="padding-left:18px;line-height:2">{items}</ul>', unsafe_allow_html=True)

        # Critical gaps
        with card():
            st.markdown('<div class="section-label">Critical gaps</div>', unsafe_allow_html=True)
            for g in gap.get("critical_gaps", []):
                imp        = g.get("importance", "Medium")
                extra_cls  = "gap-card-medium" if imp == "Medium" else ""
                badge_cls  = "priority-high" if imp == "High" else "priority-medium" if imp == "Medium" else "priority-low"
                st.markdown(f"""
                <div class="gap-card {extra_cls}">
                    <span class="{badge_cls}">{imp} priority</span>
                    <div class="gap-title">{g.get("gap")}</div>
                    <div class="gap-fix">💡 {g.get("how_to_fix")}</div>
                </div>
                """, unsafe_allow_html=True)

        # Suggested projects
        with card():
            st.markdown('<div class="section-label">Suggested projects to add</div>', unsafe_allow_html=True)
            for p in gap.get("suggested_projects", []):
                tech = " · ".join(p.get("tech_stack", []))
                st.markdown(f"""
                <div class="project-card">
                    <div class="project-title">🛠️ {p.get("title")}</div>
                    <div class="project-tech">{tech}</div>
                    <div class="project-desc">{p.get("description")}</div>
                    <div style="font-size:12px;color:#444;margin-bottom:6px">
                        <strong>Why it helps:</strong> {p.get("why_it_helps")}
                    </div>
                    <span class="project-metric">⚡ {p.get("sample_metric")}</span>
                </div>
                """, unsafe_allow_html=True)

        # Quick wins
        with card():
            st.markdown('<div class="section-label">Quick wins — fix these immediately</div>', unsafe_allow_html=True)
            items = "".join([f"<li style='font-size:14px;color:#444;padding:3px 0'>✅ {qw}</li>" for qw in gap.get("quick_wins", [])])
            st.markdown(f'<ul style="padding-left:18px;line-height:2">{items}</ul>', unsafe_allow_html=True)


# ════════════════════════════════════════
# TAB 5 — FINAL RESUME
# ════════════════════════════════════════
with tab5:
    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        st.markdown('<span class="agent-badge badge-green">Agent 4 — Resume Writer · resume_writer.py</span>', unsafe_allow_html=True)

        final_resume = result.get("final_resume", "")

        if final_resume:
            # Download button
            try:
                docx_bytes = generate_resume_docx(final_resume)
                st.download_button(
                    label="⬇ Download Resume as DOCX",
                    data=docx_bytes,
                    file_name="tailored_resume.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
            except Exception as e:
                st.warning(f"DOCX generation failed: {e}")

            # Resume preview card
            st.markdown('<div style="margin-top:16px"></div>', unsafe_allow_html=True)
            with card(key="resume_preview"):
                st.markdown("""
                <div style="background:#f8f7f4;padding:10px 16px;border-bottom:1px solid #e5e3db;
                            font-size:12px;color:#888;font-weight:500">
                    FINAL RESUME PREVIEW — tailored_resume.docx
                </div>
                """, unsafe_allow_html=True)

                # Render resume lines as styled HTML
                lines      = final_resume.strip().split("\n")
                resume_html = '<div class="resume-preview" style="border:none;border-radius:0;margin:0">'
                for i, line in enumerate(lines):
                    line = line.strip()
                    if not line:
                        resume_html += "<br/>"
                        continue
                    is_header = line.startswith("##") or line.isupper() or (len(line) < 40 and line.endswith(":"))
                    if i == 0:
                        resume_html += f'<div class="resume-name">{line.replace("#","").strip()}</div>'
                    elif i == 1 and any(c in line for c in ["@", "|", "·"]):
                        resume_html += f'<div class="resume-contact">{line}</div>'
                    elif is_header:
                        resume_html += f'<div class="resume-section">{line.replace("##","").replace(":","").strip()}</div>'
                    elif line.startswith(("•", "-", "*")):
                        resume_html += f'<div style="font-size:14px;color:#333;padding:2px 0 2px 16px">• {line.lstrip("•-* ").strip()}</div>'
                    else:
                        resume_html += f'<div style="font-size:14px;color:#333;padding:2px 0">{line}</div>'
                resume_html += '</div>'

                st.markdown(resume_html, unsafe_allow_html=True)

            # Footer note
            role = result["parsed_jd"].get("role", "this role")
            company = result["parsed_jd"].get("company", "")
            st.markdown(f"""
            <div style="margin-top:12px;font-size:12px;color:#888;text-align:center">
                Resume generated by Agent 4 · Tailored for {role}
                {f"at {company}" if company != "Unknown" else ""}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("Resume writer returned empty output. Please try again.")