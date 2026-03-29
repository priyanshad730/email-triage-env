# task1_easy.py
# The EASY task: classify a single email correctly.
# The agent just needs to look at one email and decide:
#   1. How urgent is it? (low / medium / high)
#   2. Which department handles it? (billing / technical / general)

from environment.data import get_emails_for_task

# ── TASK DEFINITION ───────────────────────────────────────────────────────────
# This dictionary describes the task to the agent in plain English.

TASK1_CONFIG = {
    "task_id": "easy",
    "name": "Single Email Classification",
    "description": (
        "You are a customer support agent. "
        "Read the email carefully and classify it correctly. "
        "Decide the urgency (low, medium, or high) and "
        "which department should handle it (billing, technical, or general)."
    ),
    "max_steps": 3,        # agent gets 3 chances to submit an action
    "passing_score": 0.6,  # agent needs at least 0.6 to pass this task
}

# ── TASK SETUP ────────────────────────────────────────────────────────────────

def get_task1_emails():
    """Return the single email used for the easy task."""
    return get_emails_for_task("easy")

# ── GRADER ────────────────────────────────────────────────────────────────────
# This function checks the agent's answer against the correct answer.
# It returns a score between 0.0 and 1.0.
# Partial credit is given — getting urgency right but department wrong = 0.5

def grade_task1(action: dict, ground_truth: dict) -> dict:
    """
    Grade the agent's classification of a single email.
    
    action       : what the agent decided  (urgency, department, is_duplicate)
    ground_truth : the correct answer from our data.py file
    
    Returns a dict with:
        score     : float between 0.0 and 1.0
        reason    : plain English explanation
        breakdown : detailed per-field scores
    """

    breakdown = {}
    total = 0.0

    # ── Check urgency (worth 0.4 points) ──────────────────────────────────────
    if action.get("urgency") == ground_truth.get("urgency"):
        breakdown["urgency"] = 0.4
        total += 0.4
    else:
        breakdown["urgency"] = 0.0

    # ── Check department (worth 0.4 points) ───────────────────────────────────
    if action.get("department") == ground_truth.get("department"):
        breakdown["department"] = 0.4
        total += 0.4
    else:
        breakdown["department"] = 0.0

    # ── Check duplicate detection (worth 0.2 points) ──────────────────────────
    correct_duplicate = ground_truth.get("duplicate_of") is not None
    agent_duplicate = action.get("is_duplicate", False)

    if agent_duplicate == correct_duplicate:
        breakdown["duplicate"] = 0.2
        total += 0.2
    else:
        breakdown["duplicate"] = 0.0

    # ── Build reason string ───────────────────────────────────────────────────
    reason_parts = []

    if breakdown["urgency"] > 0:
        reason_parts.append("urgency correct (+0.4)")
    else:
        reason_parts.append(
            f"urgency wrong — agent said '{action.get('urgency')}' "
            f"but correct is '{ground_truth.get('urgency')}' (+0.0)"
        )

    if breakdown["department"] > 0:
        reason_parts.append("department correct (+0.4)")
    else:
        reason_parts.append(
            f"department wrong — agent said '{action.get('department')}' "
            f"but correct is '{ground_truth.get('department')}' (+0.0)"
        )

    if breakdown["duplicate"] > 0:
        reason_parts.append("duplicate flag correct (+0.2)")
    else:
        reason_parts.append("duplicate flag wrong (+0.0)")

    return {
        "score": round(total, 4),
        "reason": " | ".join(reason_parts),
        "breakdown": breakdown,
    }
