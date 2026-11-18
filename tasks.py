"""
CrewAI Task definitions for the Multi-Agent Job Application Assistant.

Each task is paired with a specific agent and defines:
  - What the agent should do (description)
  - What the expected output looks like (expected_output)
  - Context dependencies (which prior task outputs to use)
"""

from crewai import Task
from agents import (
    create_job_analyzer_agent,
    create_resume_customizer_agent,
    create_linkedin_outreach_agent,
    create_resume_reviewer_agent,
)
from config import Config


def _truncate(text: str | None, max_chars: int) -> str:
    """Trim large text inputs to reduce prompt size/latency while keeping key context."""
    if not text:
        return "N/A"
    value = str(text).strip()
    if len(value) <= max_chars:
        return value
    return value[: max_chars - 40].rstrip() + "\n\n[...truncated for speed...]"


def _format_job_text(job_data: dict) -> str:
    limit = getattr(Config, "MAX_JOB_TEXT_CHARS", 6000)
    return (
        f"Position Title: {job_data.get('title', 'N/A')}\n"
        f"Organization: {job_data.get('organization', 'N/A')}\n"
        f"Department: {job_data.get('department', 'N/A')}\n"
        f"Location: {job_data.get('location', 'N/A')}\n"
        f"Salary: {job_data.get('salary', 'N/A')}\n"
        f"Grade: {job_data.get('grade', 'N/A')}\n"
        f"Job URL: {job_data.get('url', 'N/A')}\n\n"
        f"--- Job Summary ---\n{_truncate(job_data.get('description', 'N/A'), limit)}\n\n"
        f"--- Major Duties ---\n{_truncate(job_data.get('duties', 'N/A'), limit)}\n\n"
        f"--- Qualifications ---\n{_truncate(job_data.get('qualifications', 'N/A'), limit)}\n"
    )


def create_job_analysis_task(job_data: dict) -> tuple[Task, object]:
    """
    Create a task that analyzes a job posting and extracts key requirements.

    Args:
        job_data: Dict with job listing fields (title, description, duties, qualifications, etc.)

    Returns:
        Tuple of (Task, Agent) so the crew can be assembled.
    """
    agent = create_job_analyzer_agent()
    job_text = _format_job_text(job_data)

    task = Task(
        description=(
            "Analyze the following job posting and extract a structured, practical breakdown.\n\n"
            f"JOB POSTING:\n{job_text}\n\n"
            "Your analysis must cover:\n"
            "1. **Required Hard Skills** — technical skills, tools, languages, certifications\n"
            "2. **Required Soft Skills** — communication, leadership, teamwork, etc.\n"
            "3. **Education Requirements** — degrees, fields of study, equivalencies\n"
            "4. **Experience Requirements** — years, types (e.g., federal, supervisory)\n"
            "5. **Key Responsibilities** — the top 5 duties the hire will perform\n"
            "6. **Nice-to-Have Qualifications** — preferred but not required\n"
            "7. **Keywords for ATS** — important terms an applicant should include\n"
            "8. **Cultural/Organizational Fit Indicators** — values, work style\n"
            "9. **Application Tips** — specific advice for standing out for THIS role\n"
        ),
        expected_output=(
            "A comprehensive, well-structured markdown analysis with a brief executive summary "
            "and clearly labeled sections 1-9 using bullet points with specific, actionable details."
        ),
        agent=agent,
    )

    return task, agent


