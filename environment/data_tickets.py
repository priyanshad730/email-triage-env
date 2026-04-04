# data_tickets.py
# This file contains fake support tickets AND fake support agents.
# The agent must match each ticket to the best available support agent.
#
# Each support agent has:
#   - skills     : what types of tickets they can handle
#   - workload   : how many tickets they already have (lower = more available)
#
# Each ticket has:
#   - required_skill : what kind of expert is needed
#   - priority       : how urgent it is
#   - best_agent     : the CORRECT answer (who should get this ticket)

SUPPORT_AGENTS = [
    {
        "id"      : "agent_alice",
        "name"    : "Alice",
        "skills"  : ["technical", "billing"],
        "workload": 2,   # has 2 tickets already
    },
    {
        "id"      : "agent_bob",
        "name"    : "Bob",
        "skills"  : ["technical"],
        "workload": 4,   # busy
    },
    {
        "id"      : "agent_carol",
        "name"    : "Carol",
        "skills"  : ["billing", "general"],
        "workload": 1,   # very available
    },
    {
        "id"      : "agent_dave",
        "name"    : "Dave",
        "skills"  : ["general", "technical"],
        "workload": 3,
    },
    {
        "id"      : "agent_eve",
        "name"    : "Eve",
        "skills"  : ["billing"],
        "workload": 0,   # completely free
    },
]

TICKETS = [

    # ── EASY TICKETS (skill match is obvious) ─────────────────────────────

    {
        "id"            : "ticket_01",
        "subject"       : "Payment failed on checkout",
        "body"          : "I tried to pay for my order but the payment keeps failing.",
        "required_skill": "billing",
        "priority"      : "high",
        "best_agent"    : "agent_eve",    # Eve: billing skill, workload 0
    },
    {
        "id"            : "ticket_02",
        "subject"       : "App crashes on Android",
        "body"          : "The mobile app crashes every time I open it on my Android phone.",
        "required_skill": "technical",
        "priority"      : "high",
        "best_agent"    : "agent_alice",  # Alice: technical skill, workload 2 (less than Bob's 4)
    },
    {
        "id"            : "ticket_03",
        "subject"       : "How do I cancel my subscription?",
        "body"          : "I would like to cancel my subscription. Please advise.",
        "required_skill": "general",
        "priority"      : "low",
        "best_agent"    : "agent_carol",  # Carol: general skill, workload 1
    },

    # ── MEDIUM TICKETS (need to balance skill + workload) ─────────────────

    {
        "id"            : "ticket_04",
        "subject"       : "Invoice shows wrong amount",
        "body"          : "My invoice shows $200 but I should only be charged $100.",
        "required_skill": "billing",
        "priority"      : "high",
        "best_agent"    : "agent_eve",    # Eve: billing skill, workload 0 (better than Carol's 1)
    },
    {
        "id"            : "ticket_05",
        "subject"       : "API returning 500 errors",
        "body"          : "Our integration is getting 500 errors from your API since this morning.",
        "required_skill": "technical",
        "priority"      : "high",
        "best_agent"    : "agent_alice",  # Alice: technical, workload 2 (better than Bob's 4)
    },
    {
        "id"            : "ticket_06",
        "subject"       : "Need help setting up account",
        "body"          : "I am new and need help configuring my account settings.",
        "required_skill": "general",
        "priority"      : "medium",
        "best_agent"    : "agent_carol",  # Carol: general, workload 1
    },
    {
        "id"            : "ticket_07",
        "subject"       : "Refund not received after 7 days",
        "body"          : "I requested a refund last week but have not received it yet.",
        "required_skill": "billing",
        "priority"      : "medium",
        "best_agent"    : "agent_eve",    # Eve: billing, workload 0
    },
    {
        "id"            : "ticket_08",
        "subject"       : "Dashboard not loading",
        "body"          : "The main dashboard just shows a blank white screen.",
        "required_skill": "technical",
        "priority"      : "medium",
        "best_agent"    : "agent_alice",  # Alice: technical, workload 2
    },

    # ── HARD TICKETS (ambiguous skill, must read carefully) ───────────────

    {
        "id"            : "ticket_09",
        "subject"       : "Charged after cancellation",
        "body"          : "I cancelled my account last month but was still charged. "
                          "Also the cancellation page had a bug.",
        "required_skill": "billing",      # primary issue is billing
        "priority"      : "high",
        "best_agent"    : "agent_eve",    # Eve: billing, workload 0
    },
    {
        "id"            : "ticket_10",
        "subject"       : "General question about features",
        "body"          : "Hi, I was wondering if your platform supports bulk exports. "
                          "If yes, how do I set it up technically?",
        "required_skill": "technical",    # it's a technical how-to question
        "priority"      : "low",
        "best_agent"    : "agent_alice",  # Alice: technical + lower workload than Bob
    },
]

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────

def get_tickets_for_task(task: str) -> list:
    """Return the right number of tickets depending on difficulty."""
    if task == "routing_easy":
        return TICKETS[0:3]    # 3 tickets
    elif task == "routing_medium":
        return TICKETS[0:8]    # 8 tickets
    elif task == "routing_hard":
        return TICKETS[0:10]   # all 10 tickets
    return []

def get_all_agents() -> list:
    """Return all support agents."""
    return SUPPORT_AGENTS