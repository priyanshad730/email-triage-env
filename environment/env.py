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
# Maps task names to their config and grader function.
# Easy to add new tasks later — just add a line here.

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
        """
        Set up the environment for a specific task.
        task_id must be one of: "easy", "medium", "hard"
        """
        if task_id not in TASK_REGISTRY:
            raise ValueError(
                f"Unknown task '{task_id}'. "
                f"Choose from: {list(TASK_REGISTRY.keys())}"
            )

        self.task_id = task_id
        self.config  = TASK_REGISTRY[task_id]["config"]
        self.grader  = TASK_REGISTRY[task_id]["grader"]

        # These get set properly when reset() is called
        self.emails        = []
        self.actions_taken = []
        self.current_score = 0.0
        self.steps_taken   = 0
        self.done          = False

    # ── RESET ─────────────────────────────────────────────────────────────────

    def reset(self) -> EmailObservation:
        """
        Start a fresh episode.
        Clears all previous actions and scores.
        Returns the first observation the agent will see.
        """
        self.emails        = get_emails_for_task(self.task_id)
        self.actions_taken = []
        self.current_score = 0.0
        self.steps_taken   = 0
        self.done          = False

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
        We grade it, update the score, and return what happens next.

        Returns a dict with:
            observation : what the agent sees now
            reward      : the score for this action
            done        : whether the episode is finished
            info        : extra debugging info
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
            # Agent referred to an email that doesn't exist
            grade_result = {
                "score": 0.0,
                "reason": f"Email '{email_id}' not found.",
                "breakdown": {}
            }
        else:
            if self.task_id == "easy":
                grade_result = self.grader(action, ground_truth)
            else:
                # For medium and hard, grade all actions so far
                grade_result = self.grader(
                    self.actions_taken,
                    self.emails[:len(self.actions_taken)]
                )

        # ── Update running score ───────────────────────────────────────────
        self.current_score = grade_result["score"]

        # ── Check if episode should end ────────────────────────────────────
        all_emails_done = len(self.actions_taken) >= len(self.emails)
        out_of_steps    = self.steps_taken >= self.config["max_steps"]

        if all_emails_done or out_of_steps:
            self.done = True

        # ── Build reward object ────────────────────────────────────────────
        reward = TriageReward(
            value     = grade_result["score"],
            reason    = grade_result["reason"],
            breakdown = grade_result["breakdown"],
        )

        return {
            "observation": self._get_observation(),
            "reward":      reward,
            "done":        self.done,
            "info": {
                "steps_taken":   self.steps_taken,
                "emails_triaged": len(self.actions_taken),
                "total_emails":  len(self.emails),
            }
        }

    # ── STATE ──────────────────────────────────────────────────────────────────

    def state(self) -> dict:
        """
        Returns the full current state of the environment.
        Useful for debugging — shows everything happening inside.
        """
        return {
            "task_id":        self.task_id,
            "steps_taken":    self.steps_taken,
            "max_steps":      self.config["max_steps"],
            "current_score":  self.current_score,
            "emails_triaged": len(self.actions_taken),
            "total_emails":   len(self.emails),
            "done":           self.done,
            "actions_taken":  self.actions_taken,
        }

    # ── PRIVATE HELPER ─────────────────────────────────────────────────────────

    def _get_observation(self) -> EmailObservation:
        """Build the current observation object."""
        return EmailObservation(
            task_id       = self.task_id,
            instructions  = self.config["description"],
            emails        = self.emails,
            current_score = self.current_score,
            steps_taken   = self.steps_taken,
            max_steps     = self.config["max_steps"],
            done          = self.done,
        )
