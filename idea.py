"""
Startup Idea Enhancement System using LangGraph
Processes raw startup ideas through normalization, structuring, validation, and enhancement.
"""

import os
import sys
import json
from typing import TypedDict, List, Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

# Load environment variables from .env
load_dotenv()

# Fix Windows console encoding issue
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ============================================================================
# PYDANTIC MODELS FOR STRUCTURED OUTPUT
# ============================================================================

class MarketSize(BaseModel):
    tam: str = Field(description="Total Addressable Market estimate")
    sam: str = Field(description="Serviceable Available Market estimate")
    som: str = Field(description="Serviceable Obtainable Market estimate")


class Competitor(BaseModel):
    name: str
    strengths: str
    weaknesses: str
    gaps: str


class MVPScope(BaseModel):
    core_features: List[str] = Field(description="Minimum viable features")
    build_complexity: Literal["WEEKEND", "1_MONTH", "3_MONTHS"]


class EnhancedStartupIdea(BaseModel):
    problem_statement: str
    target_users: str
    solution: str
    value_proposition: str
    key_assumptions: List[str]

    feasibility_score: float = Field(ge=0, le=1)
    problem_clarity_score: float = Field(ge=0, le=1)
    user_specificity_score: float = Field(ge=0, le=1)

    market_type: Literal["B2C", "B2B", "B2G", "B2B2C", "Marketplace", "Platform"]

    differentiation_strength: Literal["LOW", "MEDIUM", "HIGH"]
    differentiation_explanation: str

    assumption_risk_score: float = Field(ge=0, le=1)
    execution_complexity: Literal["LOW", "MEDIUM", "HIGH"]

    validation_readiness: Literal[
        "READY_FOR_INTERVIEWS",
        "READY_FOR_MVP",
        "NEEDS_MORE_RESEARCH",
        "READY_FOR_LANDING_PAGE"
    ]

    primary_risk_category: Literal[
        "MARKET", "PRODUCT", "EXECUTION", "TECHNICAL", "REGULATORY"
    ]

    ethical_legal_sensitivity_level: Literal["LOW", "MEDIUM", "HIGH"]
    ethical_legal_sensitivity_explanation: str

    next_best_action: Literal[
        "USER_INTERVIEWS",
        "LANDING_PAGE",
        "MVP_PROTOTYPE",
        "MARKET_RESEARCH",
        "COMPETITOR_ANALYSIS"
    ]

    market_size: MarketSize
    competitors: List[Competitor]

    founder_problem_fit: float = Field(ge=0, le=1)
    revenue_streams: List[str]
    key_metrics: List[str]
    unfair_advantage: str

    mvp_scope: MVPScope
    customer_acquisition_channels: List[str]

    desirability_score: float = Field(ge=0, le=1)
    viability_score: float = Field(ge=0, le=1)


# ============================================================================
# STATE DEFINITION
# ============================================================================

class WorkflowState(TypedDict):
    raw_idea: str
    normalized_idea: str
    structured_idea: str
    validation_result: str
    validation_passed: bool
    retry_count: int
    final_output: dict
    error: str


# ============================================================================
# WORKFLOW CLASS
# ============================================================================

class StartupIdeaEnhancer:

    def __init__(self, groq_api_key: str, max_retries: int = 5):
        self.max_retries = max_retries
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model="openai/gpt-oss-120b",
            temperature=0.7
        )
        self.structured_llm = self.llm.with_structured_output(EnhancedStartupIdea)

    def normalization_agent(self, state: WorkflowState) -> WorkflowState:
        print("🔄 Running Normalization Agent...")

        prompt = f"""
Normalize the following startup idea:
{state['raw_idea']}
"""

        response = self.llm.invoke([SystemMessage(content=prompt)])
        state["normalized_idea"] = response.content.strip()
        return state

    def structuring_agent(self, state: WorkflowState) -> WorkflowState:
        print("🔄 Running Structuring Agent...")

        prompt = f"""
Extract problem, target_users, solution, value_proposition, key_assumptions as JSON.

Idea:
{state['normalized_idea']}
"""

        response = self.llm.invoke([SystemMessage(content=prompt)])
        state["structured_idea"] = response.content.strip()
        return state

    def validation_agent(self, state: WorkflowState) -> WorkflowState:
        print("🔄 Running Validation Agent...")

        prompt = f"""
Validate the following structured idea.
Return STATUS: PASS or FAIL.

{state['structured_idea']}
"""

        response = self.llm.invoke([SystemMessage(content=prompt)])
        state["validation_result"] = response.content.strip()
        state["validation_passed"] = "PASS" in state["validation_result"]
        return state

    def enhancement_agent(self, state: WorkflowState) -> WorkflowState:
        print("🔄 Running Enhancement Agent...")

        try:
            structured = json.loads(state["structured_idea"])
        except Exception:
            structured = {"raw": state["structured_idea"]}

        prompt = f"""
Enhance this startup idea:

{json.dumps(structured, indent=2, ensure_ascii=False)}
"""

        try:
            result = self.structured_llm.invoke(
                [SystemMessage(content=prompt), HumanMessage(content="Generate full analysis")]
            )
            state["final_output"] = result.model_dump()
        except Exception as e:
            state["error"] = str(e)

        return state

    def should_retry(self, state: WorkflowState) -> str:
        if state["validation_passed"]:
            return "enhance"

        if state["retry_count"] >= self.max_retries:
            state["error"] = "Max retries reached"
            return "end"

        state["retry_count"] += 1
        return "retry"

    def build_graph(self):
        graph = StateGraph(WorkflowState)

        graph.add_node("normalize", self.normalization_agent)
        graph.add_node("structure", self.structuring_agent)
        graph.add_node("validate", self.validation_agent)
        graph.add_node("enhance", self.enhancement_agent)

        graph.set_entry_point("normalize")
        graph.add_edge("normalize", "structure")
        graph.add_edge("structure", "validate")

        graph.add_conditional_edges(
            "validate",
            self.should_retry,
            {"retry": "structure", "enhance": "enhance", "end": END}
        )

        graph.add_edge("enhance", END)
        return graph.compile()

    def process_idea(self, raw_idea: str) -> dict:
        initial_state: WorkflowState = {
            "raw_idea": raw_idea,
            "normalized_idea": "",
            "structured_idea": "",
            "validation_result": "",
            "validation_passed": False,
            "retry_count": 0,
            "final_output": {},
            "error": ""
        }

        graph = self.build_graph()
        return graph.invoke(initial_state)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":

    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    enhancer = StartupIdeaEnhancer(GROQ_API_KEY)

    raw_idea = """
    students always struggle finding good notes and study material
    i want to build platform where they share notes and get rewards
    also AI can help summarize long pdfs
    """

    result = enhancer.process_idea(raw_idea)

    if result["final_output"]:
        print("\n📊 ENHANCED STARTUP IDEA:\n")
        print(json.dumps(result["final_output"], indent=2, ensure_ascii=False))

        with open("enhanced_startup_idea.json", "w", encoding="utf-8") as f:
            json.dump(result["final_output"], f, indent=2, ensure_ascii=False)

        print("\n💾 Saved to enhanced_startup_idea.json")

    else:
        print("❌ ERROR:", result["error"])