def create_resume_customization_task(
    user_resume: str,
    job_data: dict,
    analysis_task: Task | None = None,
    analysis_output: str | None = None,
) -> tuple[Task, object]:
    """
    Create a task that tailors the user's resume and drafts a cover letter.

    Args:
        user_resume: The user's base resume text.
        job_data: Dict with job listing fields.
        analysis_task: Optional preceding job analysis task (for context chaining).
        analysis_output: Optional analysis text for stepwise execution (preferred when available).

    Returns:
        Tuple of (Task, Agent).
    """
    agent = create_resume_customizer_agent()
    resume_limit = getattr(Config, "MAX_RESUME_CHARS", 12000)
    analysis_text = _truncate(
        analysis_output or (str(analysis_task.output) if analysis_task and getattr(analysis_task, "output", None) else ""),
        getattr(Config, "MAX_JOB_TEXT_CHARS", 6000) * 2,
    )

    analysis_block = ""
    if analysis_text and analysis_text != "N/A":
        analysis_block = f"\nJOB ANALYSIS (from previous step):\n{analysis_text}\n"

    task = Task(
        description=(
            "Using the job analysis (below and/or in task context), customize the candidate's resume "
            f"and write a tailored cover letter for **{job_data.get('title', 'N/A')}** at "
            f"**{job_data.get('organization', 'N/A')}**.\n"
            f"{analysis_block}\n"
            f"CANDIDATE'S BASE RESUME:\n{_truncate(user_resume, resume_limit)}\n\n"
            "Instructions:\n"
            "1. **Tailored Resume**:\n"
            "   - Lead with the most relevant experience for this specific role\n"
            "   - Incorporate ATS keywords identified in the analysis\n"
            "   - Quantify achievements wherever possible (use numbers, percentages)\n"
            "   - Match terminology used in the job posting\n"
            "   - Keep formatting professional and ATS-friendly\n"
            "   - Include a targeted Professional Summary at the top\n\n"
            "2. **Cover Letter**:\n"
            "   - Address the specific organization and position\n"
            "   - Highlight 2-3 key qualifications matching top requirements\n"
            "   - Show relevant impact with a brief example/story\n"
            "   - Show knowledge/fit for the organization\n"
            "   - Keep it concise (under 400 words) and professional\n"
        ),
        expected_output=(
            "Two clearly separated markdown documents:\n\n"
            "## TAILORED RESUME\n"
            "(Complete, ready-to-use resume)\n\n"
            "## COVER LETTER\n"
            "(Complete, ready-to-send cover letter)\n"
        ),
        agent=agent,
        context=[analysis_task] if analysis_task else [],
    )

    return task, agent


def create_linkedin_outreach_task(
    user_resume: str,
    job_data: dict,
    analysis_task: Task | None = None,
    resume_task: Task | None = None,
    analysis_output: str | None = None,
    resume_output: str | None = None,
) -> tuple[Task, object]:
    """
    Create a task that drafts LinkedIn outreach messages.

    Args:
        user_resume: The user's base resume text.
        job_data: Dict with job listing fields.
        analysis_task: Optional job analysis task (for context).
        resume_task: Optional resume customization task (for context).
        analysis_output: Optional analysis text for stepwise execution.
        resume_output: Optional tailored resume/cover letter text for stepwise execution.

    Returns:
        Tuple of (Task, Agent).
    """
    agent = create_linkedin_outreach_agent()
    resume_limit = getattr(Config, "MAX_RESUME_CHARS", 12000)
    job_limit = getattr(Config, "MAX_JOB_TEXT_CHARS", 6000)

    analysis_text = _truncate(
        analysis_output or (str(analysis_task.output) if analysis_task and getattr(analysis_task, "output", None) else ""),
        job_limit * 2,
    )
    tailored_text = _truncate(
        resume_output or (str(resume_task.output) if resume_task and getattr(resume_task, "output", None) else ""),
        job_limit * 2,
    )

    prior_context = ""
    if analysis_text and analysis_text != "N/A":
        prior_context += f"\nJOB ANALYSIS:\n{analysis_text}\n"
    if tailored_text and tailored_text != "N/A":
        prior_context += f"\nTAILORED RESUME & COVER LETTER:\n{tailored_text}\n"

    task = Task(
        description=(
            "Using the job analysis and tailored materials (below and/or in task context), draft personalized "
            f"LinkedIn outreach messages for **{job_data.get('title', 'N/A')}** at "
            f"**{job_data.get('organization', 'N/A')}** "
            f"(Department: {job_data.get('department', 'N/A')}).\n"
            f"{prior_context}\n"
            f"CANDIDATE BACKGROUND SUMMARY:\n{_truncate(user_resume, min(1200, resume_limit))}\n\n"
            "Create the following messages:\n\n"
            "1. **Hiring Manager Message** — interest in the role, aligned experience, specific role aspects\n"
            f"2. **Recruiter Message** — slightly more formal, reference Position ID ({job_data.get('position_id', 'N/A')})\n"
            "3. **Team Member / Informational Interview Request** — softer networking ask for a brief chat\n\n"
            "Each message must include:\n"
            "- A connection request note (under 300 characters)\n"
            "- A follow-up message (under 500 words) for after connection\n"
            "- Personable, professional tone with relevant skills/experience\n"
            "- A clear, low-pressure call to action\n"
        ),
        expected_output=(
            "Three pairs of LinkedIn messages in markdown format:\n\n"
            "## 1. HIRING MANAGER OUTREACH\n"
            "**Connection Request Note** (under 300 chars):\n...\n"
            "**Follow-up Message**:\n...\n\n"
            "## 2. RECRUITER OUTREACH\n"
            "**Connection Request Note** (under 300 chars):\n...\n"
            "**Follow-up Message**:\n...\n\n"
            "## 3. INFORMATIONAL INTERVIEW REQUEST\n"
            "**Connection Request Note** (under 300 chars):\n...\n"
            "**Follow-up Message**:\n...\n\n"
            "All messages should be polished, personalized, and ready to send."
        ),
        agent=agent,
        context=[t for t in (analysis_task, resume_task) if t is not None],
    )

    return task, agent


