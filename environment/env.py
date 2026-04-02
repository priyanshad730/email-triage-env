# env.py
# This is the main environment class.
# Think of it as the "game engine" — it controls:
#   - what the agent sees (observations)
#   - what happens when the agent acts (step)
#   - how the episode starts fresh (reset)
#   - what the current state looks like (state)

from environment.models import EmailObservation, TriageAction, TriageReward
from environment.data import get_emails_for_task
from environment.tasks.task1_easy import grade_task1, TASK1_CONFIG
from environment.tasks.task2_medium import grade_task2, TASK2_CONFIG
from environment.tasks.task3_hard import grade_task3, TASK3_CONFIG

# ── TASK REGISTRY ─────────────────────────────────────────────────────────────

TASK_REGISTRY = {
    "easy":   {"config": TASK1_CONFIG, "grader": grade_task1},
    "medium": {"config": TASK2_CONFIG, "grader": grade_task2},
    "hard":   {"config": TASK3_CONFIG, "grader": grade_task3},
}

# ── ENVIRONMENT CLASS ─────────────────────────────────────────────────────────

class EmailTriageEnv:
    """
    The main OpenEnv environment for email triage.

    Usage:
        env = EmailTriageEnv(task_id="easy")
        observation = env.reset()
        result = env.step(action)
        current = env.state()
    """

    def __init__(self, task_id: str = "easy"):
        if task_id not in TASK_REGISTRY:
            raise ValueError(
                f"Unknown task '{task_id}'. "
                f"Choose from: {list(TASK_REGISTRY.keys())}"
            )

        self.task_id = task_id
        self.config  = TASK_REGISTRY[task_id]["config"]
        self.grader  = TASK_REGISTRY[task_id]["grader"]

        self.emails              = []
        self.actions_taken       = []
        self.current_score       = 0.0
        self.steps_taken         = 0
        self.done                = False
        self.consecutive_correct = 0    # tracks streak of correct answers

    # ── RESET ─────────────────────────────────────────────────────────────────

    def reset(self) -> EmailObservation:
        """
        Start a fresh episode.
        Clears all previous actions, scores, and streaks.
        Returns the first observation the agent will see.
        """
        self.emails              = get_emails_for_task(self.task_id)
        self.actions_taken       = []
        self.current_score       = 0.0
        self.steps_taken         = 0
        self.done                = False
        self.consecutive_correct = 0

        return EmailObservation(
            task_id       = self.task_id,
            instructions  = self.config["description"],
            emails        = self.emails,
            current_score = self.current_score,
            steps_taken   = self.steps_taken,
            max_steps     = self.config["max_steps"],
            done          = self.done,
        )

    # ── STEP ──────────────────────────────────────────────────────────────────

    def step(self, action: dict) -> dict:
        """
        The agent submits one action (classification of one email).
        We grade it, apply bonuses/penalties, and return what happens next.

        Reward breakdown:
            base score          : from grader (urgency + dept + duplicate)
            streak bonus        : +0.05 if 3+ correct answers in a row
            speed bonus         : +0.05 if episode finishes under max steps
            confidence penalty  : -0.1 if agent wrongly marks as duplicate
        """

        # ── If already done, don't accept more actions ─────────────────────
        if self.done:
            return {
                "observation": self._get_observation(),
                "reward": TriageReward(
                    value=0.0,
                    reason="Episode already finished.",
                    breakdown={}
                ),
                "done": True,
                "info": {"message": "Episode is already complete."}
            }

        # ── Record this action ─────────────────────────────────────────────
        self.actions_taken.append(action)
        self.steps_taken += 1

        # ── Find the ground truth for this email ──────────────────────────
        email_id = action.get("email_id")
        ground_truth = next(
            (e for e in self.emails if e["id"] == email_id),
            None
        )

        # ── Grade the action ──────────────────────────────────────────────
        if ground_truth is None:
            grade_result = {
                "score"    : 0.0,
                "reason"   : f"Email '{email_id}' not found.",
                "breakdown": {}
            }
        else:
            if self.task_id == "easy":
                grade_result = self.grader(action, ground_truth)
            else:
                grade_result = self.grader(
                    self.actions_taken,
                    self.emails[:len(self.actions_taken)]
                )

        # ── Check if episode should end ────────────────────────────────────
        all_emails_done = len(self.actions_taken) >= len(self.emails)
        out_of_steps    = self.steps_taken >= self.config["max_steps"]

        if all_emails_done or out_of_steps:
            self.done = True

        # ── Calculate bonuses and penalties ───────────────────────────────
        base_score = grade_result["score"]

        # 1. Streak bonus — reward 3 correct answers in a row
        streak_bonus = 0.0
        if base_score >= 0.8:
            self.consecutive_correct += 1
            if self.consecutive_correct >= 3:
                streak_bonus = 0.05
        else:
            self.consecutive_correct = 0

        # 2. Confidence penalty — wrong duplicate flag loses extra points
        # Because marking something as duplicate means the team ignores it
        confidence_penalty = 0.0
        if ground_truth is not None:
            correct_dup = ground_truth.get("duplicate_of") is not None
            agent_dup   = action.get("is_duplicate", False)
            if agent_dup and not correct_dup:
                confidence_penalty = 0.1

        # 3. Speed bonus — finishing well under the step limit
        speed_bonus = 0.0
        if self.done:
            steps_remaining = self.config["max_steps"] - self.steps_taken
            if steps_remaining > 0:
                speed_bonus = round(
                    min(0.05, steps_remaining / self.config["max_steps"] * 0.1),
                    4
                )

        # ── Final score — clamped between 0.0 and 1.0 ────────────────────
        final_score = base_score + streak_bonus + speed_bonus - confidence_penalty
        self.current_score = round(max(0.0, min(1.0, final_score)), 4)

        # ── Build reward object ────────────────────────────────────────────
        reward = TriageReward(
            value  = self.current_score,
            reason = grade_result["reason"],
            breakdown = {
                **grade_result["breakdown"],
                "base_score"         : base_score,
                "streak_bonus"       : streak_bonus,
                "speed_bonus"        : speed_bonus,
                "confidence_penalty" : confidence_penalty,
            },
        )

        return {
            "observation": self._get_observation(),
            "reward":      reward,
            "done":        self.done,
            "info": {
                "steps_taken"        : self.steps_taken,
                "emails_triaged"     : len(self.actions_taken),
                "total_emails"       : len(self.emails),
                "consecutive_correct": self.consecutive_correct,
                "streak_bonus"       : streak_bonus,
                "speed_bonus"        : speed_bonus,
                "confidence_penalty" : confidence_penalty,
            }
        }

    # ── STATE ──────────────────────────────────────────────────────────────────

    def state(self) -> dict:
        return {
            "task_id"            : self.task_id,
            "steps_taken"        : self.steps_taken,
            "max_steps"          : self.config["max_steps"],
            "current_score"      : self.current_score,
            "emails_triaged"     : len(self.actions_taken),
            "total_emails"       : len(self.emails),
            "done"               : self.done,
            "consecutive_correct": self.consecutive_correct,
            "actions_taken"      : self.actions_taken,
        }

    # ── PRIVATE HELPER ─────────────────────────────────────────────────────────

    def _get_observation(self) -> EmailObservation:
        return EmailObservation(
            task_id       = self.task_id,
            instructions  = self.config["description"],
            emails        = self.emails,
            current_score = self.current_score,
            steps_taken   = self.steps_taken,
            max_steps     = self.config["max_steps"],
            done          = self.done,
        )
