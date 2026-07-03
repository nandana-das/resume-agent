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

# ── CSS — matches HTML mockup exactly ──
st.markdown("""
<style>
/* ── Global ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    background: #f8f7f4 !important;
    color: #1a1a1a !important;
}

/* Hide default Streamlit header and footer */
#MainMenu, footer, header { visibility: hidden; }

/* Remove default padding */
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── App Header ── */
.app-header {
    background: #fff;
    border-bottom: 1px solid #e5e3db;
    padding: 14px 32px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 0;
}
.app-header h1 { font-size: 18px; font-weight: 500; margin: 0; }
.app-header span { font-size: 13px; color: #888; }

/* ── Content wrapper ── */
.main-content { max-width: 860px; margin: 0 auto; padding: 28px 24px; }

/* ── Cards ── */
.card {
    background: #fff;
    border: 1px solid #e5e3db;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}

/* ── Section labels ── */
.section-label {
    font-size: 12px;
    font-weight: 500;
    color: #888;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}

/* ── Agent badges ── */
.agent-badge {
    display: inline-block;
    color: #fff;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 14px;
    letter-spacing: 0.3px;
}
.badge-coral  { background: #993C1D; }
.badge-amber  { background: #854F0B; }
.badge-blue   { background: #185FA5; }
.badge-green  { background: #3B6D11; }
.badge-purple { background: #4f46e5; }

/* ── Tag pills ── */
.tag-wrap { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.tag {
    font-size: 12px; font-weight: 500;
    padding: 4px 10px; border-radius: 20px;
}
.tag-blue  { background: #eef2ff; color: #3730a3; }
.tag-green { background: #f0fdf4; color: #15803d; }
.tag-red   { background: #fef2f2; color: #b91c1c; }
.tag-gray  { background: #f1efe8; color: #5f5e5a; }

/* ── Score display ── */
.score-big {
    text-align: center;
    padding: 28px;
    background: #f0fdf4;
    border-radius: 12px;
    border: 1.5px solid #86efac;
    margin-bottom: 20px;
}
.score-num { font-size: 56px; font-weight: 700; color: #16a34a; line-height: 1; }
.score-num.amber { color: #d97706; }
.score-num.red   { color: #dc2626; }
.score-label { font-size: 13px; color: #666; margin-top: 4px; }

/* ── Progress bars ── */
.progress-item { margin-bottom: 14px; }
.progress-row  { display: flex; justify-content: space-between; font-size: 13px; margin-bottom: 5px; }
.progress-track { height: 6px; background: #f1efe8; border-radius: 4px; overflow: hidden; }
.progress-fill  { height: 100%; border-radius: 4px; background: #4f46e5; }
.progress-fill.green { background: #16a34a; }
.progress-fill.amber { background: #d97706; }

/* ── Verdict box ── */
.verdict {
    background: #fffbeb;
    border: 1px solid #fcd34d;
    border-radius: 8px;
    padding: 14px 16px;
    font-size: 13px;
    color: #78350f;
    line-height: 1.6;
}

/* ── KV rows ── */
.kv-row { display: flex; justify-content: space-between; font-size: 13px; padding: 6px 0; border-bottom: 1px solid #f1efe8; }
.kv-row:last-child { border-bottom: none; }
.kv-key { color: #666; }
.kv-val { font-weight: 500; }

/* ── Gap cards ── */
.gap-card {
    border-left: 3px solid #ef4444;
    padding: 12px 14px;
    background: #fef2f2;
    border-radius: 0 8px 8px 0;
    margin-bottom: 10px;
}
.gap-card-medium { border-left-color: #f59e0b !important; background: #fffbeb !important; }
.gap-title { font-size: 13px; font-weight: 500; margin-bottom: 4px; }
.gap-fix   { font-size: 12px; color: #666; }
.priority-high   { display:inline-block; font-size:11px; font-weight:500; padding:2px 7px; border-radius:10px; background:#fee2e2; color:#b91c1c; margin-bottom:4px; }
.priority-medium { display:inline-block; font-size:11px; font-weight:500; padding:2px 7px; border-radius:10px; background:#fef3c7; color:#92400e; margin-bottom:4px; }
.priority-low    { display:inline-block; font-size:11px; font-weight:500; padding:2px 7px; border-radius:10px; background:#f1efe8; color:#5f5e5a; margin-bottom:4px; }

/* ── Project cards ── */
.project-card {
    background: #f0fdf4;
    border-left: 3px solid #22c55e;
    border-radius: 0 10px 10px 0;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.project-title  { font-size: 14px; font-weight: 500; margin-bottom: 4px; }
.project-tech   { font-size: 12px; color: #166534; font-family: monospace; margin-bottom: 6px; }
.project-desc   { font-size: 13px; color: #444; line-height: 1.5; margin-bottom: 6px; }
.project-metric { font-size: 12px; background: #dcfce7; color: #166534; padding: 3px 8px; border-radius: 6px; display: inline-block; }

/* ── Resume preview ── */
.resume-preview {
    background: #fff;
    border: 1px solid #e5e3db;
    border-radius: 10px;
    padding: 28px 32px;
    font-family: Georgia, serif;
    line-height: 1.6;
    font-size: 13px;
}
.resume-name    { font-size: 22px; font-weight: 700; text-align: center; margin-bottom: 4px; }
.resume-contact { text-align: center; font-size: 12px; color: #666; margin-bottom: 20px; }
.resume-section {
    font-size: 11px; font-weight: 700; letter-spacing: 1px;
    text-transform: uppercase; border-bottom: 1.5px solid #1a1a1a;
    margin: 16px 0 8px; padding-bottom: 3px;
    font-family: -apple-system, sans-serif;
}

/* ── 2-col grid ── */
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

/* ── Success / info boxes ── */
.success-box {
    background: #f0fdf4; border: 1px solid #86efac;
    border-radius: 8px; padding: 12px 14px;
    font-size: 13px; color: #166534; margin-bottom: 14px;
}
.info-box {
    background: #eef2ff; border: 1px solid #c7d2fe;
    border-radius: 8px; padding: 12px 14px;
    font-size: 13px; color: #3730a3; margin-bottom: 14px;
}

/* ── Upload zone ── */
.upload-zone {
    border: 1.5px dashed #c9c7be; border-radius: 10px;
    padding: 32px; text-align: center; background: #fafaf8;
    cursor: pointer;
}
.upload-icon { font-size: 32px; margin-bottom: 8px; }

/* ── Streamlit overrides ── */
div[data-testid="stTabs"] button {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #666 !important;
    padding: 12px 18px !important;
}
div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #4f46e5 !important;
    border-bottom-color: #4f46e5 !important;
}
div[data-testid="stFileUploader"] {
    background: #fafaf8 !important;
    border: 1.5px dashed #c9c7be !important;
    border-radius: 10px !important;
}
.stButton button {
    background: #4f46e5 !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
}
.stButton button:hover { background: #4338ca !important; }
.stTextInput input, .stTextArea textarea {
    border: 1px solid #e5e3db !important;
    border-radius: 8px !important;
    font-size: 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79,70,229,0.08) !important;
}
.stRadio label { font-size: 14px !important; }
.stCheckbox label { font-size: 14px !important; }
div[data-testid="stExpander"] {
    border: 1px solid #e5e3db !important;
    border-radius: 8px !important;
    background: #fff !important;
}
hr { border: none; border-top: 1px solid #e5e3db; margin: 18px 0; }
</style>
""", unsafe_allow_html=True)

