from env.tasks import TASKS
from env.grader import grade


class AIValidationEnv:

    def __init__(self):
        self.current_index = 0
        self.current_task = None

    def reset(self):
        self.current_index = 0
        self.current_task = TASKS[self.current_index]

        return {
            "observation": {
                "decision_text": self.current_task["decision_text"],
                "context": self.current_task["context"]
            },
            "reward": 0.0,
            "done": False,
            "info": {}
        }

    def step(self, action):
        # ✅ Correct grading (only score returned)
        score = grade(action, self.current_task["ground_truth"])
        info = {}

        # Move to next task
        self.current_index += 1
        done = self.current_index >= len(TASKS)

        if not done:
            self.current_task = TASKS[self.current_index]
            observation = {
                "decision_text": self.current_task["decision_text"],
                "context": self.current_task["context"]
            }
        else:
            observation = {}

        return {
            "observation": observation,
            "reward": score,
            "done": done,
            "info": info
        }

    def state(self):
        return {
            "current_index": self.current_index,
            "total_tasks": len(TASKS)
        }