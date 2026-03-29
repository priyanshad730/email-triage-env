# test_env.py
# This script simulates a fake agent playing through all 3 tasks.
# It's not a real AI — just hardcoded answers.
# Purpose: make sure reset(), step(), and state() all work correctly.

from environment.env import EmailTriageEnv

def test_easy():
    print("\n── TASK 1: EASY ──────────────────────────────────────")
    env = EmailTriageEnv(task_id="easy")

    # Start fresh episode
    obs = env.reset()
    print(f"Task      : {obs.task_id}")
    print(f"Emails    : {len(obs.emails)}")
    print(f"First email subject: {obs.emails[0]['subject']}")

    # Simulate agent submitting one action
    action = {
        "email_id"    : "email_01",
        "urgency"     : "high",        # correct answer
        "department"  : "technical",   # correct answer
        "is_duplicate": False,         # correct answer
    }

    result = env.step(action)
    print(f"Score     : {result['reward'].value}")
    print(f"Reason    : {result['reward'].reason}")
    print(f"Done      : {result['done']}")

def test_medium():
    print("\n── TASK 2: MEDIUM ────────────────────────────────────")
    env = EmailTriageEnv(task_id="medium")
    obs = env.reset()
    print(f"Task      : {obs.task_id}")
    print(f"Emails    : {len(obs.emails)}")

    # Simulate agent submitting actions for all 5 emails
    actions = [
        {"email_id": "email_01", "urgency": "high",   "department": "technical", "is_duplicate": False},
        {"email_id": "email_02", "urgency": "high",   "department": "billing",   "is_duplicate": False},
        {"email_id": "email_03", "urgency": "low",    "department": "general",   "is_duplicate": False},
        {"email_id": "email_04", "urgency": "high",   "department": "technical", "is_duplicate": False},
        {"email_id": "email_05", "urgency": "medium", "department": "billing",   "is_duplicate": False},
    ]

    for action in actions:
        result = env.step(action)

    print(f"Final score : {result['reward'].value}")
    print(f"Reason      : {result['reward'].reason}")
    print(f"Done        : {result['done']}")

def test_hard():
    print("\n── TASK 3: HARD ──────────────────────────────────────")
    env = EmailTriageEnv(task_id="hard")
    obs = env.reset()
    print(f"Task      : {obs.task_id}")
    print(f"Emails    : {len(obs.emails)}")

    # Simulate agent — gets some right, misses the escalation emails
    actions = [
        {"email_id": "email_01", "urgency": "high",   "department": "technical", "is_duplicate": False},
        {"email_id": "email_02", "urgency": "high",   "department": "billing",   "is_duplicate": False},
        {"email_id": "email_03", "urgency": "low",    "department": "general",   "is_duplicate": False},
        {"email_id": "email_04", "urgency": "high",   "department": "technical", "is_duplicate": False},
        {"email_id": "email_05", "urgency": "medium", "department": "billing",   "is_duplicate": False},
        {"email_id": "email_06", "urgency": "low",    "department": "technical", "is_duplicate": True},
        {"email_id": "email_07", "urgency": "low",    "department": "billing",   "is_duplicate": False},
        {"email_id": "email_08", "urgency": "high",   "department": "technical", "is_duplicate": False},
        {"email_id": "email_09", "urgency": "low",    "department": "general",   "is_duplicate": False},
        {"email_id": "email_10", "urgency": "high",   "department": "billing",   "is_duplicate": False},
        {"email_id": "email_11", "urgency": "medium", "department": "technical", "is_duplicate": False},
        {"email_id": "email_12", "urgency": "low",    "department": "billing",   "is_duplicate": True},  # misses escalation!
        {"email_id": "email_13", "urgency": "low",    "department": "technical", "is_duplicate": True},
        {"email_id": "email_14", "urgency": "low",    "department": "technical", "is_duplicate": False}, # misses escalation!
        {"email_id": "email_15", "urgency": "medium", "department": "billing",   "is_duplicate": True},
    ]

    for action in actions:
        result = env.step(action)

    print(f"Final score        : {result['reward'].value}")
    print(f"Reason             : {result['reward'].reason}")
    print(f"Escalation misses  : {result['reward'].breakdown.get('escalation_misses', 'N/A')}")
    print(f"Done               : {result['done']}")

def test_state():
    print("\n── STATE CHECK ───────────────────────────────────────")
    env = EmailTriageEnv(task_id="easy")
    env.reset()
    state = env.state()
    print(f"task_id       : {state['task_id']}")
    print(f"steps_taken   : {state['steps_taken']}")
    print(f"current_score : {state['current_score']}")
    print(f"done          : {state['done']}")

if __name__ == "__main__":
    test_easy()
    test_medium()
    test_hard()
    test_state()
    print("\n✅ All tests passed!")
