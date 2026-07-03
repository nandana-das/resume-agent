# graph/pipeline.py
# ─────────────────────────────────────────────
# LangGraph Pipeline
# Connects all 4 agents into one automated flow
# Input  : Resume text + JD text
# Output : Final state with all agent outputs
# ─────────────────────────────────────────────

import time
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

from agents.jd_parser import parse_jd
from agents.resume_evaluator import evaluate_resume
from agents.gap_analyst import analyze_gaps
from agents.resume_writer import write_resume


# ── Shared state — passed between all agents ──
class ResumeState(TypedDict):
    # Inputs
    resume_text: str
    jd_text: str
    include_suggested_projects: bool

    # Agent outputs — empty at start, filled as pipeline runs
    parsed_jd: Optional[dict]       # filled by Agent 1
    evaluation: Optional[dict]      # filled by Agent 2
    gap_analysis: Optional[dict]    # filled by Agent 3
    final_resume: Optional[str]     # filled by Agent 4

    # Tracking
    current_step: Optional[str]
    error: Optional[str]


# ── Node 1 — JD Parser ──
def jd_parser_node(state: ResumeState) -> ResumeState:
    """
    Reads jd_text from state.
    Adds parsed_jd to state.
    """
    try:
        print("  🔍 Agent 1 running — Parsing JD...")
        parsed = parse_jd(state["jd_text"])
        return {
            **state,
            "parsed_jd": parsed,
            "current_step": "jd_parsed"
        }
    except Exception as e:
        return {
            **state,
            "error": f"Agent 1 failed: {e}",
            "current_step": "error"
        }


# ── Node 2 — Resume Evaluator ──
def evaluator_node(state: ResumeState) -> ResumeState:
    """
    Reads resume_text + parsed_jd from state.
    Adds evaluation to state.
    """
    time.sleep(3)
    if state.get("error"):
        return state  # skip if previous agent failed

    try:
        print("  ⭐ Agent 2 running — Evaluating resume...")
        evaluation = evaluate_resume(
            state["resume_text"],
            state["parsed_jd"]
        )
        return {
            **state,
            "evaluation": evaluation,
            "current_step": "evaluated"
        }
    except Exception as e:
        return {
            **state,
            "error": f"Agent 2 failed: {e}",
            "current_step": "error"
        }


# ── Node 3 — Gap Analyst ──
def gap_analyst_node(state: ResumeState) -> ResumeState:
    """
    Reads resume_text + parsed_jd + evaluation from state.
    Adds gap_analysis to state.
    """
    time.sleep(3)
    if state.get("error"):
        return state  # skip if previous agent failed

    try:
        print("  💡 Agent 3 running — Analyzing gaps...")
        gap_analysis = analyze_gaps(
            state["resume_text"],
            state["parsed_jd"],
            state["evaluation"]
        )
        return {
            **state,
            "gap_analysis": gap_analysis,
            "current_step": "gaps_analyzed"
        }
    except Exception as e:
        return {
            **state,
            "error": f"Agent 3 failed: {e}",
            "current_step": "error"
        }


# ── Node 4 — Resume Writer ──
def writer_node(state: ResumeState) -> ResumeState:
    """
    Reads everything from state.
    Adds final_resume to state.
    """
    time.sleep(3)
    if state.get("error"):
        return state  # skip if previous agent failed

    try:
        print("  ✍️  Agent 4 running — Writing resume...")
        final_resume = write_resume(
            resume_text=state["resume_text"],
            parsed_jd=state["parsed_jd"],
            evaluation=state["evaluation"],
            gap_analysis=state["gap_analysis"],
            include_suggested_projects=state.get(
                "include_suggested_projects", True
            )
        )
        return {
            **state,
            "final_resume": final_resume,
            "current_step": "done"
        }
    except Exception as e:
        return {
            **state,
            "error": f"Agent 4 failed: {e}",
            "current_step": "error"
        }


# ── Build the Graph ──
def build_pipeline():
    """
    Creates and compiles the LangGraph StateGraph.
    Nodes = agents
    Edges = connections between agents
    """
    graph = StateGraph(ResumeState)

    # Add all 4 agents as nodes
    graph.add_node("jd_parser",   jd_parser_node)
    graph.add_node("evaluator",   evaluator_node)
    graph.add_node("gap_analyst", gap_analyst_node)
    graph.add_node("writer",      writer_node)

    # Connect nodes in sequence
    graph.set_entry_point("jd_parser")
    graph.add_edge("jd_parser",   "evaluator")
    graph.add_edge("evaluator",   "gap_analyst")
    graph.add_edge("gap_analyst", "writer")
    graph.add_edge("writer",      END)

    return graph.compile()


# ── Main entry point ──
def run_pipeline(
    resume_text: str,
    jd_text: str,
    include_suggested_projects: bool = True
) -> ResumeState:
    """
    Single function that runs the entire 4-agent pipeline.
    This is what Streamlit calls with one line.
    Returns final state with all agent outputs.
    """
    pipeline = build_pipeline()

    # Initial state — empty outputs, just inputs
    initial_state: ResumeState = {
        "resume_text": resume_text,
        "jd_text": jd_text,
        "include_suggested_projects": include_suggested_projects,
        "parsed_jd": None,
        "evaluation": None,
        "gap_analysis": None,
        "final_resume": None,
        "current_step": "starting",
        "error": None
    }

    print("\n🚀 Pipeline started...\n")
    result = pipeline.invoke(initial_state)
    print("\n✅ Pipeline complete!\n")

    return result