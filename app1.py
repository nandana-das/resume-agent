import streamlit as st
from contextlib import contextmanager
from utils.pdf_extractor import extract_resume_text
from utils.jd_scraper import fetch_jd_from_url
from utils.resume_generator import generate_resume_docx
from graph.pipeline import run_pipeline
from agents.resume_writer import write_resume

# ── Page Config ──
st.set_page_config(
    page_title="Resume Helper",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

TOTAL_STEPS = 4

# ── Session state ──
_defaults = {
    "step": 1,
    "resume_text": "",
    "resume_filename": "",
    "target_role": "",
    "jd_mode": "link",       # "link" or "paste"
    "job_url": "",
    "jd_text": "",
    "include_projects": True,
    "pipeline_result": None,
    "final_resume": None,
    "final_resume_is_fallback": False,
}
for _k, _v in _defaults.items():
    if _k not in st.session_state:
        st.session_state[_k] = _v


@contextmanager
def card():
    """A real card container — st.container(border=True) nests properly,
    unlike raw markdown div strings which don't."""
    with st.container(border=True):
        yield


def go_to(step: int):
    st.session_state.step = step
    st.rerun()


def restart():
    for k, v in _defaults.items():
        st.session_state[k] = v
    st.rerun()


# ── CSS — warm, rounded, plain-language design ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap');

:root {
    --bg: #fafafa;
    --card: #ffffff;
    --border: #e7e7e5;
    --border-strong: #d6d5d1;
    --ink: #1a1a1a;
    --ink-soft: #767671;
    --accent: #1a1a1a;
    --accent-soft: #f0efec;
    --success: #1a1a1a;
    --success-soft: #f0efec;
    --warning: #4d4d49;
    --warning-soft: #f5f4f1;
}

html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stHeader"] {
    font-family: 'Nunito', -apple-system, sans-serif !important;
    background: var(--bg) !important;
    color: var(--ink) !important;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 1rem 3rem !important; max-width: 640px !important; }

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    box-shadow: 0 2px 10px rgba(35,38,47,0.05) !important;
    margin-bottom: 16px !important;
}
div[data-testid="stVerticalBlockBorderWrapper"] > div > div[data-testid="stVerticalBlock"] {
    padding: 28px 26px !important;
}

.dots { display: flex; justify-content: center; gap: 8px; margin-bottom: 18px; }
.dot { width: 8px; height: 8px; border-radius: 50%; background: var(--border-strong); display: inline-block; }
.dot.active { width: 24px; border-radius: 4px; background: var(--accent); }

.step-caption { text-align: center; font-size: 13px; color: var(--ink-soft); font-weight: 700; letter-spacing: 0.03em; margin: 0 0 4px; }
.step-headline { text-align: center; font-size: 26px; font-weight: 800; margin: 0 0 8px; color: var(--ink); }
.step-sub { text-align: center; font-size: 15px; color: var(--ink-soft); line-height: 1.6; margin: 0 0 24px; }

.section-title { font-size: 15px; font-weight: 800; margin: 0 0 10px; display: flex; align-items: center; gap: 7px; color: var(--ink); }
.plain-line { font-size: 14.5px; color: var(--ink-soft); line-height: 1.7; margin: 0 0 6px; }

