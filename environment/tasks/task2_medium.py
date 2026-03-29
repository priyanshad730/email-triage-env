# task2_medium.py
# The MEDIUM task: triage a batch of 5 emails.
# The agent must classify ALL 5 correctly AND detect any duplicates.
# Harder than task 1 because:
#   - more emails to read
#   - one email is a duplicate of another — agent must spot it
#   - agent must get most of them right to score well

from environment.data import get_emails_for_task

# ── TASK DEFINITION ───────────────────────────────────────────────────────────

TASK2_CONFIG = {
    "task_id": "medium",
    "name": "Batch Email Triage",
    "description": (
        "You are a customer support agent. "
        "You have 5 emails in your inbox. "
        "For EACH email decide: urgency (low/medium/high), "
        "department (billing/technical/general), "
        "and whether it is a duplicate of another email you have already seen. "
        "You must submit one action per email."
    ),
    "max_steps": 8,        # agent gets more steps for more emails
    "passing_score": 0.7,  # harder task — needs 0.7 to pass
}

# ── TASK SETUP ────────────────────────────────────────────────────────────────

def get_task2_emails():
    """Return the 5 emails used for the medium task."""
    return get_emails_for_task("medium")

# ── GRADER ────────────────────────────────────────────────────────────────────

def grade_task2(actions: list, ground_truths: list) -> dict:
    """
    Grade the agent's triage of 5 emails.

    actions       : list of 5 dicts — one action per email
    ground_truths : list of 5 dicts — correct answers from data.py

    Each email is worth an equal share of the total score.
    Partial credit per email:
        urgency correct    → +0.4
        department correct → +0.4
        duplicate correct  → +0.2

    Final score = average score across all 5 emails.
    """

    if not actions:
        return {
            "score": 0.0,
            "reason": "No actions submitted.",
            "breakdown": {},
        }

    per_email_scores = []
    breakdown = {}

    for i, (action, truth) in enumerate(zip(actions, ground_truths)):
        email_id = truth.get("id", f"email_{i}")
        email_score = 0.0
        email_breakdown = {}

        # ── Urgency (0.4) ─────────────────────────────────────────────────────
        if action.get("urgency") == truth.get("urgency"):
            email_breakdown["urgency"] = 0.4
            email_score += 0.4
        else:
            email_breakdown["urgency"] = 0.0

        # ── Department (0.4) ──────────────────────────────────────────────────
        if action.get("department") == truth.get("department"):
            email_breakdown["department"] = 0.4
            email_score += 0.4
        else:
            email_breakdown["department"] = 0.0

        # ── Duplicate detection (0.2) ─────────────────────────────────────────
        correct_dup = truth.get("duplicate_of") is not None
        agent_dup = action.get("is_duplicate", False)

        if agent_dup == correct_dup:
            email_breakdown["duplicate"] = 0.2
            email_score += 0.2
        else:
            email_breakdown["duplicate"] = 0.0

        per_email_scores.append(round(email_score, 4))
        breakdown[email_id] = email_breakdown

    # ── Final score = average across all emails ───────────────────────────────
    final_score = round(sum(per_email_scores) / len(per_email_scores), 4)

    # ── Bonus: reward perfect triage ─────────────────────────────────────────
    if final_score == 1.0:
        reason = "Perfect triage! All emails correctly classified."
    elif final_score >= 0.7:
        reason = f"Good triage. Average score: {final_score}."
    elif final_score >= 0.4:
        reason = f"Partial triage. Average score: {final_score}. Some emails misclassified."
    else:
        reason = f"Poor triage. Average score: {final_score}. Most emails misclassified."

    return {
        "score": final_score,
        "reason": reason,
        "breakdown": breakdown,
    }
