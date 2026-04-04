# env.py
from environment.models import EmailObservation, TriageReward
from environment.data import get_emails_for_task
from environment.tasks.task1_easy import grade_task1, TASK1_CONFIG
from environment.tasks.task2_medium import grade_task2, TASK2_CONFIG
from environment.tasks.task3_hard import grade_task3, TASK3_CONFIG
from environment.tasks.task4_routing import (
    grade_routing,
    TASK4_EASY_CONFIG,
    TASK4_MEDIUM_CONFIG,
    TASK4_HARD_CONFIG,
)
from environment.data_tickets import get_tickets_for_task, get_all_agents

# ── TASK REGISTRY ─────────────────────────────────────────────────────────────

TASK_REGISTRY = {
    "easy"          : {"config": TASK1_CONFIG,        "grader": grade_task1},
    "medium"        : {"config": TASK2_CONFIG,        "grader": grade_task2},
    "hard"          : {"config": TASK3_CONFIG,        "grader": grade_task3},
    "routing_easy"  : {"config": TASK4_EASY_CONFIG,   "grader": grade_routing},
    "routing_medium": {"config": TASK4_MEDIUM_CONFIG, "grader": grade_routing},
    "routing_hard"  : {"config": TASK4_HARD_CONFIG,   "grader": grade_routing},
}

# ── ENVIRONMENT CLASS ─────────────────────────────────────────────────────────

class EmailTriageEnv:

    def __init__(self, task_id: str = "easy"):
        if task_id not in TASK_REGISTRY:
            raise ValueError(
                f"Unknown task '{task_id}'. "
                f"Choose from: {list(TASK_REGISTRY.keys())}"
            )

        self.task_id             = task_id
        self.config              = TASK_REGISTRY[task_id]["config"]
        self.grader              = TASK_REGISTRY[task_id]["grader"]
        self.emails              = []
        self.actions_taken       = []
        self.current_score       = 0.0
        self.steps_taken         = 0
        self.done                = False
        self.consecutive_correct = 0

    # ── RESET ─────────────────────────────────────────────────────────────────

    def reset(self) -> EmailObservation:
        if self.task_id.startswith("routing"):
            self.emails = get_tickets_for_task(self.task_id)
        else:
            self.emails = get_emails_for_task(self.task_id)

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

        # ── Find the ground truth ──────────────────────────────────────────
        if self.task_id.startswith("routing"):
            item_id = action.get("ticket_id")
            ground_truth = next(
                (t for t in self.emails if t["id"] == item_id),
                None
            )
        else:
            item_id = action.get("email_id")
            ground_truth = next(
                (e for e in self.emails if e["id"] == item_id),
                None
            )

        # ── Grade the action ──────────────────────────────────────────────
        if ground_truth is None:
            grade_result = {
                "score"    : 0.0,
                "reason"   : f"Item '{item_id}' not found.",
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
        all_done     = len(self.actions_taken) >= len(self.emails)
        out_of_steps = self.steps_taken >= self.config["max_steps"]

        if all_done or out_of_steps:
            self.done = True

        # ── Bonuses and penalties ─────────────────────────────────────────
        base_score = grade_result["score"]

        # Streak bonus
        streak_bonus = 0.0
        if base_score >= 0.8:
            self.consecutive_correct += 1
            if self.consecutive_correct >= 3:
                streak_bonus = 0.05
        else:
            self.consecutive_correct = 0

        # Confidence penalty (email tasks only)
        confidence_penalty = 0.0
        if ground_truth is not None and not self.task_id.startswith("routing"):
            correct_dup = ground_truth.get("duplicate_of") is not None
            agent_dup   = action.get("is_duplicate", False)
            if agent_dup and not correct_dup:
                confidence_penalty = 0.1

        # Speed bonus
        speed_bonus = 0.0
        if self.done:
            steps_remaining = self.config["max_steps"] - self.steps_taken
            if steps_remaining > 0:
                speed_bonus = round(
                    min(0.05, steps_remaining / self.config["max_steps"] * 0.1),
                    4
                )

        # Final score
        final_score        = base_score + streak_bonus + speed_bonus - confidence_penalty
        self.current_score = round(max(0.0, min(1.0, final_score)), 4)

        # ── Build reward ───────────────────────────────────────────────────
        reward = TriageReward(
            value     = self.current_score,
            reason    = grade_result["reason"],
            breakdown = {
                **grade_result["breakdown"],
                "base_score"        : base_score,
                "streak_bonus"      : streak_bonus,
                "speed_bonus"       : speed_bonus,
                "confidence_penalty": confidence_penalty,
            },
        )

        return {
            "observation": self._get_observation(),
            "reward"     : reward,
            "done"       : self.done,
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