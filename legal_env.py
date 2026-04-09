import asyncio
from typing import List, Optional, Dict, Any
from pydantic import Field
from openenv_core.env_server.interfaces import Environment
from openenv_core.env_server.types import Action, Observation, State

from tasks import TASKS, LegalTask

class LegalObservation(Observation):
    clause: str = Field(..., description="The legal clause to process.")
    history: List[str] = Field(default_factory=list, description="History of attempts and feedback.")
    task_name: str = Field(..., description="The name of the current task.")

class LegalAction(Action):
    simplified_text: str = Field(..., description="The simplified version of the clause.")
    risk: str = Field(..., description="Classification: SAFE or NOT SAFE.")
    key_points: List[str] = Field(..., description="Extracted key points.")

class LegalState(State):
    task_index: int = Field(..., description="Index of the current task.")
    current_task_name: str = Field(..., description="Name of the current task.")

class LegalRedLineEnv(Environment[LegalAction, LegalObservation, LegalState]):
    def __init__(self, task_index: int = 0):
        super().__init__()
        self.task_index = task_index % len(TASKS)
        self.current_task: LegalTask = TASKS[self.task_index]
        self.steps_taken = 0
        self.max_steps = 3
        self.history = []
        self._done = False

    def reset(self, **kwargs) -> LegalObservation:
        self.steps_taken = 0
        self.history = []
        self._done = False
        return LegalObservation(
            clause=self.current_task.clause,
            history=self.history,
            task_name=self.current_task.name,
            done=False,
            reward=0.01
        )

    def step(self, action: LegalAction, **kwargs) -> LegalObservation:
        self.steps_taken += 1
        
        # Grading logic
        score, feedback = self._grade(action)
        
        # Multi-step logic: if score is >= 0.99 or max steps reached, we are done
        if score >= 0.99 or self.steps_taken >= self.max_steps:
            self._done = True
        
        self.history.append(f"Step {self.steps_taken}: Score {score:.2f} - {feedback}")
        
        return LegalObservation(
            clause=self.current_task.clause,
            history=self.history,
            task_name=self.current_task.name,
            done=self._done,
            reward=score,
            metadata={"feedback": feedback}
        )

    def state(self) -> LegalState:
        return LegalState(
            episode_id="unknown",
            step_count=self.steps_taken,
            task_index=self.task_index,
            current_task_name=self.current_task.name
        )

    def _grade(self, action: LegalAction) -> tuple[float, str]:
        score = 0.0
        feedback_parts = []
        
        # 1. Format Check (0.1)
        score += 0.1
        
        # 2. Risk Detection (0.3)
        if action.risk.upper() == self.current_task.risk.upper():
            score += 0.3
            feedback_parts.append("Correct risk detection.")
        else:
            feedback_parts.append(f"Incorrect risk detection. Expected {self.current_task.risk}.")
            
        # 3. Key Points (0.3)
        found_points = 0
        total_mandatory = len(self.current_task.key_points_keywords)
        for kw in self.current_task.key_points_keywords:
            if any(kw.lower() in p.lower() for p in action.key_points):
                found_points += 1
        
        point_score = (found_points / total_mandatory) * 0.3
        score += point_score
        if found_points == total_mandatory:
            feedback_parts.append("All key points captured.")
        else:
            feedback_parts.append(f"Captured {found_points}/{total_mandatory} key points.")
            
        # 4. Simplified Text (0.3)
        found_keywords = 0
        total_simple_kw = len(self.current_task.simplified_text_keywords)
        for kw in self.current_task.simplified_text_keywords:
            if kw.lower() in action.simplified_text.lower():
                found_keywords += 1
        
        simple_score = (found_keywords / total_simple_kw) * 0.3
        score += simple_score
        if found_keywords == total_simple_kw:
            feedback_parts.append("Simplified text is accurate and complete.")
        else:
            feedback_parts.append(f"Simplified text missing some details ({found_keywords}/{total_simple_kw} keywords found).")

        # Ensure score is strictly between 0 and 1 (strictly avoiding 0.0 and 1.0)
        return max(0.01, min(0.99, score)), "; ".join(feedback_parts)

    def close(self):
        pass
