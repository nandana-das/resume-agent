# Resume Agent

AI-powered resume builder and evaluator built with Streamlit.

## Local run

```bash
pip install -r requirements.txt
streamlit run app1.py
```

## GitHub + Streamlit deployment

1. Push this repository to GitHub.
2. Deploy it on Streamlit Community Cloud and point the app to `app1.py`.
3. Add secrets in the Streamlit dashboard or create `.streamlit/secrets.toml` locally.
4. Set at least `GROQ_API_KEY`.
5. Optional: set `FIRECRAWL_API_KEY` if you want faster JD scraping.

## Secrets format

```toml
GROQ_API_KEY = "..."
FIRECRAWL_API_KEY = "..."
```