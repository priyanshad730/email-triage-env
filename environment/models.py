# models.py
# This file defines the "shapes" of data that flow through our environment.
# Think of it like defining what an email looks like, what an agent's action looks like,
# and what a reward looks like — all in one place.

from pydantic import BaseModel
from typing import Literal, Optional, List

# ── OBSERVATION ────────────────────────────────────────────────────────────────
# This is what the AGENT SEES when it looks at the environment.
# Like a human reading their inbox.

class EmailObservation(BaseModel):
    task_id: str                  # which task is running: "easy", "medium", "hard"
    instructions: str             # plain English: what the agent is supposed to do
    emails: List[dict]            # the actual emails (list of email objects)
    current_score: float = 0.0   # running score so far (starts at 0)
    steps_taken: int = 0         # how many actions the agent has taken
    max_steps: int = 10          # maximum actions allowed before episode ends
    done: bool = False           # is the task finished?

# ── ACTION ─────────────────────────────────────────────────────────────────────
# This is what the AGENT DOES — its decision for each email.
# Like a human deciding what to do with each email in their inbox.

class TriageAction(BaseModel):
    email_id: str                                              # which email to act on
    urgency: Literal["low", "medium", "high"]                 # how urgent is it?
    department: Literal["billing", "technical", "general"]    # which team handles it?
    is_duplicate: bool = False                                 # is it a repeat email?
    notes: Optional[str] = None                               # optional agent reasoning

# ── REWARD ─────────────────────────────────────────────────────────────────────
# This is the SCORE the agent gets after each action.
# Partial credit is given — not just 0 or 1.

class TriageReward(BaseModel):
    value: float        # the actual score: anywhere from -0.1 to 1.0
    reason: str         # human-readable explanation of why this score was given
    breakdown: dict     # detailed scoring: {"urgency": 0.4, "department": 0.3, ...}