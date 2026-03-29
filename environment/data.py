# data.py
# This file contains all the fake emails our agent will practice on.
# We write them by hand so we always know the correct answer — 
# which means we can grade the agent perfectly.

# Each email is a dictionary (a collection of labeled values).
# Every email has:
#   - id         : unique name so we can refer to it
#   - subject    : the email subject line
#   - body       : the email content
#   - urgency    : the CORRECT answer for urgency (low/medium/high)
#   - department : the CORRECT answer for department (billing/technical/general)
#   - duplicate_of: None, or the id of the email this is a duplicate of

EMAILS = [

    # ── EASY EMAILS (obvious signals, clear department) ──────────────────────

    {
        "id": "email_01",
        "subject": "Cannot login to my account",
        "body": "Hi, I have been trying to log in for the past hour but keep getting an error. Please help urgently.",
        "urgency": "high",
        "department": "technical",
        "duplicate_of": None
    },
    {
        "id": "email_02",
        "subject": "Wrong charge on my bill",
        "body": "I was charged $150 instead of $50 on my last invoice. Please correct this as soon as possible.",
        "urgency": "high",
        "department": "billing",
        "duplicate_of": None
    },
    {
        "id": "email_03",
        "subject": "How do I update my profile picture?",
        "body": "Hello, I would like to know how to change my profile photo on the website. Thanks.",
        "urgency": "low",
        "department": "general",
        "duplicate_of": None
    },
    {
        "id": "email_04",
        "subject": "App is crashing on startup",
        "body": "Every time I open the app it crashes immediately. I have tried restarting my phone but it still crashes.",
        "urgency": "high",
        "department": "technical",
        "duplicate_of": None
    },
    {
        "id": "email_05",
        "subject": "Request for refund",
        "body": "I would like to request a refund for my purchase made last week. The product did not meet expectations.",
        "urgency": "medium",
        "department": "billing",
        "duplicate_of": None
    },

    # ── MEDIUM EMAILS (less obvious, need reading carefully) ─────────────────

    {
        "id": "email_06",
        "subject": "Still waiting for response",
        "body": "I sent an email three days ago about my login issue and have not heard back. This is very frustrating.",
        "urgency": "high",
        "department": "technical",
        "duplicate_of": "email_01"   # duplicate of email_01
    },
    {
        "id": "email_07",
        "subject": "Question about pricing plans",
        "body": "Could you explain the difference between the basic and premium plans? I am considering upgrading.",
        "urgency": "low",
        "department": "billing",
        "duplicate_of": None
    },
    {
        "id": "email_08",
        "subject": "Data export not working",
        "body": "When I click the export button nothing happens. I need this data for a report due tomorrow morning.",
        "urgency": "high",
        "department": "technical",
        "duplicate_of": None
    },
    {
        "id": "email_09",
        "subject": "Feedback on new dashboard",
        "body": "The new dashboard looks great! Just wanted to share some thoughts on how it could be improved further.",
        "urgency": "low",
        "department": "general",
        "duplicate_of": None
    },
    {
        "id": "email_10",
        "subject": "Double charged this month",
        "body": "I noticed two charges of $50 on my credit card this month from your service. Please investigate.",
        "urgency": "high",
        "department": "billing",
        "duplicate_of": None
    },

    # ── HARD EMAILS (tricky, ambiguous, escalation buried inside) ────────────

    {
        "id": "email_11",
        "subject": "General inquiry",
        "body": "Hi, I have a few questions. First my invoice seems off. Second the app keeps freezing. Third I wanted to say the support team was very helpful last time.",
        "urgency": "medium",
        "department": "technical",  # primary issue is technical
        "duplicate_of": None
    },
    {
        "id": "email_12",
        "subject": "Following up again",
        "body": "This is my third email about the double charge. Nobody has responded. I will contact my bank if this is not resolved today.",
        "urgency": "high",
        "department": "billing",
        "duplicate_of": "email_10"  # escalation of email_10
    },
    {
        "id": "email_13",
        "subject": "App feedback",
        "body": "Love the app overall. One small thing — the export button does not seem to work on my end. No rush though.",
        "urgency": "low",           # user said no rush — but it IS a duplicate
        "department": "technical",
        "duplicate_of": "email_08"  # duplicate of email_08
    },
    {
        "id": "email_14",
        "subject": "Urgent: account suspended",
        "body": "My account has been suspended without warning. I have an important client presentation in 2 hours and need access immediately.",
        "urgency": "high",
        "department": "technical",
        "duplicate_of": None
    },
    {
        "id": "email_15",
        "subject": "Invoice question",
        "body": "Hello, not sure if this is the right place to ask but I think I may have been charged twice. Could someone look into this when they get a chance?",
        "urgency": "medium",        # polite tone but real billing issue
        "department": "billing",
        "duplicate_of": "email_10"  # another duplicate of email_10
    },
]

# ── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
# These make it easy to grab specific emails from the list above.

def get_email_by_id(email_id: str) -> dict:
    """Find and return one email by its id."""
    for email in EMAILS:
        if email["id"] == email_id:
            return email
    return None

def get_emails_for_task(task: str) -> list:
    """Return the right set of emails depending on the task difficulty."""
    if task == "easy":
        return EMAILS[0:1]       # just 1 email
    elif task == "medium":
        return EMAILS[0:5]       # first 5 emails
    elif task == "hard":
        return EMAILS[0:15]      # all 15 emails
    else:
        return []
