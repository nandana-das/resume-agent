# Resume Agent

An AI-powered resume builder that parses a job description, evaluates a resume against the role, finds gaps, and generates a tailored final resume.

## What it does

- Extracts resume text from PDF files.
- Scrapes or fetches job descriptions from a URL.
- Parses the job description into structured requirements.
- Scores the resume against the role with a breakdown of strengths and weaknesses.
- Identifies missing skills and suggested projects.
- Generates a tailored resume draft and exports it as DOCX.

## Tech Stack

- Streamlit for the UI
- LangGraph for orchestration
- LangChain + Groq for LLM calls
- BeautifulSoup, httpx, and pdfplumber for extraction and scraping
- python-docx and reportlab for document generation

## Project Layout

```text
app1.py                 # Streamlit entrypoint
agents/                 # JD parser, evaluator, gap analyst, resume writer
graph/pipeline.py       # LangGraph pipeline wiring
utils/                  # PDF extraction, scraping, and DOCX generation helpers
requirements.txt        # Python dependencies
```

## Local Setup

### 1. Create and activate a virtual environment

```bash
python -m venv resume
resume\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add environment variables

Create a `.env` file in the repository root or set these in your shell:

```env
GROQ_API_KEY=your_groq_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

`GROQ_API_KEY` is required for the LLM flow. `FIRECRAWL_API_KEY` is optional and only used for faster JD scraping.

### 4. Run the app

```bash
streamlit run app1.py
```

## How to Use

1. Upload a resume PDF.
2. Paste a job description or provide a job post URL.
3. Run the analysis pipeline.
4. Review the score, gaps, and tailored resume output.
5. Download the generated DOCX file if needed.

## Deployment on GitHub + Streamlit Community Cloud

1. Push this repository to GitHub.
2. Create a new app on Streamlit Community Cloud.
3. Point the app to this repository and use `app1.py` as the main file.
4. Add secrets in the Streamlit dashboard:

```toml
GROQ_API_KEY = "..."
FIRECRAWL_API_KEY = "..."
```

5. Deploy and verify the app loads correctly.

## Secrets and Config Files

- `.streamlit/secrets.toml` is ignored by Git and should hold local secrets only.
- `.streamlit/secrets.example.toml` shows the expected secret keys.
- `.streamlit/config.toml` contains the app theme and Streamlit runtime settings.

## Notes

- If you do not provide `FIRECRAWL_API_KEY`, the app falls back to HTTP-based scraping.
- The LLM config reads from Streamlit secrets first, then from environment variables.
- The pipeline is organized so each agent can be tested or extended independently.