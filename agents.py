"""
CrewAI Agent definitions for the Multi-Agent Job Application Assistant.

Three specialized agents collaborate in a sequential pipeline:
  1. Job Analyzer Agent — extracts key requirements from job listings.
  2. Resume Customizer Agent — tailors resume and cover letter to the job.
  3. LinkedIn Outreach Agent — drafts personalized outreach messages.
"""

from crewai import Agent, LLM
from config import Config


def _get_llm() -> LLM:
    """Create a shared Gemini LLM instance for all agents."""
    return LLM(
        model=Config.GEMINI_MODEL,
        temperature=0.7,
        api_key=Config.GEMINI_API_KEY,
    )


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
        verbose=True,
        memory=True,
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
        verbose=True,
        memory=True,
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
        verbose=True,
        memory=True,
        allow_delegation=False,
    )