# ── App Header ──
st.markdown("""
<div class="app-header">
    <span style="font-size:22px">📄</span>
    <div>
        <h1>AI Resume Builder</h1>
        <span>4-agent system that tailors your resume to any job description</span>
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
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Step 1 — Upload
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 2 — Target Role
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Step 2 — Target role</div>', unsafe_allow_html=True)
    target_role = st.text_input(
        "Target Role",
        placeholder="e.g. Senior Data Scientist, ML Engineer, Backend Developer",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 3 — Job Description
    st.markdown('<div class="card">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

    # Step 4 — Options
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Step 4 — Options</div>', unsafe_allow_html=True)
    include_projects = st.checkbox(
        "Include suggested projects in final resume",
        value=True
    )
    st.markdown('</div>', unsafe_allow_html=True)

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

    st.markdown('<div class="card" style="background:#fafaf8">', unsafe_allow_html=True)
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
        items_html += f'<li style="display:flex;gap:8px;font-size:13px;padding:4px 0"><span style="color:{color};font-weight:700">{icon}</span>{label}</li>'
    st.markdown(f'<ul style="list-style:none;padding:0">{items_html}</ul>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)


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
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-coral">Agent 1 — JD Parser · jd_parser.py</span>', unsafe_allow_html=True)

        jd = result["parsed_jd"]

        # Role details card
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        # Skills grid
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Required skills</div>', unsafe_allow_html=True)
            tags = "".join([f'<span class="tag tag-blue">{s}</span>' for s in jd.get("required_skills", [])])
            st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Preferred skills</div>', unsafe_allow_html=True)
            tags = "".join([f'<span class="tag tag-gray">{s}</span>' for s in jd.get("preferred_skills", [])])
            st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Responsibilities
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Key responsibilities</div>', unsafe_allow_html=True)
        items = "".join([f"<li style='font-size:13px;color:#444;padding:3px 0'>{r}</li>" for r in jd.get("responsibilities", [])])
        st.markdown(f'<ul style="padding-left:18px;line-height:2">{items}</ul>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ATS Keywords
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">ATS keywords to include in resume</div>', unsafe_allow_html=True)
        tags = "".join([f'<span class="tag tag-blue">{k}</span>' for k in jd.get("keywords", [])])
        st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# TAB 3 — SCORE CARD
# ════════════════════════════════════════
with tab3:
    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-amber">Agent 2 — Resume Evaluator · resume_evaluator.py</span>', unsafe_allow_html=True)

        ev      = result["evaluation"]
        overall = ev.get("overall_score", 0)
        color_class = "green" if overall >= 7 else "amber" if overall >= 5 else "red"
        border_color = "#86efac" if overall >= 7 else "#fcd34d" if overall >= 5 else "#fca5a5"
        bg_color     = "#f0fdf4" if overall >= 7 else "#fffbeb" if overall >= 5 else "#fef2f2"

        # Big score
        _, mid, _ = st.columns([1, 2, 1])
        with mid:
            st.markdown(f"""
            <div style="text-align:center;padding:28px;background:{bg_color};
                        border-radius:12px;border:1.5px solid {border_color};margin-bottom:20px">
                <div class="score-num {color_class}">{overall}/10</div>
                <div class="score-label">Overall resume score for this role</div>
            </div>
            """, unsafe_allow_html=True)

        # Score breakdown
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        # Matched vs Missing
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Matched skills</div>', unsafe_allow_html=True)
            tags = "".join([f'<span class="tag tag-green">✅ {s}</span>' for s in ev.get("matched_skills", [])])
            st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label" style="margin-top:16px">Strengths</div>', unsafe_allow_html=True)
            items = "".join([f"<li style='font-size:13px;color:#444;padding:2px 0'>{s}</li>" for s in ev.get("strengths", [])])
            st.markdown(f'<ul style="padding-left:16px;line-height:1.9">{items}</ul>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<div class="section-label">Missing skills</div>', unsafe_allow_html=True)
            tags = "".join([f'<span class="tag tag-red">❌ {s}</span>' for s in ev.get("missing_skills", [])])
            st.markdown(f'<div class="tag-wrap">{tags}</div>', unsafe_allow_html=True)
            st.markdown('<div class="section-label" style="margin-top:16px">Weaknesses</div>', unsafe_allow_html=True)
            items = "".join([f"<li style='font-size:13px;color:#444;padding:2px 0'>{s}</li>" for s in ev.get("weaknesses", [])])
            st.markdown(f'<ul style="padding-left:16px;line-height:1.9">{items}</ul>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        # Verdict
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Hiring manager\'s verdict</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="verdict">{ev.get("verdict", "N/A")}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# TAB 4 — SUGGESTIONS
# ════════════════════════════════════════
with tab4:
    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
        st.markdown('<span class="agent-badge badge-blue">Agent 3 — Gap Analyst · gap_analyst.py</span>', unsafe_allow_html=True)

        gap = result["gap_analysis"]

        # What they want
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">What they\'re really looking for</div>', unsafe_allow_html=True)
        items = "".join([f"<li style='font-size:13px;color:#444;padding:3px 0'>{w}</li>" for w in gap.get("what_they_want", [])])
        st.markdown(f'<ul style="padding-left:18px;line-height:2">{items}</ul>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Critical gaps
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        # Suggested projects
        st.markdown('<div class="card">', unsafe_allow_html=True)
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
        st.markdown('</div>', unsafe_allow_html=True)

        # Quick wins
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="section-label">Quick wins — fix these immediately</div>', unsafe_allow_html=True)
        items = "".join([f"<li style='font-size:13px;color:#444;padding:3px 0'>✅ {qw}</li>" for qw in gap.get("quick_wins", [])])
        st.markdown(f'<ul style="padding-left:18px;line-height:2">{items}</ul>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════
# TAB 5 — FINAL RESUME
# ════════════════════════════════════════
with tab5:
    result = st.session_state.pipeline_result
    if not result:
        no_results()
    else:
        st.markdown('<div class="main-content">', unsafe_allow_html=True)
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
            st.markdown("""
            <div class="card" style="padding:0;overflow:hidden;margin-top:16px">
                <div style="background:#f8f7f4;padding:10px 16px;border-bottom:1px solid #e5e3db;
                            font-size:12px;color:#888;font-weight:500">
                    FINAL RESUME PREVIEW — tailored_resume.docx
                </div>
                <div style="padding:24px">
            """, unsafe_allow_html=True)

            # Render resume lines as styled HTML
            lines      = final_resume.strip().split("\n")
            resume_html = '<div class="resume-preview">'
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
                    resume_html += f'<div style="font-size:13px;color:#333;padding:2px 0 2px 16px">• {line.lstrip("•-* ").strip()}</div>'
                else:
                    resume_html += f'<div style="font-size:13px;color:#333;padding:2px 0">{line}</div>'
            resume_html += '</div>'

            st.markdown(resume_html, unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

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

        st.markdown('</div>', unsafe_allow_html=True)