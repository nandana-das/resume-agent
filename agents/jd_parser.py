# agents/jd_parser.py
# ─────────────────────────────────────────────
# Agent 1: JD Parser
# Input  : Raw job description text
# Output : Structured dict with skills,
#          keywords and responsibilities
# ─────────────────────────────────────────────

import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm


# ── The prompt we send to the LLM ──
PARSER_PROMPT = PromptTemplate(
    input_variables=["jd_text"],
    template="""
You are an expert technical recruiter with 10 years of experience.
Analyze the job description below and extract structured information.

JOB DESCRIPTION:
{jd_text}

Return ONLY a valid JSON object. No explanation. No markdown. Just JSON.

{{
  "role": "exact job title from JD",
  "company": "company name if mentioned, else Unknown",
  "experience_years": "e.g. 3-5 years or fresher",
  "required_skills": ["skill1", "skill2", "skill3"],
  "preferred_skills": ["skill1", "skill2"],
  "responsibilities": ["responsibility1", "responsibility2"],
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "education": "education requirement if mentioned",
  "summary": "2 sentence summary of what this role is about"
}}

Be thorough with required_skills and keywords.
These are used for resume matching so extract as many as possible.
"""
)


def parse_jd(jd_text: str) -> dict:
    """
    Main function — called by LangGraph pipeline.
    Sends JD text to LLM and returns structured dict.
    """
    llm = get_llm()

    # Prompt → LLM → Output Parser (the LCEL chain)
    chain = PARSER_PROMPT | llm | StrOutputParser()

    # Send JD text to the chain
    raw_output = chain.invoke({"jd_text": jd_text})

    # Clean and parse the JSON response
    try:
        # Remove accidental markdown fences like ```json
        cleaned = re.sub(r"```json|```", "", raw_output).strip()
        return json.loads(cleaned)

    except json.JSONDecodeError:
        # If JSON parsing fails return raw output in a safe dict
        return {
            "role": "Unknown",
            "company": "Unknown",
            "experience_years": "Not specified",
            "required_skills": [],
            "preferred_skills": [],
            "responsibilities": [],
            "keywords": [],
            "education": "Not specified",
            "summary": raw_output[:300],
            "parse_error": "JSON parsing failed"
        }