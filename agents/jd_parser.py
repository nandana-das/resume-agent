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


NON_SKILL_TERMS = {
    "responsibility",
    "responsibilities",
    "responsibilitys",
    "responsibility of",
    "access",
    "location",
    "age",
    "country",
    "verify",
    "birth year",
    "birth",
    "year",
    "month",
    "day",
    "remember",
    "terms",
    "conditions",
    "privacy",
    "cookie",
    "cookies",
    "policy",
    "apply",
    "apply now",
    "job",
    "role",
    "company",
    "candidate",
    "email",
    "phone",
    "address",
}


SKILL_HINT_PATTERNS = (
    r"(?:experience with|proficient in|familiar with|knowledge of|skills in|using|working with|hands-on with|strong in)\s+([^.\n;:]*)",
    r"(?:must have|required|requirements|qualification[s]?)\s*[:\-]\s*([^.\n;:]*)",
)


COMMON_SKILL_TERMS = (
    "python",
    "java",
    "javascript",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "powerpoint",
    "tensor flow",
    "tensorflow",
    "pytorch",
    "keras",
    "scikit-learn",
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
    "data analysis",
    "data science",
    "communication",
    "stakeholder management",
    "project management",
    "problem solving",
    "presentations",
    "research",
    "statistics",
    "optimization",
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



def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()


def _looks_like_skill(item: str) -> bool:
    candidate = _normalize(item)
    if not candidate:
        return False

    if candidate in NON_SKILL_TERMS:
        return False

    # Match NON_SKILL_TERMS as whole words/phrases, not arbitrary substrings.
    # A raw substring check here would reject valid skills like "Language",
    # "Storage", "Management", "Package", or "Image" just because they contain
    # the short filler term "age" — which silently wipes out most real tech
    # skill lists. Word-boundary matching keeps the intent (drop boilerplate
    # words like "email", "phone", "apply now") without nuking real terms
    # that merely contain those letters.
    if any(
        re.search(rf"\b{re.escape(term)}\b", candidate)
        for term in NON_SKILL_TERMS
    ):
        return False

    # Keep concise, concrete technical terms; drop long narrative phrases.
    if len(candidate) < 2 or len(candidate) > 60:
        return False

    return True


def _clean_skill_list(items: list[str]) -> list[str]:
    cleaned = []
    seen = set()
    for item in items:
        if not isinstance(item, str):
            continue
        candidate = item.strip()
        normalized = _normalize(candidate)
        if not _looks_like_skill(candidate) or normalized in seen:
            continue
        seen.add(normalized)
        cleaned.append(candidate)
    return cleaned


def _split_candidate_phrase(phrase: str) -> list[str]:
    parts = re.split(r"[,/;&]|\band\b", phrase, flags=re.IGNORECASE)
    return [part.strip(" .:-\t\n\r") for part in parts if part and part.strip()]


def _extract_fallback_skills(jd_text: str) -> list[str]:
    text = jd_text or ""
    candidates = []

    for pattern in SKILL_HINT_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            candidates.extend(_split_candidate_phrase(match.group(1)))

    lowered = _normalize(text)
    for term in COMMON_SKILL_TERMS:
        if term in lowered:
            candidates.append(term)

    return _clean_skill_list(candidates)


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
Only include concrete skills, technologies, tools, methods, or certifications.
Do not include legal, privacy, location, demographic, or generic job-posting words.
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
        parsed = json.loads(cleaned)

        if isinstance(parsed, dict):
            parsed["required_skills"] = _clean_skill_list(parsed.get("required_skills", []))
            parsed["preferred_skills"] = _clean_skill_list(parsed.get("preferred_skills", []))
            parsed["keywords"] = _clean_skill_list(parsed.get("keywords", []))

            # If the LLM gives us sparse or noisy skill lists, mine a fallback set
            # from the raw JD text so the evaluator can still compare resume vs JD.
            fallback_skills = _extract_fallback_skills(jd_text)
            if not parsed["required_skills"] and fallback_skills:
                parsed["required_skills"] = fallback_skills[:]

            parsed["all_skills"] = _clean_skill_list(
                parsed["required_skills"] + parsed["preferred_skills"] + parsed["keywords"]
            )

            if not parsed["all_skills"] and fallback_skills:
                parsed["all_skills"] = fallback_skills

        return parsed

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
            "all_skills": _extract_fallback_skills(jd_text),
            "education": "Not specified",
            "summary": raw_output[:300],
            "parse_error": "JSON parsing failed"
        }