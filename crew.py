"""
Crew orchestration for the Multi-Agent Job Application Assistant.

Runs the pipeline step-by-step for better performance visibility and progress reporting:
  Job Analysis → Resume Customization → LinkedIn Outreach
"""

import time
from collections.abc import Callable

from crewai import Crew, LLM, Process
from tasks import (
    create_job_analysis_task,
    create_resume_customization_task,
    create_linkedin_outreach_task,
    create_resume_review_task,
)
from config import Config


def _notify_progress(progress_callback: Callable[[int, int, str], None] | None, step: int, total: int, label: str) -> None:
    if progress_callback:
        try:
            progress_callback(step, total, label)
        except Exception:
            # Progress updates should never break the pipeline.
            pass


_RETRYABLE_ERROR_TOKENS = (
    "503",
    "UNAVAILABLE",
    "HIGH DEMAND",
    "404",
    "NOT_FOUND",
    "429",
    "RATE LIMITED",
    "TOO MANY REQUESTS",
)


def _is_retryable_error(error: Exception) -> bool:
    """Identify transient capacity errors or retired/unavailable model errors."""
    message = str(error).upper()
    return any(token in message for token in _RETRYABLE_ERROR_TOKENS)


def _run_single_task(task, agent):
    """
    Execute a single task with a single-agent crew and return string output.

    On transient model errors, retries across the configured fallback models with
    exponential backoff so a temporary 503 on one model does not fail the pipeline.
    """
    def _kickoff():
        crew = Crew(
            agents=[agent],
            tasks=[task],
            process=Process.sequential,
            verbose=Config.CREW_VERBOSE,
        )
        result = crew.kickoff()
        return str(task.output) if getattr(task, "output", None) else str(result)

    try:
        return _kickoff()
    except Exception as original_error:
        if not _is_retryable_error(original_error):
            raise

        last_error = original_error
        for model in Config.GEMINI_FALLBACK_MODELS:
            for attempt in range(Config.GEMINI_FALLBACK_RETRIES):
                try:
                    agent.llm = LLM(
                        model=model,
                        temperature=0.7,
                        api_key=Config.GEMINI_API_KEY,
                    )
                    return _kickoff()
                except Exception as retry_error:
                    last_error = retry_error
                    if not _is_retryable_error(retry_error):
                        raise
                    if attempt < Config.GEMINI_FALLBACK_RETRIES - 1:
                        time.sleep(Config.GEMINI_RETRY_DELAY_SECONDS * (2 ** attempt))

        raise last_error


def run_job_application_crew(
    job_data: dict,
    user_resume: str,
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> dict:
    """
    Orchestrate the full multi-agent pipeline for a given job and resume.

    Runs each step sequentially in its own crew so callers can update progress between steps.

    Args:
        job_data: Parsed job listing dict.
        user_resume: The user's base resume as a text string.
        progress_callback: Optional callable(step, total_steps, label) for UI progress updates.

    Returns:
        Dict with keys: 'analysis', 'resume_cover_letter', 'linkedin_messages', 'full_output'.
    """
    total_steps = 3

    # Step 1: Job analysis
    _notify_progress(progress_callback, 1, total_steps, "Analyzing job description...")
    analysis_task, analyzer_agent = create_job_analysis_task(job_data)
    analysis_output = _run_single_task(analysis_task, analyzer_agent)

    # Step 2: Resume + cover letter (uses analysis output)
    _notify_progress(progress_callback, 2, total_steps, "Tailoring resume and drafting cover letter...")
    resume_task, resume_agent = create_resume_customization_task(
        user_resume=user_resume,
        job_data=job_data,
        analysis_task=analysis_task,
        analysis_output=analysis_output,
    )
    resume_output = _run_single_task(resume_task, resume_agent)

    # Step 3: LinkedIn outreach (uses analysis + tailored materials)
    _notify_progress(progress_callback, 3, total_steps, "Drafting LinkedIn outreach messages...")
    linkedin_task, linkedin_agent = create_linkedin_outreach_task(
        user_resume=user_resume,
        job_data=job_data,
        analysis_task=analysis_task,
        resume_task=resume_task,
        analysis_output=analysis_output,
        resume_output=resume_output,
    )
    linkedin_output = _run_single_task(linkedin_task, linkedin_agent)

    _notify_progress(progress_callback, 3, total_steps, "Completed all steps.")

    outputs = {
        "analysis": analysis_output or "",
        "resume_cover_letter": resume_output or "",
        "linkedin_messages": linkedin_output or "",
        "full_output": (
            "## Job Analysis\n\n"
            f"{analysis_output}\n\n"
            "## Resume & Cover Letter\n\n"
            f"{resume_output}\n\n"
            "## LinkedIn Outreach\n\n"
            f"{linkedin_output}"
        ),
    }

    return outputs


def run_resume_review_crew(user_resume_text: str, job_data: dict | None = None) -> dict:
    """
    Run a standalone resume review crew with the Resume Reviewer agent.
    """
    jd_context = ""
    if job_data:
        jd_context = (
            f"Position Title: {job_data.get('title', 'N/A')}\n"
            f"Organization: {job_data.get('organization', 'N/A')}\n"
            f"Department: {job_data.get('department', 'N/A')}\n"
            f"Location: {job_data.get('location', 'N/A')}\n\n"
            f"--- Job Summary ---\n{job_data.get('description', 'N/A')}\n\n"
            f"--- Major Duties ---\n{job_data.get('duties', 'N/A')}\n\n"
            f"--- Qualifications ---\n{job_data.get('qualifications', 'N/A')}\n"
        )

    review_task, reviewer_agent = create_resume_review_task(user_resume_text, jd_context)

    try:
        review_output = _run_single_task(review_task, reviewer_agent)
        return {
            "review": review_output,
            "full_output": review_output,
        }
    except Exception as e:
        return {
            "review": f"Error: {e}",
            "full_output": f"Error: {e}",
        }
