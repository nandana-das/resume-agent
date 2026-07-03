# agents/resume_evaluator.py
# ─────────────────────────────────────────────
# Agent 2: Resume Evaluator
# Input  : Resume text + parsed JD dict
# Output : Score out of 10 with full breakdown
# ─────────────────────────────────────────────

import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm


EVALUATOR_PROMPT = PromptTemplate(
    input_variables=["resume_text", "parsed_jd"],
    template="""
You are a senior technical hiring manager with 15 years of experience.
Evaluate the resume below strictly against the job description data.

RESUME:
{resume_text}

JOB DESCRIPTION DATA:
{parsed_jd}

Return ONLY a valid JSON object. No explanation. No markdown. Just JSON.

{{
  "overall_score": <number between 1 and 10>,
  "breakdown": {{
    "skills_match": <1-10>,
    "experience_relevance": <1-10>,
    "keywords_alignment": <1-10>,
    "project_relevance": <1-10>,
    "presentation_clarity": <1-10>
  }},
  "matched_skills": ["skills from JD that ARE in the resume"],
  "missing_skills": ["skills from JD that are NOT in the resume"],
  "strengths": ["specific strength 1", "specific strength 2"],
  "weaknesses": ["specific weakness 1", "specific weakness 2"],
  "verdict": "one paragraph honest assessment of this resume for this role"
}}

Be strict and specific. Mention actual skills and experiences from the resume.
Do not inflate scores. A 10 means the resume is perfect for this role.
"""
)


def evaluate_resume(resume_text: str, parsed_jd: dict) -> dict:
    """
    Main function — called by LangGraph pipeline.
    Takes resume text and parsed JD dict from Agent 1.
    Returns structured evaluation dict.
    """
    llm = get_llm()

    chain = EVALUATOR_PROMPT | llm | StrOutputParser()

    raw_output = chain.invoke({
        "resume_text": resume_text,
        # Convert dict to string so LLM can read it
        "parsed_jd": json.dumps(parsed_jd, indent=2)
    })

    try:
        cleaned = re.sub(r"```json|```", "", raw_output).strip()
        return json.loads(cleaned)

    except json.JSONDecodeError:
        return {
            "overall_score": 0,
            "breakdown": {},
            "matched_skills": [],
            "missing_skills": [],
            "strengths": [],
            "weaknesses": [],
            "verdict": raw_output[:500],
            "parse_error": "JSON parsing failed"
        }