"""
Crew orchestration for the Multi-Agent Job Application Assistant.

Assembles agents and tasks into a CrewAI Crew that runs sequentially:
  Job Analysis → Resume Customization → LinkedIn Outreach
"""

from crewai import Crew, Process
from tasks import (
    create_job_analysis_task,
    create_resume_customization_task,
    create_linkedin_outreach_task,
)


def run_job_application_crew(
    job_data: dict,
    user_resume: str,
) -> dict:
    """
    Orchestrate the full multi-agent pipeline for a given job and resume.

    Args:
        job_data: Parsed job listing dict (from USAJobs client).
        user_resume: The user's base resume as a text string.

    Returns:
        Dict with keys: 'analysis', 'resume_cover_letter', 'linkedin_messages',
        each containing the string output of the respective agent.
    """
    # --- Step 1: Create tasks (with their agents) ---
    analysis_task, analyzer_agent = create_job_analysis_task(job_data)

    resume_task, resume_agent = create_resume_customization_task(
        user_resume=user_resume,
        job_data=job_data,
        analysis_task=analysis_task,
    )

    linkedin_task, linkedin_agent = create_linkedin_outreach_task(
        user_resume=user_resume,
        job_data=job_data,
        analysis_task=analysis_task,
        resume_task=resume_task,
    )

    # --- Step 2: Assemble the Crew ---
    crew = Crew(
        agents=[analyzer_agent, resume_agent, linkedin_agent],
        tasks=[analysis_task, resume_task, linkedin_task],
        process=Process.sequential,
        verbose=True,
    )

    # --- Step 3: Kickoff ---
    result = crew.kickoff()

    # --- Step 4: Collect individual task outputs ---
    outputs = {
        "analysis": str(analysis_task.output) if analysis_task.output else "",
        "resume_cover_letter": str(resume_task.output) if resume_task.output else "",
        "linkedin_messages": str(linkedin_task.output) if linkedin_task.output else "",
        "full_output": str(result),
    }

    return outputs
