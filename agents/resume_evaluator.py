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


COMMON_SKILL_TERMS = (
    "python",
    "java",
    "javascript",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "tensorflow",
    "pytorch",
    "keras",
    "scikit-learn",
    "sklearn",
    "opencv",
    "pandas",
    "numpy",
    "git",
    "github",
    "linux",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "gcp",
    "machine learning",
    "deep learning",
    "computer vision",
    "nlp",
    "natural language processing",
    "data analysis",
    "data science",
    "statistics",
    "problem solving",
    "communication",
    "stakeholder management",
    "project management",
    # GenAI / LLM-era terms
    "generative ai",
    "genai",
    "gpt-4",
    "gpt",
    "llm",
    "large language model",
    "hugging face",
    "hugging face transformers",
    "transformers",
    "openai",
    "langchain",
    "langgraph",
    "rag",
    "graphrag",
    "retrieval augmented generation",
    "vector database",
    "embeddings",
    "prompt engineering",
    "agentic ai",
    "mlflow",
    "stable diffusion",
    "jupyter",
    "jupyter notebooks",
)

SKILL_HINT_PATTERNS = (
    r"(?:experience with|proficient in|familiar with|knowledge of|skills in|using|working with|hands-on with|strong in)\s+([^.\n;:]*)",
    r"(?:required skills?|preferred skills?|skills?|requirements?|qualifications?)\s*[:\-]\s*([^.\n;:]*)",
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _resume_has_skill(resume_text: str, skill: str) -> bool:
    resume = _normalize(resume_text)
    candidate = _normalize(skill)
    if not candidate:
        return False

    # Treat multi-word skills as substrings and single-word skills as token matches.
    if " " in candidate or "/" in candidate or "+" in candidate or "-" in candidate:
        return candidate in resume

    return re.search(rf"\b{re.escape(candidate)}\b", resume) is not None


def _jd_skill_candidates(parsed_jd: dict) -> list[str]:
    skills = []

    value = parsed_jd.get("all_skills", [])
    if isinstance(value, list):
        skills.extend(item for item in value if isinstance(item, str))

    for key in ("required_skills", "preferred_skills"):
        value = parsed_jd.get(key, [])
        if isinstance(value, list):
            skills.extend(item for item in value if isinstance(item, str))

    if not skills:
        value = parsed_jd.get("keywords", [])
        if isinstance(value, list):
            skills.extend(item for item in value if isinstance(item, str))

    deduped = []
    seen = set()
    for skill in skills:
        normalized = _normalize(skill)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(skill.strip())

    return deduped


def _extract_skill_candidates_from_jd_text(jd_text: str) -> list[str]:
    text = _normalize(jd_text)
    if not text:
        return []

    candidates = []

    for pattern in SKILL_HINT_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            chunk = match.group(1)
            parts = re.split(r"[,/;&]|\band\b", chunk, flags=re.IGNORECASE)
            for part in parts:
                candidate = part.strip(" .:-\t\n\r")
                if candidate:
                    candidates.append(candidate)

    for term in COMMON_SKILL_TERMS:
        if term in text:
            candidates.append(term)

    deduped = []
    seen = set()
    for skill in candidates:
        normalized = _normalize(skill)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(skill.strip())

    return deduped


def _finalize_skill_lists(resume_text: str, parsed_jd: dict, evaluation: dict, jd_text: str | None = None) -> dict:
    candidates = _jd_skill_candidates(parsed_jd)
    if not candidates and jd_text:
        candidates = _extract_skill_candidates_from_jd_text(jd_text)

    matched = [skill for skill in candidates if _resume_has_skill(resume_text, skill)]
    missing = [skill for skill in candidates if skill not in matched]

    evaluation["matched_skills"] = matched
    evaluation["missing_skills"] = missing
    return evaluation


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
Important: matched_skills and missing_skills must be derived only from the JD skill lists.
Do not introduce skills that are not present in parsed_jd.required_skills or parsed_jd.preferred_skills.
"""
)


def evaluate_resume(resume_text: str, parsed_jd: dict, jd_text: str | None = None) -> dict:
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
        evaluation = json.loads(cleaned)
        return _finalize_skill_lists(resume_text, parsed_jd, evaluation, jd_text=jd_text)

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