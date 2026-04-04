---
title: Email Triage Env
emoji: 📧
colorFrom: blue
colorTo: green
sdk: docker
app_file: app.py
pinned: false
---

# 📧 Email Triage Environment

An OpenEnv-compliant reinforcement learning environment where an AI agent
learns to triage customer support emails by urgency, department, and duplicate detection.

## What is this?

Real customer support teams receive hundreds of emails daily. 
This environment simulates that challenge — the agent must read emails and decide:
- **Urgency**: how quickly does this need attention? (low / medium / high)
- **Department**: who should handle it? (billing / technical / general)
- **Duplicate**: is this a repeat of an email already seen?

This is a real task that companies actually do. Getting it wrong costs time and money.

---

## Tasks

| Task           | Items | Difficulty | Passing Score | Description |
|----------------|-------|------------|---------------|-------------|
| easy           | 1     | Easy       | 0.6           | Classify a single email |
| medium         | 5     | Medium     | 0.7           | Triage batch, detect duplicates |
| hard           | 15    | Hard       | 0.8           | Full inbox with escalations |
| routing_easy   | 3     | Easy       | 0.6           | Assign 3 tickets to best agent |
| routing_medium | 8     | Medium     | 0.65          | Balance skill and workload |
| routing_hard   | 10    | Hard       | 0.7           | Ambiguous tickets, read carefully |
---

## Baseline Scores

Tested with `meta-llama/Llama-3.1-8B-Instruct` via Hugging Face Inference API:

| Task   | Score  | Status |
|--------|--------|--------|
| easy   | 1.0000 | ✅ PASS |
| medium | 1.0000 | ✅ PASS |
| hard   | 0.8933 | ✅ PASS |
| **avg**| **0.9644** | ✅ |
---

## Action Space

Each action is a JSON object with these fields:

| Field        | Type    | Values                              |
|--------------|---------|-------------------------------------|
| email_id     | string  | ID of the email being classified    |
| urgency      | enum    | low, medium, high                   |
| department   | enum    | billing, technical, general         |
| is_duplicate | boolean | true or false                       |
| notes        | string  | optional agent reasoning            |

Example action:
```json
{
    "email_id": "email_01",
    "urgency": "high",
    "department": "technical",
    "is_duplicate": false,
    "notes": "Customer cannot login and needs urgent help"
}
```

---

## Observation Space

Each observation contains:

| Field         | Type    | Description                        |
|---------------|---------|------------------------------------|
| task_id       | string  | Which task is running              |
| instructions  | string  | Plain English task description     |
| emails        | list    | List of emails to triage           |
| current_score | float   | Running score so far               |
| steps_taken   | int     | Number of actions taken            |
| max_steps     | int     | Maximum actions allowed            |
| done          | boolean | Whether the episode is finished    |

---

## Reward Function

Partial credit is given for every action:

| Correct field     | Points |
|-------------------|--------|
| urgency correct   | +0.4   |
| department correct| +0.4   |
| duplicate correct | +0.2   |
| **Total per email**| **1.0** |

**Hard task only:** Missing a time-sensitive escalation email incurs a -0.2 penalty.

Final score = average across all emails in the task, clamped to [0.0, 1.0].

---

## Setup & Usage

### Prerequisites
- Python 3.12
- A Hugging Face account with API token

### Install
```bash
git clone https://huggingface.co/spaces/yourusername/email-triage-env
cd email-triage-env
pip install -r requirements.txt
```

### Run the environment server
```bash
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Run the baseline inference script
```bash
export HF_TOKEN=your_token_here
export API_BASE_URL=https://router.huggingface.co/v1
export MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
python inference.py
```

On Windows:
```bash
set HF_TOKEN=your_token_here
set API_BASE_URL=https://router.huggingface.co/v1
set MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct
python inference.py
```

### Run with Docker
```bash
docker build -t email-triage-env .
docker run -p 8000:8000 \
  -e HF_TOKEN=your_token \
  -e API_BASE_URL=https://router.huggingface.co/v1 \
  -e MODEL_NAME=meta-llama/Llama-3.1-8B-Instruct \
  email-triage-env
```

---

## API Endpoints

| Method | Endpoint | Description              |
|--------|----------|--------------------------|
| GET    | /        | Health check             |
| POST   | /reset   | Start a fresh episode    |
| POST   | /step    | Submit one action        |
| GET    | /state   | Get current state        |

---

## Project Structure
```
email-triage-env/
├── environment/
│   ├── tasks/
│   │   ├── task1_easy.py
│   │   ├── task2_medium.py
│   │   └── task3_hard.py
│   ├── data.py
│   ├── env.py
│   └── models.py
├── tests/
│   └── test_env.py
├── app.py
├── inference.py
├── openenv.yaml
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Author

Priyansha Dhaundiyal
