# task4_routing.py
# The ROUTING tasks: assign support tickets to the right agent.
#
# The agent must look at:
#   1. The ticket's required skill
#   2. Each support agent's skills
#   3. Each support agent's current workload
#
# And decide which agent should handle each ticket.
#
# Scoring per ticket:
#   Skill match correct    → +0.5  (most important)
#   Best workload choice   → +0.3  (picked least busy qualified agent)
#   Priority acknowledged  → +0.2  (high priority → low workload agent)

from environment.data_tickets import get_tickets_for_task, get_all_agents

# ── TASK CONFIGS ──────────────────────────────────────────────────────────────

TASK4_EASY_CONFIG = {
    "task_id"     : "routing_easy",
    "name"        : "Ticket Routing — Easy",
    "description" : (
        "You are a support team manager. "
        "Assign each incoming ticket to the best available support agent. "
        "Consider the agent's skills and current workload. "
        "Available agents: Alice (technical, billing, workload 2), "
        "Bob (technical, workload 4), Carol (billing, general, workload 1), "
        "Dave (general, technical, workload 3), Eve (billing, workload 0). "
        "Reply with the agent_id of your chosen agent."
    ),
    "max_steps"   : 5,
    "passing_score": 0.6,
}

TASK4_MEDIUM_CONFIG = {
    "task_id"     : "routing_medium",
    "name"        : "Ticket Routing — Medium",
    "description" : (
        "You are a support team manager with 8 tickets to assign. "
        "For each ticket choose the best agent based on skill match AND workload. "
        "Available agents: Alice (technical, billing, workload 2), "
        "Bob (technical, workload 4), Carol (billing, general, workload 1), "
        "Dave (general, technical, workload 3), Eve (billing, workload 0). "
        "Reply with the agent_id of your chosen agent."
    ),
    "max_steps"   : 12,
    "passing_score": 0.65,
}

TASK4_HARD_CONFIG = {
    "task_id"     : "routing_hard",
    "name"        : "Ticket Routing — Hard",
    "description" : (
        "You are a support team manager with 10 tickets including ambiguous ones. "
        "Some tickets have unclear skill requirements — read carefully. "
        "Balance skill match with workload. High priority tickets must go "
        "to the least busy qualified agent. "
        "Available agents: Alice (technical, billing, workload 2), "
        "Bob (technical, workload 4), Carol (billing, general, workload 1), "
        "Dave (general, technical, workload 3), Eve (billing, workload 0)."
    ),
    "max_steps"   : 15,
    "passing_score": 0.7,
}

# ── GRADER ────────────────────────────────────────────────────────────────────

def grade_routing(actions: list, ground_truths: list) -> dict:
    """
    Grade the agent's ticket routing decisions.

    actions       : list of dicts, each with {"ticket_id", "assigned_agent_id"}
    ground_truths : list of ticket dicts with correct answers

    Per ticket scoring:
        +0.5  skill match    — assigned agent has the required skill
        +0.3  workload       — chose the least busy qualified agent
        +0.2  priority match — high priority went to low workload agent
    """

    if not actions:
        return {
            "score"    : 0.0,
            "reason"   : "No actions submitted.",
            "breakdown": {},
        }

    agents      = {a["id"]: a for a in get_all_agents()}
    per_ticket  = []
    breakdown   = {}

    for action, truth in zip(actions, ground_truths):
        ticket_id   = truth["id"]
        assigned_id = action.get("assigned_agent_id", "")
        agent       = agents.get(assigned_id)

        ticket_score = 0.0
        ticket_breakdown = {}

        if agent is None:
            # Agent assigned to someone who doesn't exist
            ticket_breakdown = {
                "skill_match": 0.0,
                "workload"   : 0.0,
                "priority"   : 0.0,
                "reason"     : f"Unknown agent '{assigned_id}'"
            }
            per_ticket.append(0.0)
            breakdown[ticket_id] = ticket_breakdown
            continue

        required_skill = truth["required_skill"]

        # ── Skill match (0.5) ─────────────────────────────────────────────
        if required_skill in agent["skills"]:
            ticket_breakdown["skill_match"] = 0.5
            ticket_score += 0.5
        else:
            ticket_breakdown["skill_match"] = 0.0

        # ── Workload check (0.3) ──────────────────────────────────────────
        # Find the minimum workload among all qualified agents
        qualified_agents = [
            a for a in agents.values()
            if required_skill in a["skills"]
        ]
        min_workload = min(a["workload"] for a in qualified_agents)

        if agent["workload"] == min_workload:
            ticket_breakdown["workload"] = 0.3
            ticket_score += 0.3
        elif agent["workload"] <= min_workload + 1:
            # Close enough — partial credit
            ticket_breakdown["workload"] = 0.15
            ticket_score += 0.15
        else:
            ticket_breakdown["workload"] = 0.0

        # ── Priority match (0.2) ──────────────────────────────────────────
        # High priority tickets should go to least busy agent
        if truth["priority"] == "high" and agent["workload"] == min_workload:
            ticket_breakdown["priority"] = 0.2
            ticket_score += 0.2
        elif truth["priority"] != "high":
            # Not high priority — any valid assignment gets credit
            ticket_breakdown["priority"] = 0.2
            ticket_score += 0.2
        else:
            ticket_breakdown["priority"] = 0.0

        per_ticket.append(round(ticket_score, 4))
        breakdown[ticket_id] = ticket_breakdown

    final_score = round(sum(per_ticket) / len(per_ticket), 4)

    if final_score >= 0.9:
        reason = f"Excellent routing! Score: {final_score}"
    elif final_score >= 0.7:
        reason = f"Good routing with some suboptimal assignments. Score: {final_score}"
    elif final_score >= 0.5:
        reason = f"Partial routing — some skill mismatches. Score: {final_score}"
    else:
        reason = f"Poor routing — most tickets misassigned. Score: {final_score}"

    return {
        "score"    : final_score,
        "reason"   : reason,
        "breakdown": breakdown,
    }