def create_resume_review_task(user_resume_text: str, job_description_context: str = "") -> tuple[Task, object]:
    """
    Create a task that audits a resume and gives actionable improvement feedback.
    """
    agent = create_resume_reviewer_agent()
    resume_limit = getattr(Config, "MAX_RESUME_CHARS", 12000)
    job_limit = getattr(Config, "MAX_JOB_TEXT_CHARS", 6000)

    context_block = ""
    if job_description_context and job_description_context.strip():
        context_block = (
            "TARGET JOB CONTEXT (if provided):\n"
            f"{_truncate(job_description_context, job_limit * 2)}\n\n"
        )

    task = Task(
        description=(
            "Review the uploaded/base resume thoroughly and provide an honest, actionable audit.\n\n"
            f"RESUME:\n{_truncate(user_resume_text, resume_limit)}\n\n"
            f"{context_block}"
            "Your review MUST cover the following:\n"
            "1. **Overall Verdict & Scorecard** - Markdown table with scores (0-10) for Structure, "
            "Impact of Bullets, ATS Friendliness, Keywords Match, Readability, and Overall. Include a short verdict.\n"
            "2. **Strengths** - 2-4 concrete strengths with examples.\n"
            "3. **Critical Fixes** - Prioritized list (High/Medium/Low) with specific issues and how to fix them.\n"
            "4. **Section-by-Section Review** - Contact, Summary/Profile, Experience, Education, Skills, "
            "Projects/Certifications, and other relevant sections.\n"
            "5. **Bullet Analysis & Rewrites** - 2-5 weak bullets rewritten as strong Action + Context + Impact bullets.\n"
            "6. **ATS Audit** - Formatting/parsing risks, missing/overused keywords.\n"
            "7. **Tailored Suggestions** - If target job context is provided, suggest exact keywords/phrases and where to add them; "
            "otherwise give general best-practice suggestions.\n"
            "8. **Action Plan** - 'Do Today (Quick Wins)' and 'This Week (Bigger Improvements)'.\n"
            "9. **Final Checklist** - A checklist to use before applying.\n\n"
            "Be specific and actionable. Focus on changes that will move the needle."
        ),
        expected_output=(
            "A clean markdown report containing: Resume Review Scorecard table, Strengths, Critical Fixes, "
            "Suggested Rewrites (Before -> After), ATS Audit, Action Plan, and Final Checklist."
        ),
        agent=agent,
    )

    return task, agent
