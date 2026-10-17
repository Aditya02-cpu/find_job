# 🚀 Multi-Agent Job Application Assistant

An AI-powered job application assistant built with **CrewAI**, **Google Gemini**, and **Streamlit** that automates your entire job search workflow using a collaborative multi-agent system.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![CrewAI](https://img.shields.io/badge/CrewAI-Multi--Agent-purple)
![Gemini](https://img.shields.io/badge/Google-Gemini-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-red)

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Streamlit Web App                      │
│  ┌──────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  Search   │  │   Generate   │  │  Application      │  │
│  │  Jobs     │  │   Materials  │  │  History           │  │
│  └────┬─────┘  └──────┬───────┘  └───────────────────┘  │
│       │               │                                  │
│       ▼               ▼                                  │
│  ┌─────────┐   ┌──────────────┐                         │
│  │ USAJobs │   │  CrewAI Crew │                         │
│  │   API   │   │  ┌─────────┐ │                         │
│  └─────────┘   │  │Analyzer │─┤                         │
│                │  ├─────────┤ │                         │
│                │  │Resume   │─┤                         │
│                │  ├─────────┤ │                         │
│                │  │LinkedIn │ │                         │
│                │  └─────────┘ │                         │
│                └──────────────┘                         │
│                       │                                  │
│                       ▼                                  │
│               Google Gemini LLM                          │
└─────────────────────────────────────────────────────────┘
```

### AI Agents Pipeline

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| 🔬 **Job Analyzer** | Extracts requirements, skills, keywords | Job posting data | Structured analysis report |
| 📄 **Resume Customizer** | Tailors resume & writes cover letter | Analysis + User resume | ATS-optimized resume + cover letter |
| 💬 **LinkedIn Outreach** | Drafts networking messages | Analysis + Resume | 3 personalized message templates |

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

Edit `.env` and fill in your keys:

| Key | Where to Get It |
|-----|----------------|
| `GEMINI_API_KEY` | [Google AI Studio](https://aistudio.google.com/) |
| `USAJOBS_API_KEY` | [USAJobs Developer Portal](https://developer.usajobs.gov/APIRequest/Index) |
| `USAJOBS_EMAIL` | The email you registered with USAJobs |

### 3. Run the App

```bash
streamlit run app.py
```

---

## 🖥️ Usage

1. **Search Jobs** — Enter keywords and location to fetch real government job listings from USAJobs.gov
2. **Select a Position** — Click "Select for AI Processing" on any job card
3. **Paste Your Resume** — Add your base resume in the sidebar
4. **Generate Materials** — Click "Launch AI Agent Pipeline" to run all 3 agents
5. **Download Results** — Get your tailored resume, cover letter, and LinkedIn messages
6. **Track History** — View all past applications in the History tab

---

## 📁 Project Structure

```
Multi_agent_job/
├── app.py                 # Streamlit web application
├── agents.py              # CrewAI agent definitions
├── tasks.py               # CrewAI task definitions
├── crew.py                # Crew orchestration
├── config.py              # Configuration management
├── usajobs_client.py      # USAJobs API client
├── logger.py              # Application logging
├── requirements.txt       # Python dependencies
├── .env.example           # API key template
├── .gitignore
└── README.md
```

---

## 🛠️ Technologies

- **CrewAI** — Multi-agent orchestration framework
- **Google Gemini** (via LiteLLM) — Large language model for NLP tasks
- **Streamlit** — Interactive web application framework
- **USAJobs API** — Real government job postings data source
- **Python 3.10+** — Core language

---

## 📄 License

MIT License — feel free to use this as a portfolio project.
