# inference.py
# This is the mandatory agent loop for the hackathon.
# It connects an AI model to our environment and runs it on all 3 tasks.
# The AI reads each email and decides urgency, department, and duplicate status.

import os
import json
from openai import OpenAI
from environment.env import EmailTriageEnv

# ── LOAD ENVIRONMENT VARIABLES ────────────────────────────────────────────────
# These must be set before running this script.
# On Windows: set HF_TOKEN=xxx, set API_BASE_URL=xxx, set MODEL_NAME=xxx

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY      = os.getenv("HF_TOKEN")
MODEL_NAME   = os.getenv("MODEL_NAME")

# ── SETTINGS ──────────────────────────────────────────────────────────────────

MAX_STEPS   = 25       # maximum actions per episode
TEMPERATURE = 0.1      # low = more consistent answers
MAX_TOKENS  = 300      # keep responses short and structured

# ── OPENAI CLIENT ─────────────────────────────────────────────────────────────
# We use the OpenAI client but point it at Hugging Face's API.

client = OpenAI(
    base_url = API_BASE_URL,
    api_key  = API_KEY,
)

# ── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
# This tells the AI exactly what role it plays and how to format its answer.

SYSTEM_PROMPT = """
You are a customer support triage agent.
You will be given one email to classify.

You must respond with ONLY a JSON object in this exact format:
{
    "email_id": "the email id from the input",
    "urgency": "low" or "medium" or "high",
    "department": "billing" or "technical" or "general",
    "is_duplicate": true or false,
    "notes": "one sentence explanation of your decision"
}

Rules:
- urgency "high" means the customer needs help immediately or is very frustrated
- urgency "medium" means the issue is real but not time-sensitive
- urgency "low" means it is a general question or feedback
- department "billing" means it is about payments, charges, refunds, or invoices
- department "technical" means it is about the app, login, bugs, or features
- department "general" means it does not fit billing or technical
- is_duplicate is true if the email seems like a follow-up to another email in the list
- Respond with ONLY the JSON. No extra text. No explanation outside the JSON.
""".strip()

# ── HELPER: BUILD USER PROMPT ─────────────────────────────────────────────────

def build_user_prompt(email: dict, all_emails: list) -> str:
    """
    Build the prompt the agent sees for each email.
    Shows the current email plus a summary of previous emails for duplicate detection.
    """

    # Show previous email subjects so agent can detect duplicates
    previous = [
        f"- [{e['id']}] {e['subject']}"
        for e in all_emails
        if e["id"] != email["id"]
    ]
    previous_text = (
        "\n".join(previous)
        if previous
        else "None — this is the first email."
    )

    return f"""
Previous emails in this inbox:
{previous_text}

Now classify this email:
ID      : {email['id']}
Subject : {email['subject']}
Body    : {email['body']}
""".strip()

# ── HELPER: CALL THE MODEL ────────────────────────────────────────────────────

def call_model(user_prompt: str) -> dict:
    """
    Send a prompt to the AI model and parse its JSON response.
    Returns a dict with the agent's classification decision.
    """
    try:
        response = client.chat.completions.create(
            model       = MODEL_NAME,
            messages    = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature = TEMPERATURE,
            max_tokens  = MAX_TOKENS,
        )

        raw_text = response.choices[0].message.content.strip()

        # Sometimes the model wraps JSON in ```json ``` — strip that out
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]

        return json.loads(raw_text)

    except json.JSONDecodeError:
        print(f"  ⚠ Model returned invalid JSON. Using fallback action.")
        return {
            "email_id"    : "unknown",
            "urgency"     : "medium",
            "department"  : "general",
            "is_duplicate": False,
            "notes"       : "Fallback action due to JSON parse error."
        }
    except Exception as e:
        print(f"  ⚠ Model call failed: {e}. Using fallback action.")
        return {
            "email_id"    : "unknown",
            "urgency"     : "medium",
            "department"  : "general",
            "is_duplicate": False,
            "notes"       : "Fallback action due to API error."
        }

# ── RUN ONE TASK ──────────────────────────────────────────────────────────────

def run_task(task_id: str) -> float:
    """
    Run the agent on one task (easy, medium, or hard).
    Returns the final score as a float between 0.0 and 1.0.
    """
    print(f"\n{'='*55}")
    print(f"  TASK: {task_id.upper()}")
    print(f"{'='*55}")

    # Start fresh environment
    env = EmailTriageEnv(task_id=task_id)
    obs = env.reset()

    print(f"  Emails to triage : {len(obs.emails)}")
    print(f"  Instructions     : {obs.instructions[:80]}...")

    final_score = 0.0

    # Loop through each email one by one
    for i, email in enumerate(obs.emails):
        if env.done:
            break

        print(f"\n  Email {i+1}/{len(obs.emails)}: [{email['id']}] {email['subject']}")

        # Build prompt and call model
        user_prompt = build_user_prompt(email, obs.emails)
        action      = call_model(user_prompt)

        # Make sure email_id matches the current email
        action["email_id"] = email["id"]

        print(f"  → urgency: {action.get('urgency')} | "
              f"department: {action.get('department')} | "
              f"duplicate: {action.get('is_duplicate')}")

        # Submit action to environment
        result      = env.step(action)
        final_score = result["reward"].value

        print(f"  → score so far: {final_score}")

    print(f"\n  FINAL SCORE ({task_id}): {final_score}")
    print(f"  Reason: {result['reward'].reason}")
    return final_score

# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "="*55)
    print("  EMAIL TRIAGE ENV — BASELINE INFERENCE")
    print("="*55)
    print(f"  Model   : {MODEL_NAME}")
    print(f"  API URL : {API_BASE_URL}")

    scores = {}

    # Run all 3 tasks in order
    for task_id in ["easy", "medium", "hard"]:
        scores[task_id] = run_task(task_id)

    # Print final summary
    print("\n" + "="*55)
    print("  FINAL SCORES SUMMARY")
    print("="*55)
    for task_id, score in scores.items():
        status = "✅ PASS" if score >= 0.6 else "❌ FAIL"
        print(f"  {task_id:<8} : {score:.4f}  {status}")

    avg = sum(scores.values()) / len(scores)
    print(f"\n  Average  : {avg:.4f}")
    print("="*55)

if __name__ == "__main__":
    main()
