# agents/gap_analyst.py
# ─────────────────────────────────────────────
# Agent 3: Gap Analyst
# Input  : Resume text + parsed JD + evaluation
# Output : Gaps, what company wants, and
#          3 concrete project suggestions
# ─────────────────────────────────────────────

import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm


GAP_ANALYST_PROMPT = PromptTemplate(
    input_variables=["resume_text", "parsed_jd", "evaluation"],
    template="""
You are a career coach specializing in tech roles.
Your job is to bridge the gap between what the candidate has
and what the role demands.

RESUME:
{resume_text}

JOB DESCRIPTION DATA:
{parsed_jd}

EVALUATION RESULTS FROM PREVIOUS ANALYSIS:
{evaluation}

Return ONLY a valid JSON object. No explanation. No markdown. Just JSON.

{{
  "what_they_want": [
    "Specific thing the company is really looking for beyond just skills",
    "Another key expectation from the JD"
  ],
  "critical_gaps": [
    {{
      "gap": "Gap description",
      "importance": "High/Medium/Low",
      "how_to_fix": "How to address this in the resume"
    }}
  ],
  "suggested_projects": [
    {{
      "title": "Project title",
      "description": "2 sentence project description",
      "tech_stack": ["tech1", "tech2", "tech3"],
      "why_it_helps": "Why this project fills a gap for this specific role",
      "sample_metric": "Example impact metric e.g. Reduced inference time by 40%"
    }},
    {{
      "title": "Project title 2",
      "description": "2 sentence project description",
      "tech_stack": ["tech1", "tech2"],
      "why_it_helps": "Why this fills a gap",
      "sample_metric": "Example metric"
    }},
    {{
      "title": "Project title 3",
      "description": "2 sentence project description",
      "tech_stack": ["tech1", "tech2"],
      "why_it_helps": "Why this fills a gap",
      "sample_metric": "Example metric"
    }}
  ],
  "quick_wins": [
    "Quick fix 1 that can be done immediately to improve the resume",
    "Quick fix 2",
    "Quick fix 3"
  ]
}}

Make project suggestions realistic and directly tied to JD requirements.
Each project should fill a specific gap identified in the evaluation.
"""
)


def analyze_gaps(
    resume_text: str,
    parsed_jd: dict,
    evaluation: dict
) -> dict:
    """
    Main function — called by LangGraph pipeline.
    Takes outputs from Agent 1 AND Agent 2.
    Returns gap analysis with project suggestions.
    """
    llm = get_llm()

    chain = GAP_ANALYST_PROMPT | llm | StrOutputParser()

    raw_output = chain.invoke({
        "resume_text": resume_text,
        "parsed_jd": json.dumps(parsed_jd, indent=2),
        "evaluation": json.dumps(evaluation, indent=2)
    })

    try:
        cleaned = re.sub(r"```json|```", "", raw_output).strip()
        return json.loads(cleaned)

    except json.JSONDecodeError:
        return {
            "what_they_want": [],
            "critical_gaps": [],
            "suggested_projects": [],
            "quick_wins": [],
            "parse_error": "JSON parsing failed"
        }