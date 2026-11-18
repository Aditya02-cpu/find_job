"""
CrewAI Agent definitions for the Multi-Agent Job Application Assistant.

Four specialized agents collaborate:
  1. Job Analyzer Agent — extracts key requirements from job listings.
  2. Resume Customizer Agent — tailors resume and cover letter to the job.
  3. LinkedIn Outreach Agent — drafts personalized outreach messages.
  4. Resume Reviewer Agent — audits resumes and gives actionable improvement advice.
"""

from threading import Lock

from crewai import Agent, LLM
from config import Config

_shared_llm: LLM | None = None
_llm_lock = Lock()


def _get_llm() -> LLM:
    """Create/reuse a shared Gemini LLM instance for all agents to reduce startup overhead."""
    global _shared_llm
    if _shared_llm is not None:
        return _shared_llm

    with _llm_lock:
        if _shared_llm is not None:
            return _shared_llm

        kwargs = {
            "model": Config.GEMINI_MODEL,
            "temperature": 0.7,
            "api_key": Config.GEMINI_API_KEY,
        }

        # Gemini 2.5+ auto-enables "thinking" in newer CrewAI providers, which can slow responses.
        # Disable/minimize it by default for this pipeline (configurable via env vars).
        model_lower = (Config.GEMINI_MODEL or "").lower()
        if "gemini" in model_lower:
            try:
                from google.genai import types

                budget = max(int(getattr(Config, "GEMINI_THINKING_BUDGET", 0)), 0)
                include_thoughts = bool(getattr(Config, "GEMINI_INCLUDE_THOUGHTS", False))
                # Pass via both names for provider compatibility.
                thinking_cfg = types.ThinkingConfig(
                    thinking_budget=budget,
                    include_thoughts=include_thoughts,
                )
                kwargs["thinking_config"] = thinking_cfg
                kwargs["additional_params"] = {"thinking_config": thinking_cfg}
            except Exception:
                # If google-genai types are unavailable, proceed without explicit thinking config.
                pass

        _shared_llm = LLM(**kwargs)
        return _shared_llm


def reset_shared_llm() -> None:
    """Reset cached LLM (useful if config/model changes at runtime)."""
    global _shared_llm
    with _llm_lock:
        _shared_llm = None


def create_job_analyzer_agent() -> Agent:
    """
    Creates the Job Analyzer agent.

    This agent reads a job posting and extracts structured data:
    required skills, qualifications, experience level, key responsibilities,
    and cultural fit indicators.
    """
    return Agent(
        role="Senior Job Description Analyst",
        goal=(
            "Thoroughly analyze job postings to extract every critical requirement, "
            "skill, qualification, and responsibility so the applicant knows exactly "
            "what the employer is looking for and can tailor their materials accordingly."
        ),
        backstory=(
            "You are a veteran HR consultant and technical recruiter with 15+ years "
            "of experience reviewing thousands of job descriptions across government "
            "agencies and private sector companies. You have an exceptional eye for "
            "distinguishing must-have qualifications from nice-to-haves, identifying "
            "hidden requirements between the lines, and understanding what hiring "
            "managers truly prioritize. Your analyses have helped hundreds of "
            "candidates successfully land their dream positions."
        ),
        llm=_get_llm(),
        verbose=Config.CREW_VERBOSE,
        memory=Config.AGENT_MEMORY_ENABLED,
        max_iter=Config.AGENT_MAX_ITER,
        allow_delegation=False,
    )


def create_resume_customizer_agent() -> Agent:
    """
    Creates the Resume Customizer agent.

    This agent takes the job analysis and the user's base resume,
    then produces a tailored resume and cover letter.
    """
    return Agent(
        role="Expert Resume Writer & Career Strategist",
        goal=(
            "Create a perfectly tailored, ATS-optimized resume and a compelling "
            "cover letter that highlights the candidate's most relevant experience "
            "and skills for the specific position, maximizing their chances of "
            "getting past automated screening and impressing hiring managers."
        ),
        backstory=(
            "You are a certified professional resume writer (CPRW) and career "
            "coach who has helped over 500 professionals successfully transition "
            "into new roles. You specialize in federal government applications and "
            "understand the nuances of KSAs (Knowledge, Skills, and Abilities), "
            "GS pay scales, and how to translate private-sector experience into "
            "government-friendly language. You are also an expert in ATS "
            "(Applicant Tracking System) optimization, keyword density, and "
            "modern resume formatting best practices."
        ),
        llm=_get_llm(),
        verbose=Config.CREW_VERBOSE,
        memory=Config.AGENT_MEMORY_ENABLED,
        max_iter=Config.AGENT_MAX_ITER,
        allow_delegation=False,
    )


def create_linkedin_outreach_agent() -> Agent:
    """
    Creates the LinkedIn Outreach agent.

    This agent drafts professional, personalized LinkedIn messages
    for networking and job inquiries.
    """
    return Agent(
        role="Professional Networking & LinkedIn Outreach Specialist",
        goal=(
            "Craft personalized, professional, and engaging LinkedIn messages "
            "that open doors to meaningful connections with hiring managers, "
            "recruiters, and team leads at target organizations, increasing "
            "the candidate's visibility and chances of referral."
        ),
        backstory=(
            "You are a LinkedIn Top Voice in career development and a networking "
            "strategist who has personally helped professionals build connections "
            "that led to job offers. You understand the psychology of cold outreach, "
            "the art of being personable without being pushy, and how to craft "
            "messages that get responses. You tailor every message based on the "
            "recipient's background, the job requirements, and the candidate's "
            "unique value proposition. Your messages have an above-average response "
            "rate because they are genuine, concise, and value-driven."
        ),
        llm=_get_llm(),
        verbose=Config.CREW_VERBOSE,
        memory=Config.AGENT_MEMORY_ENABLED,
        max_iter=Config.AGENT_MAX_ITER,
        allow_delegation=False,
    )


def create_resume_reviewer_agent() -> Agent:
    """
    Creates the Resume Reviewer/Auditor agent.

    This agent objectively reviews resumes, scores them, and gives
    actionable feedback to improve structure, ATS compatibility, and impact.
    """
    return Agent(
        role="ATS Resume Auditor & Career Coach",
        goal=(
            "Objectively review a candidate's resume against modern hiring standards. "
            "Give a balanced scorecard, point out structural/impact issues, "
            "identify missing ATS keywords, and provide concrete, prioritized fixes "
            "to make the resume stronger for the target role."
        ),
        backstory=(
            "You are an ex-technical recruiter and certified resume reviewer who has "
            "screened 10,000+ resumes across private and government roles. You know "
            "ATS parsing, bullet writing (Action + Impact), federal resume nuances, "
            "and what actually gets interviews. You are blunt but constructive, "
            "specific with examples, and focused on high-impact changes first."
        ),
        llm=_get_llm(),
        verbose=Config.CREW_VERBOSE,
        memory=Config.AGENT_MEMORY_ENABLED,
        max_iter=Config.AGENT_MAX_ITER,
        allow_delegation=False,
    )
