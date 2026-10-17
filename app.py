"""
Streamlit Web Application — Multi-Agent Job Application Assistant

A premium, modern UI for searching government jobs, selecting positions,
and generating AI-powered application materials via CrewAI agents.
"""

import streamlit as st
import time
import traceback
from config import Config
from usajobs_client import USAJobsClient
from crew import run_job_application_crew
from logger import ApplicationLogger


# ─────────────────────────────────────────────────────────
# Page Configuration
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Job Application Assistant",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', sans-serif;
    }

    /* ── Hero header ── */
    .hero-container {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 50%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.05); opacity: 1; }
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        position: relative;
        z-index: 1;
    }
    .hero-subtitle {
        color: #cbd5e1;
        font-size: 1.05rem;
        margin-top: 0.5rem;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }

    /* ── Job cards ── */
    .job-card {
        background: linear-gradient(145deg, #1e1b4b 0%, #312e81 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    .job-card:hover {
        border-color: rgba(139, 92, 246, 0.7);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(139, 92, 246, 0.2);
    }
    .job-card::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #34d399);
        border-radius: 16px 16px 0 0;
    }
    .job-title {
        font-size: 1.2rem;
        font-weight: 700;
        color: #e0e7ff;
        margin-bottom: 0.3rem;
    }
    .job-org {
        font-size: 0.95rem;
        color: #a78bfa;
        font-weight: 500;
        margin-bottom: 0.8rem;
    }
    .job-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-bottom: 0.8rem;
    }
    .job-tag {
        background: rgba(99, 102, 241, 0.15);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #c4b5fd;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .job-description {
        color: #94a3b8;
        font-size: 0.88rem;
        line-height: 1.6;
        margin-top: 0.5rem;
    }

    /* ── Stats pills ── */
    .stat-pill {
        background: linear-gradient(135deg, #312e81, #1e1b4b);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }
    .stat-number {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label {
        color: #94a3b8;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 0.3rem;
    }

    /* ── Section headers ── */
    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #e0e7ff;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid rgba(139, 92, 246, 0.3);
    }

    /* ── Agent pipeline ── */
    .agent-pipeline {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    .agent-step {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        text-align: center;
        min-width: 180px;
    }
    .agent-step-active {
        border-color: #34d399;
        box-shadow: 0 0 15px rgba(52, 211, 153, 0.3);
    }
    .agent-step-icon {
        font-size: 1.8rem;
        margin-bottom: 0.3rem;
    }
    .agent-step-name {
        color: #e0e7ff;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .agent-arrow {
        color: #6366f1;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
    }

    /* ── Output tabs ── */
    .output-section {
        background: linear-gradient(145deg, #0f172a, #1e1b4b);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-top: 1rem;
    }

    /* ── Log entry ── */
    .log-entry {
        background: rgba(30, 27, 75, 0.6);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
    }
    .log-entry-title {
        color: #e0e7ff;
        font-weight: 600;
        font-size: 1rem;
    }
    .log-entry-meta {
        color: #64748b;
        font-size: 0.82rem;
        margin-top: 0.3rem;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29 0%, #1e1b4b 100%);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e7ff;
    }

    /* ── Status badge ── */
    .status-badge {
        display: inline-block;
        background: rgba(52, 211, 153, 0.15);
        color: #34d399;
        border: 1px solid rgba(52, 211, 153, 0.3);
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* ── Hide default streamlit cruft ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────
# Session State Initialization
# ─────────────────────────────────────────────────────────
if "jobs" not in st.session_state:
    st.session_state.jobs = []
if "total_jobs" not in st.session_state:
    st.session_state.total_jobs = 0
if "selected_job" not in st.session_state:
    st.session_state.selected_job = None
if "crew_output" not in st.session_state:
    st.session_state.crew_output = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "page" not in st.session_state:
    st.session_state.page = "search"


# ─────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🧭 Navigation")

    nav_search = st.button("🔍  Search Jobs", use_container_width=True, key="nav_search")
    nav_generate = st.button("⚡  Generate Materials", use_container_width=True, key="nav_generate")
    nav_history = st.button("📋  Application History", use_container_width=True, key="nav_history")

    if nav_search:
        st.session_state.page = "search"
    if nav_generate:
        st.session_state.page = "generate"
    if nav_history:
        st.session_state.page = "history"

    st.markdown("---")
    st.markdown("### 📝 Your Resume")
    st.caption("Paste your base resume below. This will be used by the AI agents to tailor your application materials.")
    user_resume = st.text_area(
        "Resume Content",
        height=250,
        placeholder="Paste your full resume here...\n\nInclude your work experience, skills, education, and any relevant certifications.",
        label_visibility="collapsed",
        key="user_resume",
    )

    st.markdown("---")

    # Config status
    missing = Config.validate()
    if missing:
        st.error(f"⚠️ Missing config: {', '.join(missing)}")
        st.caption("Create a `.env` file from `.env.example` and fill in your API keys.")
    else:
        st.success("✅ All API keys configured")

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#64748b;font-size:0.75rem;'>"
        "Built with CrewAI • Google Gemini • Streamlit<br>"
        "Multi-Agent Job Application Assistant"
        "</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-container">
    <h1 class="hero-title">🚀 AI Job Application Assistant</h1>
    <p class="hero-subtitle">
        Multi-agent AI system powered by CrewAI & Google Gemini — Analyze job postings,
        tailor your resume, and draft LinkedIn outreach in one click.
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# Agent Pipeline Visualization
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="agent-pipeline">
    <div class="agent-step">
        <div class="agent-step-icon">🔬</div>
        <div class="agent-step-name">Job Analyzer</div>
    </div>
    <div class="agent-arrow">→</div>
    <div class="agent-step">
        <div class="agent-step-icon">📄</div>
        <div class="agent-step-name">Resume Customizer</div>
    </div>
    <div class="agent-arrow">→</div>
    <div class="agent-step">
        <div class="agent-step-icon">💬</div>
        <div class="agent-step-name">LinkedIn Outreach</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
# PAGE: Search Jobs
# ═════════════════════════════════════════════════════════
if st.session_state.page == "search":
    st.markdown('<div class="section-header">🔍 Search Government Job Listings</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        keyword = st.text_input(
            "🔑 Keyword",
            placeholder="e.g., Data Scientist, Software Engineer, Cybersecurity",
            key="search_keyword",
        )
    with col2:
        location = st.text_input(
            "📍 Location",
            placeholder="e.g., Washington, DC or Remote",
            key="search_location",
        )
    with col3:
        num_results = st.selectbox(
            "📊 Results",
            options=[10, 25, 50],
            index=1,
            key="num_results",
        )

    search_btn = st.button("🚀 Search USAJobs", type="primary", use_container_width=True, key="search_btn")

    if search_btn:
        if not keyword.strip():
            st.warning("Please enter a search keyword.")
        elif Config.validate():
            st.error("Please configure your API keys first (see sidebar).")
        else:
            with st.spinner("🔍 Fetching jobs from USAJobs.gov..."):
                try:
                    client = USAJobsClient()
                    jobs, total = client.fetch_and_parse(
                        keyword=keyword.strip(),
                        location=location.strip(),
                        results_per_page=num_results,
                    )
                    st.session_state.jobs = jobs
                    st.session_state.total_jobs = total
                    st.success(f"✅ Found **{total}** jobs! Showing top {len(jobs)} results.")
                except Exception as e:
                    st.error(f"❌ API Error: {str(e)}")

    # Display results
    if st.session_state.jobs:
        # Stats
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            st.markdown(f"""
            <div class="stat-pill">
                <div class="stat-number">{st.session_state.total_jobs}</div>
                <div class="stat-label">Total Matches</div>
            </div>
            """, unsafe_allow_html=True)
        with col_s2:
            st.markdown(f"""
            <div class="stat-pill">
                <div class="stat-number">{len(st.session_state.jobs)}</div>
                <div class="stat-label">Displayed</div>
            </div>
            """, unsafe_allow_html=True)
        with col_s3:
            unique_orgs = len(set(j["organization"] for j in st.session_state.jobs))
            st.markdown(f"""
            <div class="stat-pill">
                <div class="stat-number">{unique_orgs}</div>
                <div class="stat-label">Organizations</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("")

        # Job cards
        for i, job in enumerate(st.session_state.jobs):
            desc_preview = (job['description'][:200] + '...') if len(job.get('description', '')) > 200 else job.get('description', 'N/A')

            st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{job['title']}</div>
                <div class="job-org">{job['organization']} — {job['department']}</div>
                <div class="job-meta">
                    <span class="job-tag">📍 {job['location']}</span>
                    <span class="job-tag">💰 {job['salary']}</span>
                    <span class="job-tag">📊 Grade: {job['grade']}</span>
                </div>
                <div class="job-description">{desc_preview}</div>
            </div>
            """, unsafe_allow_html=True)

            col_sel, col_link = st.columns([1, 1])
            with col_sel:
                if st.button(f"⚡ Select for AI Processing", key=f"select_{i}", use_container_width=True):
                    st.session_state.selected_job = job
                    st.session_state.page = "generate"
                    st.rerun()
            with col_link:
                if job.get("url") and job["url"] != "N/A":
                    st.link_button("🔗 View on USAJobs", job["url"], use_container_width=True)


# ═════════════════════════════════════════════════════════
# PAGE: Generate Materials
# ═════════════════════════════════════════════════════════
elif st.session_state.page == "generate":
    st.markdown('<div class="section-header">⚡ Generate Application Materials</div>', unsafe_allow_html=True)

    job = st.session_state.selected_job

    if not job:
        st.info("👈 Please search for jobs and select one first, or paste a job description below for manual entry.")

        st.markdown("#### Manual Job Entry")
        manual_col1, manual_col2 = st.columns(2)
        with manual_col1:
            manual_title = st.text_input("Position Title", key="manual_title")
            manual_org = st.text_input("Organization", key="manual_org")
            manual_location = st.text_input("Location", key="manual_location")
        with manual_col2:
            manual_salary = st.text_input("Salary Range", key="manual_salary")
            manual_dept = st.text_input("Department", key="manual_dept")
            manual_url = st.text_input("Job URL (optional)", key="manual_url")

        manual_description = st.text_area("Job Description / Summary", height=150, key="manual_desc")
        manual_duties = st.text_area("Major Duties", height=150, key="manual_duties")
        manual_quals = st.text_area("Qualifications", height=150, key="manual_quals")

        if st.button("✅ Use This Job", type="primary", key="use_manual"):
            if manual_title and manual_description:
                st.session_state.selected_job = {
                    "title": manual_title,
                    "organization": manual_org or "N/A",
                    "department": manual_dept or "N/A",
                    "location": manual_location or "N/A",
                    "salary": manual_salary or "N/A",
                    "grade": "N/A",
                    "url": manual_url or "N/A",
                    "description": manual_description,
                    "duties": manual_duties or "N/A",
                    "qualifications": manual_quals or "N/A",
                    "position_id": "MANUAL",
                }
                st.rerun()
            else:
                st.warning("Please fill in at least the Position Title and Job Description.")

    else:
        # Show selected job
        st.markdown(f"""
        <div class="job-card">
            <div class="job-title">📌 Selected: {job['title']}</div>
            <div class="job-org">{job['organization']} — {job.get('department', 'N/A')}</div>
            <div class="job-meta">
                <span class="job-tag">📍 {job['location']}</span>
                <span class="job-tag">💰 {job['salary']}</span>
                <span class="job-tag">📊 Grade: {job.get('grade', 'N/A')}</span>
                <span class="status-badge">SELECTED</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("❌ Clear Selection", key="clear_job"):
            st.session_state.selected_job = None
            st.session_state.crew_output = None
            st.rerun()

        st.markdown("---")

        # Pre-flight checks
        resume_text = st.session_state.get("user_resume", "").strip()
        can_run = True

        if not resume_text:
            st.warning("📝 Please paste your resume in the sidebar before generating materials.")
            can_run = False

        if Config.validate():
            st.error(f"🔑 Missing API keys: {', '.join(Config.validate())}")
            can_run = False

        # Generate button
        if can_run:
            generate_btn = st.button(
                "🚀 Launch AI Agent Pipeline",
                type="primary",
                use_container_width=True,
                disabled=st.session_state.is_running,
                key="generate_btn",
            )

            if generate_btn:
                st.session_state.is_running = True

                # Progress visualization
                progress_container = st.container()
                with progress_container:
                    st.markdown("""
                    <div class="agent-pipeline">
                        <div class="agent-step agent-step-active">
                            <div class="agent-step-icon">🔬</div>
                            <div class="agent-step-name">Running...</div>
                        </div>
                        <div class="agent-arrow">→</div>
                        <div class="agent-step">
                            <div class="agent-step-icon">📄</div>
                            <div class="agent-step-name">Waiting...</div>
                        </div>
                        <div class="agent-arrow">→</div>
                        <div class="agent-step">
                            <div class="agent-step-icon">💬</div>
                            <div class="agent-step-name">Waiting...</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    progress_bar = st.progress(0, text="🔬 Agent 1/3: Analyzing job description...")

                    try:
                        # Run the crew
                        progress_bar.progress(10, text="🔬 Agent 1/3: Analyzing job description...")

                        outputs = run_job_application_crew(
                            job_data=job,
                            user_resume=resume_text,
                        )

                        progress_bar.progress(100, text="✅ All agents completed!")
                        time.sleep(0.5)

                        st.session_state.crew_output = outputs

                        # Log the application
                        logger = ApplicationLogger()
                        app_id = logger.log_application(job, outputs)
                        st.success(f"✅ Application materials generated and saved! (ID: {app_id})")

                    except Exception as e:
                        st.error(f"❌ Error during agent execution: {str(e)}")
                        st.code(traceback.format_exc())

                    finally:
                        st.session_state.is_running = False

        # Display outputs
        if st.session_state.crew_output:
            outputs = st.session_state.crew_output

            st.markdown('<div class="section-header">📊 Generated Materials</div>', unsafe_allow_html=True)

            tab_analysis, tab_resume, tab_linkedin, tab_full = st.tabs([
                "🔬 Job Analysis",
                "📄 Resume & Cover Letter",
                "💬 LinkedIn Messages",
                "📋 Full Output",
            ])

            with tab_analysis:
                st.markdown('<div class="output-section">', unsafe_allow_html=True)
                st.markdown(outputs.get("analysis", "No analysis generated."))
                st.markdown('</div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download Analysis",
                    outputs.get("analysis", ""),
                    file_name="job_analysis.md",
                    mime="text/markdown",
                    key="dl_analysis",
                )

            with tab_resume:
                st.markdown('<div class="output-section">', unsafe_allow_html=True)
                st.markdown(outputs.get("resume_cover_letter", "No resume/cover letter generated."))
                st.markdown('</div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download Resume & Cover Letter",
                    outputs.get("resume_cover_letter", ""),
                    file_name="tailored_resume_cover_letter.md",
                    mime="text/markdown",
                    key="dl_resume",
                )

            with tab_linkedin:
                st.markdown('<div class="output-section">', unsafe_allow_html=True)
                st.markdown(outputs.get("linkedin_messages", "No LinkedIn messages generated."))
                st.markdown('</div>', unsafe_allow_html=True)
                st.download_button(
                    "⬇️ Download LinkedIn Messages",
                    outputs.get("linkedin_messages", ""),
                    file_name="linkedin_outreach.md",
                    mime="text/markdown",
                    key="dl_linkedin",
                )

            with tab_full:
                st.markdown('<div class="output-section">', unsafe_allow_html=True)
                st.markdown(outputs.get("full_output", "No output."))
                st.markdown('</div>', unsafe_allow_html=True)


# ═════════════════════════════════════════════════════════
# PAGE: Application History
# ═════════════════════════════════════════════════════════
elif st.session_state.page == "history":
    st.markdown('<div class="section-header">📋 Application History</div>', unsafe_allow_html=True)

    logger = ApplicationLogger()
    applications = logger.get_all_applications()

    if not applications:
        st.info("No applications logged yet. Generate your first application materials to see them here!")
    else:
        st.markdown(f"**{len(applications)}** application(s) on record")

        for app in reversed(applications):
            st.markdown(f"""
            <div class="log-entry">
                <div class="log-entry-title">
                    {app.get('job_title', 'N/A')} — {app.get('organization', 'N/A')}
                </div>
                <div class="log-entry-meta">
                    📍 {app.get('location', 'N/A')} &nbsp;|&nbsp;
                    💰 {app.get('salary', 'N/A')} &nbsp;|&nbsp;
                    🕐 {app.get('timestamp', 'N/A')[:19]} &nbsp;|&nbsp;
                    <span class="status-badge">{app.get('status', 'N/A').upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Show saved files
            files_saved = app.get("files_saved", {})
            if files_saved:
                with st.expander(f"📂 View saved materials — {app.get('app_id', '')}", expanded=False):
                    for file_key, filepath in files_saved.items():
                        content = logger.load_saved_output(filepath)
                        st.markdown(f"**{file_key.replace('_', ' ').title()}**")
                        st.markdown(content)
                        st.download_button(
                            f"⬇️ Download {file_key}",
                            content,
                            file_name=f"{app.get('app_id', 'output')}_{file_key}.md",
                            mime="text/markdown",
                            key=f"dl_{app.get('app_id', '')}_{file_key}",
                        )
                        st.markdown("---")