.pill { display: inline-flex; align-items: center; font-size: 13px; font-weight: 700; padding: 6px 13px; border-radius: 999px; margin: 0 6px 6px 0; }
.pill-good { background: var(--ink); color: #fff; }
.pill-todo { background: #fff; color: var(--ink-soft); border: 1.5px solid var(--border-strong); }

.priority-tag { display: inline-block; font-size: 11.5px; font-weight: 700; padding: 3px 10px; border-radius: 999px; margin-bottom: 8px; }
.priority-first { background: var(--ink); color: #fff; }
.priority-good  { background: var(--accent-soft); color: var(--ink); border: 1px solid var(--border-strong); }
.priority-nice  { background: transparent; color: var(--ink-soft); border: 1px solid var(--border); }

.project-card { background: var(--bg); border: 1px solid var(--border); border-radius: 14px; padding: 16px 18px; margin-bottom: 10px; }
.project-title { font-size: 14.5px; font-weight: 800; margin-bottom: 5px; color: var(--ink); }
.project-desc { font-size: 13.5px; color: var(--ink); line-height: 1.6; margin-bottom: 4px; }

.resume-preview { background: #fff; border-radius: 14px; padding: 30px 32px; font-size: 14px; line-height: 1.65; color: #262626; }
.resume-name { font-size: 21px; font-weight: 800; text-align: center; margin-bottom: 4px; }
.resume-contact { text-align: center; font-size: 12px; color: var(--ink-soft); margin-bottom: 20px; }
.resume-section { font-size: 12px; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); border-bottom: 1px solid var(--border); margin: 16px 0 8px; padding-bottom: 4px; }

.upload-zone { border: 1.5px dashed var(--border-strong); border-radius: 16px; padding: 26px 20px; text-align: center; background: var(--bg); }
.upload-icon { width: 44px; height: 44px; border-radius: 50%; background: var(--accent-soft); display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; font-size: 20px; }

.stTextInput input, .stTextArea textarea {
    border: 1.5px solid var(--border-strong) !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    background: #fff !important;
    color: var(--ink) !important;
    padding: 10px 14px !important;
}
.stTextInput input:focus, .stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--accent-soft) !important;
}
div[data-testid="stTextInput"] label, div[data-testid="stTextArea"] label {
    color: var(--ink) !important; font-size: 14.5px !important; font-weight: 700 !important; opacity: 1 !important;
}

.stButton button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    height: 46px !important;
    box-shadow: none !important;
}
.stButton button[kind="primary"] {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
}
.stButton button[kind="primary"]:hover { background: #3a3a38 !important; }
.stButton button[kind="secondary"] {
    background: #fff !important;
    color: var(--ink-soft) !important;
    border: 1.5px solid var(--border-strong) !important;
}
.stButton button[kind="secondary"]:hover { border-color: var(--accent) !important; color: var(--accent) !important; }

div[data-testid="stFileUploader"] { background: var(--bg) !important; border-radius: 14px !important; }
div[data-testid="stFileUploader"] section { border: none !important; background: transparent !important; }

.back-link { font-size: 13.5px; color: var(--ink-soft); font-weight: 700; cursor: pointer; }
</style>
""", unsafe_allow_html=True)


def progress_dots(current: int):
    dots = "".join(
        f'<span class="dot{" active" if i == current else ""}"></span>'
        for i in range(1, TOTAL_STEPS + 1)
    )
    st.markdown(f'<div class="dots">{dots}</div>', unsafe_allow_html=True)


def step_header(current: int, headline: str, sub: str = ""):
    progress_dots(current)
    st.markdown(f'<p class="step-caption">Step {current} of {TOTAL_STEPS}</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="step-headline">{headline}</p>', unsafe_allow_html=True)
    if sub:
        st.markdown(f'<p class="step-sub">{sub}</p>', unsafe_allow_html=True)


def score_ring(score: int) -> str:
    pct = max(0, min(100, int(score * 10)))
    if score >= 7:
        color, label = "var(--success)", "Great match — you're in good shape"
    elif score >= 5:
        color, label = "var(--warning)", "Pretty good match — a few tweaks will help"
    else:
        color, label = "var(--warning)", "Let's strengthen this before you apply"
    return f"""
    <div style="display:flex;justify-content:center;margin:6px 0 10px">
        <div style="width:140px;height:140px;border-radius:50%;
                    background:conic-gradient({color} 0% {pct}%, var(--border) {pct}% 100%);
                    display:flex;align-items:center;justify-content:center">
            <div style="width:110px;height:110px;border-radius:50%;background:var(--card);
                        display:flex;align-items:center;justify-content:center">
                <span style="font-size:28px;font-weight:800;color:var(--ink)">{score}/10</span>
            </div>
        </div>
    </div>
    <p style="text-align:center;font-size:15px;color:{color};font-weight:700;margin:0 0 22px">{label}</p>
    """


# ── STEP 1 — Start ──
def render_step1():
    step_header(
        1,
        "Let's tailor your resume",
        "Add your resume and tell us about the job you want. We'll take it from there."
    )

    with card():
        st.markdown('<div class="section-title">Your resume</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Add your resume", type=["pdf", "docx"], label_visibility="collapsed"
        )
        if uploaded_file:
            try:
                st.session_state.resume_text = extract_resume_text(uploaded_file)
                st.session_state.resume_filename = uploaded_file.name
                st.markdown(
                    f'<p class="plain-line">✓ Got it — <strong>{uploaded_file.name}</strong> is ready.</p>',
                    unsafe_allow_html=True
                )
            except Exception as e:
                st.error(f"We couldn't read that file — try a PDF or Word document. ({e})")
        elif st.session_state.resume_text:
            st.markdown(
                f'<p class="plain-line">✓ Using <strong>{st.session_state.resume_filename}</strong>.</p>',
                unsafe_allow_html=True
            )

    with card():
        st.markdown('<div class="section-title">The job you want</div>', unsafe_allow_html=True)
        st.session_state.target_role = st.text_input(
            "What job are you applying for?",
            value=st.session_state.target_role,
            placeholder="e.g. Marketing manager at a tech company"
        )

        st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
        st.markdown('<p style="font-size:14.5px;font-weight:700;margin:0 0 10px">How do you want to share the job details?</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("I have a link", use_container_width=True,
                         type="primary" if st.session_state.jd_mode == "link" else "secondary"):
                st.session_state.jd_mode = "link"
                st.rerun()
        with col2:
            if st.button("I'll paste it myself", use_container_width=True,
                         type="primary" if st.session_state.jd_mode == "paste" else "secondary"):
                st.session_state.jd_mode = "paste"
                st.rerun()

        st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

        if st.session_state.jd_mode == "link":
            st.session_state.job_url = st.text_input(
                "Job posting link", value=st.session_state.job_url,
                placeholder="Paste the link to the job posting", label_visibility="collapsed"
            )
        else:
            st.session_state.jd_text = st.text_area(
                "Job description", value=st.session_state.jd_text, height=160,
                placeholder="Paste the full job description here", label_visibility="collapsed"
            )

    ready = bool(st.session_state.resume_text) and bool(st.session_state.target_role) and (
        bool(st.session_state.job_url) if st.session_state.jd_mode == "link" else bool(st.session_state.jd_text)
    )

    if st.button("Continue →", type="primary", use_container_width=True, disabled=not ready):
        run_full_pipeline()

    if not ready:
        st.markdown(
            '<p style="text-align:center;font-size:12.5px;color:var(--ink-soft);margin-top:8px">'
            'Add your resume, the job title, and the job details to continue.</p>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<p style="text-align:center;font-size:12px;color:var(--ink-soft);margin-top:10px">'
            'Nothing to lose — you can change any of this later.</p>',
            unsafe_allow_html=True
        )


def run_full_pipeline():
    with st.status("Working on it...", expanded=True) as status:
        try:
            if st.session_state.jd_mode == "link":
                st.write("Reading the job posting...")
                st.session_state.jd_text = fetch_jd_from_url(st.session_state.job_url)

            st.write("Understanding what the role needs...")
            st.write("Comparing it to your resume...")
            st.write("Finding ways to improve it...")

            result = run_pipeline(
                resume_text=st.session_state.resume_text,
                jd_text=st.session_state.jd_text,
                include_suggested_projects=st.session_state.include_projects
            )

            if result.get("error"):
                status.update(label="Something went wrong", state="error")
                st.error("We hit a snag looking at your resume. Please try again in a moment.")
                return

            st.session_state.pipeline_result = result
            final_resume = (result.get("final_resume") or "").strip()
            if not final_resume:
                final_resume = st.session_state.resume_text.strip()
                st.session_state.final_resume_is_fallback = True
            else:
                st.session_state.final_resume_is_fallback = False

            st.session_state.final_resume = final_resume
            status.update(label="All done!", state="complete")
            go_to(2)

        except Exception:
            status.update(label="Something went wrong", state="error")
            st.error("We couldn't fetch that job posting. Try pasting the details instead.")


# ── STEP 2 — Match results ──
def render_step2():
    result = st.session_state.pipeline_result
    if not result:
        go_to(1)
        return

    ev = result["evaluation"]
    score = ev.get("overall_score", 0)

    step_header(2, "Here's how your resume matches")

    with card():
        st.markdown(score_ring(score), unsafe_allow_html=True)

        st.markdown('<div class="section-title">What\'s working well</div>', unsafe_allow_html=True)
        for s in ev.get("strengths", []):
            st.markdown(f'<p class="plain-line">{s}</p>', unsafe_allow_html=True)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">What could be better</div>', unsafe_allow_html=True)
        for w in ev.get("weaknesses", []):
            st.markdown(f'<p class="plain-line">{w}</p>', unsafe_allow_html=True)

    with card():
        st.markdown('<div class="section-title">Tools this job is looking for</div>', unsafe_allow_html=True)
        pills = "".join(f'<span class="pill pill-good">{s} ✓</span>' for s in ev.get("matched_skills", []))
        pills += "".join(f'<span class="pill pill-todo">{s} — not found yet</span>' for s in ev.get("missing_skills", []))
        if pills:
            st.markdown(f'<div>{pills}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="plain-line">We didn\'t find a clear skills list for this job — that\'s okay, we\'ll still help you improve it.</p>', unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back", type="secondary", use_container_width=True):
            go_to(1)
    with col2:
        if st.button("See how to fix this →", type="primary", use_container_width=True):
            go_to(3)


# ── STEP 3 — Ways to improve ──
def render_step3():
    result = st.session_state.pipeline_result
    if not result:
        go_to(1)
        return

    gap = result["gap_analysis"]

    step_header(3, "Here's how to make it stronger")

    priority_map = {
        "High":   ("priority-first", "Worth fixing first"),
        "Medium": ("priority-good", "Good to fix"),
        "Low":    ("priority-nice", "Nice to have"),
    }

    with card():
        st.markdown('<div class="section-title">A few things to fix</div>', unsafe_allow_html=True)
        for g in gap.get("critical_gaps", []):
            cls, label = priority_map.get(g.get("importance", "Medium"), ("priority-good", "Good to fix"))
            st.markdown(f"""
            <div style="margin-bottom:14px">
                <span class="priority-tag {cls}">{label}</span>
                <p style="font-weight:800;font-size:14.5px;margin:0 0 3px">{g.get("gap")}</p>
                <p class="plain-line">{g.get("how_to_fix")}</p>
            </div>
            """, unsafe_allow_html=True)

    with card():
        st.markdown('<div class="section-title">Easy fixes you can make right now</div>', unsafe_allow_html=True)
        for qw in gap.get("quick_wins", []):
            st.markdown(f'<p class="plain-line">✓ {qw}</p>', unsafe_allow_html=True)

    with card():
        st.markdown('<div class="section-title">New project ideas</div>', unsafe_allow_html=True)
        st.markdown('<p class="plain-line">Want us to add project ideas like these to your new resume?</p>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, add them", use_container_width=True,
                         type="primary" if st.session_state.include_projects else "secondary"):
                st.session_state.include_projects = True
                st.rerun()
        with col2:
            if st.button("No, just my resume", use_container_width=True,
                         type="primary" if not st.session_state.include_projects else "secondary"):
                st.session_state.include_projects = False
                st.rerun()

        st.markdown('<div style="height:14px"></div>', unsafe_allow_html=True)
        for p in gap.get("suggested_projects", []):
            tech = " · ".join(p.get("tech_stack", []))
            st.markdown(f"""
            <div class="project-card">
                <div class="project-title">{p.get("title")}</div>
                <p class="project-desc" style="color:var(--ink-soft);font-weight:600">{tech}</p>
                <p class="project-desc">{p.get("description")}</p>
            </div>
            """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back", type="secondary", use_container_width=True, key="back3"):
            go_to(2)
    with col2:
        if st.button("Build my new resume →", type="primary", use_container_width=True):
            with st.spinner("Writing your new resume..."):
                final_resume = write_resume(
                    resume_text=st.session_state.resume_text,
                    parsed_jd=result["parsed_jd"],
                    evaluation=result["evaluation"],
                    gap_analysis=result["gap_analysis"],
                    include_suggested_projects=st.session_state.include_projects
                )
                st.session_state.final_resume = final_resume
            go_to(4)


# ── STEP 4 — Final resume ──
def render_step4():
    final_resume = (st.session_state.final_resume or "").strip()
    if not final_resume:
        go_to(1)
        return

    step_header(4, "Your new resume is ready", "Here's the tailored version — download it whenever you're ready.")

    if st.session_state.final_resume_is_fallback:
        st.warning("The tailored draft came back empty, so this download uses your uploaded resume text instead.")

    with card():
        lines = final_resume.strip().split("\n")
        html = '<div class="resume-preview">'
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                html += "<br/>"
                continue
            is_header = line.startswith("##") or line.isupper() or (len(line) < 40 and line.endswith(":"))
            if i == 0:
                html += f'<div class="resume-name">{line.replace("#", "").strip()}</div>'
            elif i == 1 and any(c in line for c in ["@", "|", "·"]):
                html += f'<div class="resume-contact">{line}</div>'
            elif is_header:
                html += f'<div class="resume-section">{line.replace("##", "").replace(":", "").strip()}</div>'
            elif line.startswith(("•", "-", "*")):
                html += f'<div style="font-size:13.5px;padding:2px 0 2px 16px">• {line.lstrip("•-* ").strip()}</div>'
            else:
                html += f'<div style="font-size:13.5px;padding:2px 0">{line}</div>'
        html += "</div>"
        st.markdown(html, unsafe_allow_html=True)

    docx_bytes = generate_resume_docx(final_resume)
    st.download_button(
        "↓ Download my resume",
        data=docx_bytes,
        file_name="tailored_resume.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
        use_container_width=True
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back", type="secondary", use_container_width=True):
            go_to(3)
    with col2:
        if st.button("Start over with a new job", type="secondary", use_container_width=True):
            restart()


# ── Router ──
steps = {1: render_step1, 2: render_step2, 3: render_step3, 4: render_step4}
steps[st.session_state.step]()