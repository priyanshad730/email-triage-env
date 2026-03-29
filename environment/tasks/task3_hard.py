# task3_hard.py
# The HARD task: triage a full inbox of 15 emails.
# This is genuinely difficult because:
#   - 15 emails to read and classify
#   - multiple duplicates hidden inside
#   - one email has a time-sensitive escalation buried in polite language
#   - agent must prioritize correctly — not just classify
#   - penalty for missing the escalation email

from environment.data import get_emails_for_task

# ── TASK DEFINITION ───────────────────────────────────────────────────────────

TASK3_CONFIG = {
    "task_id": "hard",
    "name": "Full Inbox Triage with Escalation Detection",
    "description": (
        "You are a senior customer support agent. "
        "You have 15 emails in your inbox. "
        "For EACH email decide: urgency (low/medium/high), "
        "department (billing/technical/general), "
        "and whether it is a duplicate of another email. "
        "IMPORTANT: Some emails are follow-ups or escalations — "
        "a polite email may still be urgent if the customer has "
        "been waiting too long or has a time-sensitive need. "
        "Read every email carefully before deciding urgency."
    ),
    "max_steps": 20,       # more steps for more emails
    "passing_score": 0.8,  # hard task — needs 0.8 to pass
}

# ── ESCALATION EMAILS ─────────────────────────────────────────────────────────
# These are the emails where getting urgency wrong is penalised extra.
# email_12 is an angry escalation — must be flagged high + duplicate
# email_14 is time-sensitive — must be flagged high

ESCALATION_EMAIL_IDS = ["email_12", "email_14"]

# ── TASK SETUP ────────────────────────────────────────────────────────────────

def get_task3_emails():
    """Return all 15 emails for the hard task."""
    return get_emails_for_task("hard")

# ── GRADER ────────────────────────────────────────────────────────────────────

def grade_task3(actions: list, ground_truths: list) -> dict:
    """
    Grade the agent's triage of 15 emails.

    Same per-email scoring as task 2 (urgency 0.4, dept 0.4, dup 0.2)
    PLUS an escalation penalty:
        -0.2 for each escalation email where urgency is wrong
        This can push the score below what basic classification gives.

    Final score is clamped between 0.0 and 1.0.
    """

    if not actions:
        return {
            "score": 0.0,
            "reason": "No actions submitted.",
            "breakdown": {},
        }

    per_email_scores = []
    breakdown = {}
    escalation_misses = 0

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

            # ── Escalation penalty ────────────────────────────────────────────
            if email_id in ESCALATION_EMAIL_IDS:
                email_breakdown["escalation_penalty"] = -0.2
                email_score -= 0.2
                escalation_misses += 1

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

        # ── Clamp per-email score to 0.0 minimum ─────────────────────────────
        email_score = max(0.0, round(email_score, 4))
        per_email_scores.append(email_score)
        breakdown[email_id] = email_breakdown

    # ── Final score = average, clamped between 0.0 and 1.0 ───────────────────
    final_score = sum(per_email_scores) / len(per_email_scores)
    final_score = round(max(0.0, min(1.0, final_score)), 4)

    # ── Build reason ──────────────────────────────────────────────────────────
    if escalation_misses == 0 and final_score >= 0.8:
        reason = f"Excellent! All escalations caught. Score: {final_score}."
    elif escalation_misses == 0:
        reason = f"Escalations caught but some emails misclassified. Score: {final_score}."
    elif escalation_misses == 1:
        reason = f"Missed 1 escalation email (-0.2 penalty). Score: {final_score}."
    else:
        reason = f"Missed {escalation_misses} escalation emails. Score: {final_score}."

    return {
        "score": final_score,
        "reason": reason,
        "breakdown": breakdown,
        "escalation_misses": escalation_misses,
    }