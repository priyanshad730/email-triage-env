# app.py
# This file wraps our environment in a web API.
# Judges ping this API to validate our environment works.
# Three endpoints:
#   POST /reset  — start a fresh episode
#   POST /step   — submit one action
#   GET  /state  — see current state

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from environment.env import EmailTriageEnv

# ── CREATE THE APP ─────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "Email Triage Environment",
    description = "OpenEnv environment for email triage and classification",
    version     = "1.0.0",
)

# ── STORE THE ENVIRONMENT IN MEMORY ───────────────────────────────────────────
# We keep one environment instance running at a time
# In a real system you'd have one per user session

current_env: Optional[EmailTriageEnv] = None

# ── REQUEST MODELS ─────────────────────────────────────────────────────────────
# These define what the API expects to receive

class ResetRequest(BaseModel):
    task_id: str = "easy"   # which task to run: easy, medium, hard

class StepRequest(BaseModel):
    email_id    : str
    urgency     : str
    department  : str
    is_duplicate: bool = False
    notes       : Optional[str] = None

# ── ENDPOINTS ──────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    """Health check — judges ping this to confirm the environment is live."""
    return {
        "status" : "ok",
        "name"   : "email-triage-env",
        "version": "1.0.0",
        "tasks"  : ["easy", "medium", "hard"],
    }

@app.post("/reset")
async def reset(request: Request):
    """
    Start a fresh episode.
    Returns the first observation the agent will see.
    """
    global current_env

    # Try to parse body — if no body sent, use default task_id "easy"
    try:
        body = await request.json()
        task_id = body.get("task_id", "easy")
    except Exception:
        task_id = "easy"

    # Validate task_id
    if task_id not in ["easy", "medium", "hard", "routing_easy", "routing_medium", "routing_hard"]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task_id '{task_id}'."
        )

    current_env = EmailTriageEnv(task_id=task_id)
    obs         = current_env.reset()

    return {
        "task_id"      : obs.task_id,
        "instructions" : obs.instructions,
        "emails"       : obs.emails,
        "current_score": obs.current_score,
        "steps_taken"  : obs.steps_taken,
        "max_steps"    : obs.max_steps,
        "done"         : obs.done,
    }

@app.post("/step")
def step(request: StepRequest):
    """
    Submit one action (classification of one email).
    Returns the new observation, reward, and whether the episode is done.
    """
    global current_env

    # Make sure reset() was called first
    if current_env is None:
        raise HTTPException(
            status_code = 400,
            detail      = "Environment not initialized. Call /reset first."
        )

    # Build action dict
    action = {
        "email_id"    : request.email_id,
        "urgency"     : request.urgency,
        "department"  : request.department,
        "is_duplicate": request.is_duplicate,
        "notes"       : request.notes,
    }

    # Step the environment
    result = current_env.step(action)

    return {
        "observation": {
            "task_id"      : result["observation"].task_id,
            "instructions" : result["observation"].instructions,
            "emails"       : result["observation"].emails,
            "current_score": result["observation"].current_score,
            "steps_taken"  : result["observation"].steps_taken,
            "max_steps"    : result["observation"].max_steps,
            "done"         : result["observation"].done,
        },
        "reward": {
            "value"    : result["reward"].value,
            "reason"   : result["reward"].reason,
            "breakdown": result["reward"].breakdown,
        },
        "done": result["done"],
        "info": result["info"],
    }

@app.get("/state")
def state():
    """
    Return the current state of the environment.
    Useful for debugging.
    """
    global current_env

    if current_env is None:
        raise HTTPException(
            status_code = 400,
            detail      = "Environment not initialized. Call /reset first."
        )

    return current_env.state()

@app.get("/dashboard", response_class=None)
async def dashboard():
    """Serve the live dashboard HTML page."""
    from fastapi.responses import FileResponse
    return FileResponse("dashboard.html")