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

    job_text = (
        f"Position Title: {job_data.get('title', 'N/A')}\n"
        f"Organization: {job_data.get('organization', 'N/A')}\n"
        f"Department: {job_data.get('department', 'N/A')}\n"
        f"Location: {job_data.get('location', 'N/A')}\n"
        f"Salary: {job_data.get('salary', 'N/A')}\n"
        f"Grade: {job_data.get('grade', 'N/A')}\n"
        f"Job URL: {job_data.get('url', 'N/A')}\n\n"
        f"--- Job Summary ---\n{job_data.get('description', 'N/A')}\n\n"
        f"--- Major Duties ---\n{job_data.get('duties', 'N/A')}\n\n"
        f"--- Qualifications ---\n{job_data.get('qualifications', 'N/A')}\n"
    )

    task = Task(
        description=(
            f"Analyze the following job posting in detail and extract a structured "
            f"breakdown of all requirements.\n\n"
            f"JOB POSTING:\n{job_text}\n\n"
            f"Your analysis should cover:\n"
            f"1. **Required Hard Skills** — technical skills, tools, languages, certifications\n"
            f"2. **Required Soft Skills** — communication, leadership, teamwork, etc.\n"
            f"3. **Education Requirements** — degrees, fields of study, equivalencies\n"
            f"4. **Experience Requirements** — years, types (e.g., federal, supervisory)\n"
            f"5. **Key Responsibilities** — the top 5 duties the hire will perform\n"
            f"6. **Nice-to-Have Qualifications** — preferred but not required\n"
            f"7. **Keywords for ATS** — important terms an applicant should include\n"
            f"8. **Cultural/Organizational Fit Indicators** — values, work style\n"
            f"9. **Application Tips** — specific advice for standing out for THIS role\n"
        ),
        expected_output=(
            "A comprehensive, well-structured analysis report in markdown format "
            "with clearly labeled sections for each of the 9 categories above. "
            "Each section should contain bullet points with specific, actionable details "
            "extracted from the job posting. Include a brief executive summary at the top."
        ),
        agent=agent,
    )

    return task, agent


def create_resume_customization_task(
    user_resume: str,
    job_data: dict,
    analysis_task: Task,
) -> tuple[Task, object]:
    """
    Create a task that tailors the user's resume and drafts a cover letter.

    Args:
        user_resume: The user's base resume text.
        job_data: Dict with job listing fields.
        analysis_task: The preceding job analysis task (for context chaining).

    Returns:
        Tuple of (Task, Agent).
    """
    agent = create_resume_customizer_agent()

    task = Task(
        description=(
            f"Using the job analysis provided by the Job Analyzer (available in your "
            f"context), customize the candidate's resume and write a tailored cover "
            f"letter for the position of **{job_data.get('title', 'N/A')}** at "
            f"**{job_data.get('organization', 'N/A')}**.\n\n"
            f"CANDIDATE'S BASE RESUME:\n{user_resume}\n\n"
            f"Instructions:\n"
            f"1. **Tailored Resume**: Rewrite/restructure the resume to:\n"
            f"   - Lead with the most relevant experience for this specific role\n"
            f"   - Incorporate ATS keywords identified in the analysis\n"
            f"   - Quantify achievements wherever possible (use numbers, percentages)\n"
            f"   - Match the terminology used in the job posting\n"
            f"   - Keep it to a professional format suitable for federal applications\n"
            f"   - Include a targeted Professional Summary at the top\n\n"
            f"2. **Cover Letter**: Write a compelling cover letter that:\n"
            f"   - Addresses the specific organization and position\n"
            f"   - Highlights 2-3 key qualifications that match the top requirements\n"
            f"   - Tells a brief story showing relevant impact\n"
            f"   - Shows knowledge of the agency/organization\n"
            f"   - Is concise (under 400 words) and professional\n"
        ),
        expected_output=(
            "Two clearly separated documents in markdown format:\n\n"
            "## TAILORED RESUME\n"
            "(Complete, ready-to-use resume formatted for the target position)\n\n"
            "## COVER LETTER\n"
            "(Complete, ready-to-send cover letter addressed to the hiring organization)\n\n"
            "Both documents should be polished, professional, and immediately usable."
        ),
        agent=agent,
        context=[analysis_task],
    )

    return task, agent


def create_linkedin_outreach_task(
    user_resume: str,
    job_data: dict,
    analysis_task: Task,
    resume_task: Task,
) -> tuple[Task, object]:
    """
    Create a task that drafts LinkedIn outreach messages.

    Args:
        user_resume: The user's base resume text.
        job_data: Dict with job listing fields.
        analysis_task: The job analysis task (for context).
        resume_task: The resume customization task (for context).

    Returns:
        Tuple of (Task, Agent).
    """
    agent = create_linkedin_outreach_agent()

    task = Task(
        description=(
            f"Based on the job analysis and customized resume (available in your "
            f"context), draft personalized LinkedIn outreach messages for the "
            f"position of **{job_data.get('title', 'N/A')}** at "
            f"**{job_data.get('organization', 'N/A')}** "
            f"(Department: {job_data.get('department', 'N/A')}).\n\n"
            f"CANDIDATE BACKGROUND SUMMARY:\n{user_resume[:1000]}\n\n"
            f"Create the following messages:\n\n"
            f"1. **Hiring Manager Message** — A message to the hiring manager or "
            f"   team lead expressing interest in the role. Should reference specific "
            f"   aspects of the position and how the candidate's experience aligns.\n\n"
            f"2. **Recruiter Message** — A message to an HR recruiter or talent "
            f"   acquisition specialist at the organization. Should be slightly more "
            f"   formal and reference the position ID ({job_data.get('position_id', 'N/A')}).\n\n"
            f"3. **Team Member / Informational Interview Request** — A softer, "
            f"   networking-focused message to someone currently working in a similar "
            f"   role at the organization, requesting a brief informational conversation.\n\n"
            f"Each message should:\n"
            f"- Be under 300 characters for the connection request note\n"
            f"- Include a follow-up message (under 500 words) for after connection\n"
            f"- Be personable yet professional\n"
            f"- Reference specific relevant skills or experiences\n"
            f"- Include a clear, low-pressure call to action\n"
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
        context=[analysis_task, resume_task],
    )

    return task, agent
