from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import json
from typing import List, Literal
from typing_extensions import TypedDict


from idea import StartupIdeaEnhancer

# ----------------------------------------------------------------------------
# FASTAPI APP
# ----------------------------------------------------------------------------

app = FastAPI(
    title="Startup Idea Enhancement API",
    description="LangGraph-powered startup idea analysis & enhancement system",
    version="1.0.0"
)

# ----------------------------------------------------------------------------
# LOAD API KEY
# ----------------------------------------------------------------------------

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY not found in environment variables")

enhancer = StartupIdeaEnhancer(GROQ_API_KEY)

# ----------------------------------------------------------------------------
# REQUEST / RESPONSE MODELS
# ----------------------------------------------------------------------------

class IdeaRequest(BaseModel):
    raw_idea: str


class IdeaResponse(BaseModel):
    result: dict


# ----------------------------------------------------------------------------
# HEALTH CHECK
# ----------------------------------------------------------------------------

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Startup Idea Enhancer API is running"}

# ----------------------------------------------------------------------------
# MAIN ENDPOINT
# ----------------------------------------------------------------------------

@app.post("/enhance-idea", response_model=IdeaResponse)
def enhance_idea(request: IdeaRequest):
    try:
        result = enhancer.process_idea(request.raw_idea)

        if not result.get("final_output"):
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Idea enhancement failed")
            )

        return {"result": result["final_output"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
