# agents/resume_writer.py
# ─────────────────────────────────────────────
# Agent 4: Resume Writer
# Input  : Resume + all 3 previous agent outputs
# Output : Complete tailored resume as text
#          ready to convert to DOCX
# ─────────────────────────────────────────────

import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_config import get_llm


WRITER_PROMPT = PromptTemplate(
    input_variables=[
        "resume_text",
        "parsed_jd",
        "evaluation",
        "gap_analysis",
        "include_suggested_projects"
    ],
    template="""
You are an expert resume writer who creates ATS-optimized resumes.
Your task is to rewrite and improve the candidate's resume
to align it with the target job description.

ORIGINAL RESUME:
{resume_text}

TARGET ROLE DATA:
{parsed_jd}

EVALUATION — what is currently weak:
{evaluation}

GAP ANALYSIS — what to add and fix:
{gap_analysis}

INCLUDE SUGGESTED PROJECTS: {include_suggested_projects}

STRICT RULES — follow these exactly:
1. Do NOT fabricate companies or job roles
2. Keep the candidate's real experience — only rephrase it
3. Naturally include JD keywords in bullet points
4. Add metrics to every bullet point where possible
5. Use strong action verbs: Built, Developed, Deployed, Optimized, Led
6. If INCLUDE SUGGESTED PROJECTS is True add suggested projects
7. Put most relevant experience and skills FIRST
8. Keep formatting ATS friendly — no tables, no columns

OUTPUT FORMAT — use this exact structure:

[CANDIDATE NAME]
[Email] | [Phone] | [LinkedIn] | [GitHub] | [City]

## SUMMARY
2-3 lines tailored specifically to the target role

## SKILLS
- Technical: skill1, skill2, skill3
- Tools: tool1, tool2, tool3
- Soft Skills: skill1, skill2

## EXPERIENCE
[Job Title] — [Company Name]                [Start] – [End]
- Achievement focused bullet with metric
- Achievement focused bullet with metric
- Achievement focused bullet with metric

## PROJECTS
[Project Name] | tech1, tech2, tech3
- What you built and what problem it solved
- Key metric or outcome

## EDUCATION
[Degree] — [Institution]                    [Year]

## CERTIFICATIONS
- Certification Name — Issuing Body (Year)

Write the complete resume now.
Return only the resume text — no explanation, no preamble.
"""
)


def write_resume(
    resume_text: str,
    parsed_jd: dict,
    evaluation: dict,
    gap_analysis: dict,
    include_suggested_projects: bool = True
) -> str:
    """
    Main function — called by LangGraph pipeline.
    Takes ALL previous agent outputs as input.
    Returns final resume as plain text string.
    """
    llm = get_llm()

    chain = WRITER_PROMPT | llm | StrOutputParser()

    final_resume = chain.invoke({
        "resume_text": resume_text,
        "parsed_jd": json.dumps(parsed_jd, indent=2),
        "evaluation": json.dumps(evaluation, indent=2),
        "gap_analysis": json.dumps(gap_analysis, indent=2),
        "include_suggested_projects": str(include_suggested_projects)
    })

    return final_resume.strip()