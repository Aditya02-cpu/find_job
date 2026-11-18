# 🚀 Multi-Agent Job Application Assistant

An AI-powered job application assistant built with **CrewAI**, **Google Gemini**, and **Streamlit** that automates your entire job search workflow using a collaborative multi-agent system.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-purple)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

For full design details, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🧠 Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                     Streamlit Web App                          │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐ │
│  │  Search   │ │ Resume Review│ │ Generate │ │  History     │ │
│  │  Jobs     │ │  (AI Audit)  │ │ Materials│ │              │ │
│  └────┬─────┘ └──────┬───────┘ └────┬─────┘ └──────┬───────┘ │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│  ┌───────────┐  ┌──────────┐  ┌──────────────────────┐         │
│  │ USAJobs   │  │ Upload / │  │ CrewAI (stepwise):   │         │
│  │ Adzuna    │  │ paste CV │  │ 1. Job Analyzer      │         │
│  │ JSearch   │  └────┬─────┘  │ 2. Resume + Cover    │         │
│  │ Jooble    │       │        │ 3. LinkedIn Outreach │         │
│  └─────┬─────┘       │        └──────────┬───────────┘         │
│        └─────────────┼───────────────────┘                     │
│                      ▼                                         │
│              Google Gemini LLM (with fallback chain)           │
│                      ▼                                         │
│        logs/application_log.json + output/APP-*/...md         │
└───────────────────────────────────────────────────────────────┘
```

### AI Agents Pipeline

Each step runs in its own single-agent crew with progress reporting; prior outputs are passed explicitly to the next step.

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| 🔬 **Job Analyzer** | Extracts requirements, skills, keywords | Job posting data | Structured analysis report |
| 📄 **Resume Customizer** | Tailors resume & writes cover letter | Analysis + User resume | ATS-optimized resume + cover letter |
| 💬 **LinkedIn Outreach** | Drafts networking messages | Analysis + Resume | 3 personalized message templates |
| 🧾 **Resume Reviewer** | Audits and scores a resume | Uploaded resume + optional job | Prioritized improvement report |

---

## ⚙️ Setup

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd Multi_agent_job
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and fill in the keys you need (all options are documented in `.env.example`):

| Key | Needed for | Where to Get It |
|-----|-----------|-----------------|
| `GEMINI_API_KEY` | All AI features | [Google AI Studio](https://aistudio.google.com/) |
| `GEMINI_MODEL` | Optional model override | Defaults to `gemini/gemini-3.8-flash` |
| `GEMINI_FALLBACK_MODELS` | Optional retry chain | Defaults to two flash-lite models |
| `USAJOBS_API_KEY` | USA job search | [USAJobs Developer Portal](https://developer.usajobs.gov/APIRequest/Index) |
| `USAJOBS_EMAIL` | USA job search | The email you registered with USAJobs |
| `INDIAN_JOB_PROVIDER` | India job search | `adzuna` (default), `jsearch`, or `jooble` |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | `INDIAN_JOB_PROVIDER=adzuna` | [Adzuna API](https://developer.adzuna.com/) |
| `RAPIDAPI_KEY` | `INDIAN_JOB_PROVIDER=jsearch` | [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) |
| `JOOBLE_API_KEY` | `INDIAN_JOB_PROVIDER=jooble` | [Jooble API](https://jooble.org/api/about) |

### 3. Run the App

```bash
streamlit run app.py
```

---

## 🖥️ Usage

1. **Add Your Resume** — Upload a PDF/DOCX/TXT/MD file in the sidebar, or paste the text directly
2. **Search Jobs** — Choose `USA (USAJobs)` or `India`, then enter keywords and location
3. **Select a Position** — Click "Select for AI Processing" on any job card
4. **Generate Materials** — Launch the 3-step pipeline for a tailored resume, cover letter, and LinkedIn messages
5. **Review Your Resume** — Use the Resume Review page for an AI audit with prioritized fixes
6. **Download Results** — Export generated documents and the review report as Markdown
7. **Track History** — View all past applications in the History tab

---

## 📁 Project Structure

```
Multi_agent_job/
├── app.py                 # Streamlit UI, pages, session state, resume upload
├── agents.py              # CrewAI agents + shared Gemini LLM
├── tasks.py               # Task definitions + prompt truncation
├── crew.py                # Stepwise orchestration + retry/fallback logic
├── config.py              # Centralized config and validation
├── usajobs_client.py      # USAJobs API client
├── indian_jobs_client.py  # Adzuna / JSearch / Jooble clients
├── logger.py              # Application history + output files
├── requirements.txt       # Python dependencies
├── .env.example           # Full configuration template
├── .gitignore
├── ARCHITECTURE.md        # Detailed architecture reference
├── logs/                  # Generated at runtime (git-ignored)
├── output/                # Generated at runtime (git-ignored)
└── README.md
```

---

## 🛠️ Technologies

- **CrewAI** — Multi-agent orchestration framework
- **Google Gemini** (via LiteLLM) — LLM with fallback models and retry/backoff
- **Streamlit** — Interactive web application framework
- **USAJobs API** — US federal job postings
- **Adzuna / JSearch / Jooble** — Indian job postings
- **pypdf / python-docx** — Resume text extraction
- **Python 3.10+** — Core language

---

## 📄 License

MIT License — feel free to use this as a portfolio project.

